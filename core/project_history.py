"""Local project version history management."""
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import shutil


@dataclass
class ProjectVersion:
    """Represents a saved version of a project."""
    id: str
    timestamp: str
    name: str
    description: str
    xml_data: str
    code_preview: str
    block_count: int
    hash: str
    parent_id: Optional[str] = None


class ProjectHistory:
    """Manage local version history for projects."""
    
    def __init__(self, project_path: Path = None):
        if project_path is None:
            project_path = Path.home() / ".ardublock" / "projects"
        self.history_dir = project_path / ".history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.history_dir / "index.json"
        self.versions: Dict[str, ProjectVersion] = {}
        self.current_version_id = None
        self.project_name = "untitled"
        
        self._load_index()
    
    def _load_index(self):
        """Load version index from disk."""
        if self.index_file.exists():
            try:
                data = json.loads(self.index_file.read_text())
                self.versions = {}
                for vid, vdata in data.get('versions', {}).items():
                    self.versions[vid] = ProjectVersion(**vdata)
                self.current_version_id = data.get('current_version')
                self.project_name = data.get('project_name', 'untitled')
            except (json.JSONDecodeError, TypeError):
                pass
    
    def _save_index(self):
        """Save version index to disk."""
        data = {
            'project_name': self.project_name,
            'current_version': self.current_version_id,
            'versions': {
                vid: asdict(version) 
                for vid, version in self.versions.items()
            },
            'updated_at': datetime.now().isoformat()
        }
        self.index_file.write_text(json.dumps(data, indent=2, default=str))
    
    def _compute_hash(self, xml_data: str) -> str:
        """Compute hash of XML data for change detection."""
        return hashlib.sha256(xml_data.encode()).hexdigest()[:12]
    
    def _get_block_count(self, xml_data: str) -> int:
        """Count blocks in XML data."""
        # Simple count of block tags
        return xml_data.count('<block ')
    
    def _get_code_preview(self, xml_data: str, max_lines: int = 10) -> str:
        """Generate a preview of the Arduino code."""
        # This would call the code generator
        # For now, return a placeholder
        return f"Generated Arduino code with {self._get_block_count(xml_data)} blocks"
    
    def save_version(self, xml_data: str, description: str = "", 
                     auto_save: bool = False) -> ProjectVersion:
        """Save a new version of the project."""
        
        # Check if anything changed
        new_hash = self._compute_hash(xml_data)
        
        if self.current_version_id:
            current = self.versions.get(self.current_version_id)
            if current and current.hash == new_hash:
                # No changes
                return current
        
        # Create new version
        version_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        
        # Add auto-save prefix if needed
        if auto_save:
            description = f"[Auto-save] {description}" if description else "[Auto-save]"
        
        version = ProjectVersion(
            id=version_id,
            timestamp=datetime.now().isoformat(),
            name=f"{self.project_name}_{version_id}",
            description=description or f"Version from {datetime.now().strftime('%H:%M:%S')}",
            xml_data=xml_data,
            code_preview=self._get_code_preview(xml_data),
            block_count=self._get_block_count(xml_data),
            hash=new_hash,
            parent_id=self.current_version_id
        )
        
        # Save XML to separate file
        version_file = self.history_dir / f"{version_id}.xml"
        version_file.write_text(xml_data, encoding='utf-8')
        
        # Store in index
        self.versions[version_id] = version
        self.current_version_id = version_id
        self._save_index()
        
        # Auto-cleanup old versions (keep last 50)
        self._cleanup_old_versions(keep_count=50)
        
        return version
    
    def auto_save(self, xml_data: str) -> ProjectVersion:
        """Auto-save current state (called periodically)."""
        return self.save_version(xml_data, auto_save=True)
    
    def get_version(self, version_id: str) -> Optional[ProjectVersion]:
        """Retrieve a specific version."""
        version = self.versions.get(version_id)
        if version:
            # Load XML data from file if not in memory
            version_file = self.history_dir / f"{version_id}.xml"
            if version_file.exists() and not version.xml_data:
                version.xml_data = version_file.read_text(encoding='utf-8')
        return version
    
    def get_version_xml(self, version_id: str) -> str:
        """Get XML data for a version."""
        version = self.get_version(version_id)
        return version.xml_data if version else ""
    
    def get_version_list(self, limit: int = 30) -> List[Dict]:
        """Get list of versions for display."""
        versions = sorted(
            self.versions.values(),
            key=lambda v: v.timestamp,
            reverse=True
        )[:limit]
        
        return [
            {
                'id': v.id,
                'timestamp': v.timestamp,
                'description': v.description,
                'block_count': v.block_count,
                'is_current': v.id == self.current_version_id
            }
            for v in versions
        ]
    
    def restore_version(self, version_id: str) -> str:
        """Restore a previous version and make it current."""
        version = self.get_version(version_id)
        if version:
            self.current_version_id = version_id
            self._save_index()
            return version.xml_data
        return ""
    
    def diff_versions(self, old_id: str, new_id: str) -> Dict:
        """Show difference between two versions."""
        old_xml = self.get_version_xml(old_id)
        new_xml = self.get_version_xml(new_id)
        
        # Simple diff - count block differences
        old_blocks = set(re.findall(r'<block type="([^"]+)"', old_xml))
        new_blocks = set(re.findall(r'<block type="([^"]+)"', new_xml))
        
        return {
            'added_blocks': list(new_blocks - old_blocks),
            'removed_blocks': list(old_blocks - new_blocks),
            'old_block_count': old_xml.count('<block '),
            'new_block_count': new_xml.count('<block ')
        }
    
    def delete_version(self, version_id: str) -> bool:
        """Delete a version (cannot delete current version)."""
        if version_id == self.current_version_id:
            return False
        
        if version_id in self.versions:
            # Delete XML file
            version_file = self.history_dir / f"{version_id}.xml"
            if version_file.exists():
                version_file.unlink()
            
            del self.versions[version_id]
            self._save_index()
            return True
        
        return False
    
    def _cleanup_old_versions(self, keep_count: int = 50):
        """Remove old versions keeping only recent ones."""
        if len(self.versions) <= keep_count:
            return
        
        sorted_versions = sorted(
            self.versions.values(),
            key=lambda v: v.timestamp,
            reverse=True
        )
        
        # Keep auto-save versions even if old (optional)
        to_delete = sorted_versions[keep_count:]
        
        for version in to_delete:
            if version.id != self.current_version_id:
                self.delete_version(version.id)
    
    def export_version(self, version_id: str, export_path: Path) -> bool:
        """Export a version to an external file."""
        version = self.get_version(version_id)
        if version:
            export_path.write_text(version.xml_data, encoding='utf-8')
            return True
        return False
    
    def set_project_name(self, name: str):
        """Set the project name."""
        self.project_name = name
        self._save_index()
    
    def get_timeline_html(self) -> str:
        """Generate HTML timeline for display."""
        versions = self.get_version_list(limit=20)
        
        html = '''
        <div class="history-timeline">
            <div class="timeline-header">
                <span class="material-icons">history</span> Version History
            </div>
            <div class="timeline-list">
        '''
        
        for v in versions:
            date = datetime.fromisoformat(v['timestamp'])
            html += f'''
                <div class="timeline-item" data-version="{v['id']}">
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <div class="timeline-time">{date.strftime('%H:%M:%S')}</div>
                        <div class="timeline-date">{date.strftime('%b %d, %Y')}</div>
                        <div class="timeline-desc">{v['description']}</div>
                        <div class="timeline-stats">
                            🧩 {v['block_count']} blocks
                            {' ✓ Current' if v['is_current'] else ''}
                        </div>
                    </div>
                </div>
            '''
        
        html += '''
            </div>
        </div>
        '''
        
        return html