"""Incremental compilation cache to prevent system freezing."""
import hashlib
import json
import threading
import queue
import time
from pathlib import Path
from typing import Tuple, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import subprocess


@dataclass
class CompilationJob:
    """Represents a compilation job in the queue."""
    id: str
    code: str
    fqbn: str
    timestamp: datetime = field(default_factory=datetime.now)
    callback = None
    priority: int = 0


class CompilationCache:
    """Manages compilation cache with background processing."""
    
    def __init__(self, cache_dir: Path = None):
        if cache_dir is None:
            cache_dir = Path.home() / ".ardublock" / "compilation_cache"
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata = self._load_metadata()
        
        # Background compilation queue
        self.job_queue = queue.Queue()
        self.worker_thread = None
        self.is_running = True
        self._start_worker()
        
        # Cache cleanup thread
        self._start_cleanup_thread()
    
    def _load_metadata(self) -> Dict:
        """Load cache metadata from disk."""
        if self.metadata_file.exists():
            try:
                data = json.loads(self.metadata_file.read_text())
                # Convert string timestamps back to datetime
                for key, value in data.items():
                    if 'timestamp' in value:
                        value['timestamp'] = datetime.fromisoformat(value['timestamp'])
                return data
            except (json.JSONDecodeError, ValueError):
                pass
        return {}
    
    def _save_metadata(self):
        """Save cache metadata to disk."""
        # Convert datetime to string for JSON serialization
        data = {}
        for key, value in self.metadata.items():
            data[key] = value.copy()
            if 'timestamp' in data[key]:
                data[key]['timestamp'] = data[key]['timestamp'].isoformat()
        
        self.metadata_file.write_text(json.dumps(data, indent=2))
    
    def _get_code_hash(self, code: str, fqbn: str) -> str:
        """Generate unique hash for code + board combination."""
        content = f"{code}\n{fqbn}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get_cached_result(self, code: str, fqbn: str) -> Optional[Dict]:
        """Get cached compilation result if available and valid."""
        cache_key = self._get_code_hash(code, fqbn)
        
        if cache_key in self.metadata:
            cache_entry = self.metadata[cache_key]
            
            # Check if cache is still valid (24 hours default)
            age = (datetime.now() - cache_entry['timestamp']).total_seconds()
            if age < 86400:  # 24 hours
                # Verify hex file still exists
                hex_path = self.cache_dir / f"{cache_key}.hex"
                if hex_path.exists():
                    return {
                        'success': True,
                        'hex_path': str(hex_path),
                        'cached': True,
                        'age_hours': age / 3600
                    }
        
        return None
    
    def store_cached_result(self, code: str, fqbn: str, hex_path: Path):
        """Store compilation result in cache."""
        cache_key = self._get_code_hash(code, fqbn)
        
        # Copy hex file to cache
        cached_hex = self.cache_dir / f"{cache_key}.hex"
        if hex_path != cached_hex:
            import shutil
            shutil.copy2(hex_path, cached_hex)
        
        self.metadata[cache_key] = {
            'fqbn': fqbn,
            'timestamp': datetime.now(),
            'hex_size': cached_hex.stat().st_size,
            'code_hash': hashlib.md5(code.encode()).hexdigest()[:8]
        }
        
        self._save_metadata()
        
        # Clean old caches if too many
        self._cleanup_old_caches()
    
    def _cleanup_old_caches(self, max_entries: int = 50):
        """Remove oldest cache entries if exceeding limit."""
        if len(self.metadata) > max_entries:
            # Sort by timestamp and remove oldest
            sorted_entries = sorted(
                self.metadata.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            to_remove = sorted_entries[:-max_entries]
            for key, _ in to_remove:
                # Delete hex file
                hex_path = self.cache_dir / f"{key}.hex"
                if hex_path.exists():
                    hex_path.unlink()
                # Remove from metadata
                del self.metadata[key]
            
            self._save_metadata()
    
    def _start_worker(self):
        """Start background worker thread for compilation."""
        def worker():
            while self.is_running:
                try:
                    # Wait for job with timeout to check is_running
                    job = self.job_queue.get(timeout=1)
                    self._process_compilation_job(job)
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Compilation worker error: {e}")
        
        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()
    
    def _start_cleanup_thread(self):
        """Start periodic cleanup thread."""
        def cleanup_worker():
            while self.is_running:
                time.sleep(3600)  # Run every hour
                self._cleanup_old_caches()
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _process_compilation_job(self, job: CompilationJob):
        """Process a compilation job in background."""
        # First check cache
        cached = self.get_cached_result(job.code, job.fqbn)
        if cached:
            if job.callback:
                # Use callback to notify completion
                # This would be connected to JavaScript
                pass
            return
        
        # Perform actual compilation in background with low priority
        try:
            # Lower process priority to avoid freezing UI
            import psutil
            import os
            
            current_process = psutil.Process(os.getpid())
            current_process.nice(10)  # Lower priority on Unix
            # On Windows, use belownormal priority class
            
            # Run compilation
            # This would integrate with your existing ArduinoCLI
            # But we run it with timeout and low priority
            pass
            
        except Exception as e:
            print(f"Background compilation error: {e}")
    
    def queue_compilation(self, code: str, fqbn: str, callback=None, priority: int = 0):
        """Queue a compilation job for background processing."""
        job_id = self._get_code_hash(code, fqbn)
        job = CompilationJob(
            id=job_id,
            code=code,
            fqbn=fqbn,
            callback=callback,
            priority=priority
        )
        self.job_queue.put(job)
        return job_id
    
    def shutdown(self):
        """Shutdown the cache system."""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)


# Global cache instance
_global_cache = None

def get_compilation_cache() -> CompilationCache:
    """Get or create global compilation cache."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CompilationCache()
    return _global_cache