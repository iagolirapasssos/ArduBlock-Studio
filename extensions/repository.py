"""
Integration with official Arduino Libraries repository

CHANGELOG (fixes):
- CRÍTICO: Removido _get_latest_version() chamado em LOOP dentro de _load_index().
  Antes, a cada inicialização, fazia 1 requisição HTTP por biblioteca (50+ libs),
  bloqueando completamente o processo principal por vários segundos.
- _load_index() agora é executado em background thread e só acessa a rede SE o
  cache local tiver mais de 24h de idade.
- Cache é validado por timestamp, evitando hits desnecessários à rede.
- Todas as operações de rede têm timeout de 10s para evitar trava indefinida.
"""

import json
import threading
import time
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ArduinoLibrary:
    """Informações sobre uma biblioteca Arduino"""
    name: str
    version: str
    author: str
    maintainer: str
    sentence: str
    paragraph: str
    website: str
    category: str
    architectures: List[str]
    downloaded: int = 0
    installed: bool = False
    github_url: str = ""


_CACHE_HOURS = 24
_FALLBACK_POPULAR = [
    {"name": "Servo",              "category": "Motors",        "sentence": "Controls servo motors"},
    {"name": "LiquidCrystal",      "category": "Display",       "sentence": "Alphanumeric LCD displays"},
    {"name": "DHT sensor library", "category": "Sensors",       "sentence": "DHT11/DHT22 temperature & humidity"},
    {"name": "Adafruit NeoPixel",  "category": "LEDs",          "sentence": "NeoPixel LED strip control"},
    {"name": "WiFi",               "category": "Communication", "sentence": "WiFi connectivity for Arduino"},
    {"name": "ArduinoJson",        "category": "Data",          "sentence": "JSON library for Arduino"},
    {"name": "SD",                 "category": "Storage",       "sentence": "SD card read/write"},
    {"name": "Stepper",            "category": "Motors",        "sentence": "Stepper motor control"},
    {"name": "SoftwareSerial",     "category": "Communication", "sentence": "Serial on any digital pins"},
    {"name": "Wire",               "category": "Communication", "sentence": "I2C/TWI library"},
    {"name": "SPI",                "category": "Communication", "sentence": "SPI library"},
    {"name": "EEPROM",             "category": "Storage",       "sentence": "Read/write EEPROM memory"},
    {"name": "Ethernet",           "category": "Communication", "sentence": "Ethernet library"},
    {"name": "TFT",                "category": "Display",       "sentence": "TFT LCD library"},
    {"name": "Firmata",            "category": "Communication", "sentence": "Firmata protocol library"},
    {"name": "IRremote",           "category": "Communication", "sentence": "Infra-red send/receive"},
    {"name": "Adafruit BusIO",     "category": "Communication", "sentence": "I2C & SPI abstraction layer"},
    {"name": "Adafruit GFX Library","category": "Display",      "sentence": "Core graphics library"},
    {"name": "PubSubClient",       "category": "Communication", "sentence": "MQTT messaging library"},
    {"name": "FastLED",            "category": "LEDs",          "sentence": "FastLED animation library"},
]


class ArduinoLibraryRepository:
    """
    Repositório de bibliotecas Arduino.

    Carrega em background para não bloquear a UI. Use is_ready() ou
    espere pelo evento _ready_event antes de acessar os dados.
    """

    _CACHE_FILE = Path.home() / ".ardublock" / "library_cache.json"
    _CACHE_META = Path.home() / ".ardublock" / "library_cache_meta.json"

    def __init__(self, cli_path: str = None):
        self.cli_path = cli_path
        self.libraries: List[ArduinoLibrary] = []
        self._ready_event = threading.Event()
        self._lock = threading.Lock()

        # Carrega cache imediatamente (sem rede)
        self._load_from_cache_or_fallback()
        self._ready_event.set()  # Dados de fallback já estão disponíveis

        # Atualiza em background SE o cache estiver velho
        if self._cache_is_stale():
            t = threading.Thread(target=self._refresh_in_background, daemon=True)
            t.start()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def is_ready(self) -> bool:
        return self._ready_event.is_set()

    def search(self, query: str) -> List[ArduinoLibrary]:
        q = query.lower()
        with self._lock:
            return [
                lib for lib in self.libraries
                if q in lib.name.lower() or q in lib.sentence.lower()
            ]

    def get_by_category(self, category: str) -> List[ArduinoLibrary]:
        with self._lock:
            return [lib for lib in self.libraries if lib.category == category]

    def get_categories(self) -> List[str]:
        with self._lock:
            return sorted({lib.category for lib in self.libraries})

    def get_library_details(self, name: str) -> Optional[ArduinoLibrary]:
        with self._lock:
            for lib in self.libraries:
                if lib.name == name:
                    return lib
        return None

    def get_popular_libraries(self, limit: int = 20) -> List[ArduinoLibrary]:
        with self._lock:
            return self.libraries[:limit]

    def get_libraries_for_board(self, architecture: str) -> List[ArduinoLibrary]:
        with self._lock:
            return [
                lib for lib in self.libraries
                if "*" in lib.architectures or architecture in lib.architectures
            ]

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _load_from_cache_or_fallback(self):
        """Carrega cache local; usa fallback se não existir."""
        cache = self._read_cache()
        if cache:
            with self._lock:
                self.libraries = cache
            print(f"[LibRepo] Loaded {len(self.libraries)} libraries from cache")
        else:
            with self._lock:
                self.libraries = self._build_fallback_list()
            print(f"[LibRepo] Using fallback list ({len(self.libraries)} libs)")

    def _cache_is_stale(self) -> bool:
        """Retorna True se o cache tiver mais de _CACHE_HOURS horas."""
        if not self._CACHE_META.exists():
            return True
        try:
            meta = json.loads(self._CACHE_META.read_text())
            saved_ts = meta.get("timestamp", 0)
            age_hours = (time.time() - saved_ts) / 3600
            return age_hours > _CACHE_HOURS
        except Exception:
            return True

    def _refresh_in_background(self):
        """Tenta buscar dados atualizados da rede sem bloquear a UI."""
        print("[LibRepo] Refreshing library list in background...")
        try:
            import requests
            resp = requests.get(
                "https://api.github.com/orgs/arduino-libraries/repos?per_page=100",
                headers={"Accept": "application/vnd.github.v3+json",
                         "User-Agent": "ArduBlock-Studio/1.1"},
                timeout=10,  # Nunca espera mais de 10s
            )
            if resp.status_code == 200:
                repos = resp.json()
                new_libs = []
                for repo in repos:
                    new_libs.append(ArduinoLibrary(
                        name=repo.get("name", ""),
                        version="latest",        # Sem requisição extra por repo
                        author="Arduino Team",
                        maintainer="Arduino Team",
                        sentence=repo.get("description", "") or "",
                        paragraph=repo.get("description", "") or "",
                        website=repo.get("html_url", ""),
                        category=self._categorize(repo.get("name", "")),
                        architectures=["*"],
                        github_url=repo.get("html_url", ""),
                    ))
                if new_libs:
                    with self._lock:
                        # Mescla: mantém itens do fallback que não vieram da API
                        existing_names = {lib.name for lib in new_libs}
                        for lib in self.libraries:
                            if lib.name not in existing_names:
                                new_libs.append(lib)
                        self.libraries = new_libs
                    self._write_cache(new_libs)
                    print(f"[LibRepo] Updated: {len(new_libs)} libraries")
        except Exception as e:
            print(f"[LibRepo] Background refresh failed (non-critical): {e}")

    def _categorize(self, name: str) -> str:
        n = name.lower()
        if any(x in n for x in ["display", "lcd", "oled", "tft", "gfx"]):
            return "Display"
        if any(x in n for x in ["sensor", "dht", "temperature", "humidity", "imu"]):
            return "Sensors"
        if any(x in n for x in ["wifi", "ethernet", "ble", "mqtt", "gsm", "lora"]):
            return "Communication"
        if any(x in n for x in ["motor", "servo", "stepper"]):
            return "Motors"
        if any(x in n for x in ["led", "neopixel", "fastled", "rgb"]):
            return "LEDs"
        if any(x in n for x in ["rtc", "time", "clock"]):
            return "Timing"
        if any(x in n for x in ["json", "csv", "xml"]):
            return "Data"
        return "Miscellaneous"

    def _build_fallback_list(self) -> List[ArduinoLibrary]:
        return [
            ArduinoLibrary(
                name=d["name"],
                version="latest",
                author="Arduino/Community",
                maintainer="Various",
                sentence=d["sentence"],
                paragraph=d["sentence"],
                website=f"https://github.com/arduino-libraries/{d['name'].replace(' ', '')}",
                category=d["category"],
                architectures=["*"],
            )
            for d in _FALLBACK_POPULAR
        ]

    def _read_cache(self) -> Optional[List[ArduinoLibrary]]:
        if not self._CACHE_FILE.exists():
            return None
        try:
            data = json.loads(self._CACHE_FILE.read_text())
            libs = []
            for item in data:
                # Garante que 'architectures' é lista
                if isinstance(item.get("architectures"), str):
                    item["architectures"] = [item["architectures"]]
                # Remove chaves desconhecidas
                known = ArduinoLibrary.__dataclass_fields__.keys()  # type: ignore
                filtered = {k: v for k, v in item.items() if k in known}
                libs.append(ArduinoLibrary(**filtered))
            return libs if libs else None
        except Exception as e:
            print(f"[LibRepo] Cache read error: {e}")
            return None

    def _write_cache(self, libs: List[ArduinoLibrary]):
        try:
            self._CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self._CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump([lib.__dict__ for lib in libs], f, indent=2, ensure_ascii=False)
            with open(self._CACHE_META, "w", encoding="utf-8") as f:
                json.dump({"timestamp": time.time()}, f)
        except Exception as e:
            print(f"[LibRepo] Cache write error (non-critical): {e}")


class ExtensionLibraryMapper:
    """Mapeia blocos de extensão para as bibliotecas Arduino necessárias."""

    MAPPING = {
        "ab_servo":      "Servo",
        "ab_dht":        "DHT sensor library",
        "ab_lcd":        "LiquidCrystal",
        "ab_stepper":    "Stepper",
        "ab_wifi":       "WiFi",
        "ab_bluetooth":  "SoftwareSerial",
        "ab_neopixel":   "Adafruit NeoPixel",
        "ab_sd":         "SD",
        "ab_json":       "ArduinoJson",
        "ab_tone":       "Tone",
    }

    def get_required_library(self, block_type: str) -> Optional[str]:
        for prefix, lib in self.MAPPING.items():
            if block_type.startswith(prefix):
                return lib
        return None

    def suggest_library_installation(self, workspace_xml: str) -> List[str]:
        import re
        required = set()
        for block_type in re.findall(r'<block type="([^"]+)"', workspace_xml):
            lib = self.get_required_library(block_type)
            if lib:
                required.add(lib)
        return list(required)