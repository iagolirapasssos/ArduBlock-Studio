"""
ArduBlock Studio Extension API
================================
API simples e poderosa para criar extensões.

CHANGELOG (fixes):
- Batch de injeções JS: todos os injects são bufferizados e executados em uma
  única chamada ao final (via flush()), eliminando dezenas de eval() por extensão.
- Corrigido: add_generator() criava 'var ArduinoGen' LOCAL dentro do IIFE,
  sombreando a variável global → geradores nunca funcionavam.
- Corrigido: inp_check era passado como a string 'null' para .setCheck(),
  impedindo conexões entre blocos. Agora passa null JS real.
- Adicionado setInputsInline(true) para blocos simples (≤3 inputs), tornando-os
  visualmente idênticos aos blocos nativos da IDE.
- add_translations() agora gera UMA única chamada JS em vez de uma por chave.
- add_category() não chama mais updateToolbox() individualmente.
- Adicionado flush_all() chamado pelo manager após carregar a extensão.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class ExtensionAPI:
    """API principal para criação de extensões"""

    def __init__(self, workspace=None, bridge=None):
        self.workspace = workspace
        self.bridge = bridge
        self._extension_id = None
        self._ext_path = None
        # Buffer único – todas as injeções ficam aqui até flush()
        self._js_buffer: List[str] = []
        # Armazena traduções acumuladas para flush em lote
        self._pending_translations: Dict[str, Dict[str, str]] = {}

    def initialize(self, workspace, extension_id: str, ext_path: Path):
        """Inicializa a API (chamado automaticamente pelo sistema)"""
        self.workspace = workspace
        self._extension_id = extension_id
        self._ext_path = ext_path

    # ============================================================
    # INJEÇÃO DE JAVASCRIPT – usa buffer para reduzir eval() calls
    # ============================================================

    def inject_js(self, js_code: str):
        """Bufferiza código JavaScript para injeção em lote."""
        self._js_buffer.append(js_code.strip())

    def inject_file(self, file_path: Path):
        """Bufferiza o conteúdo de um arquivo JavaScript."""
        if file_path.exists():
            self.inject_js(file_path.read_text(encoding="utf-8"))

    def inject_css(self, css_code: str):
        """Injeta CSS via JavaScript."""
        # CSS escaping: backticks inside css_code
        escaped = css_code.replace("`", "\\`")
        self.inject_js(f"""
(function() {{
    var s = document.createElement('style');
    s.textContent = `{escaped}`;
    document.head.appendChild(s);
}})();""")

    def inject_css_file(self, file_path: Path):
        """Injeta CSS de um arquivo."""
        if file_path.exists():
            self.inject_css(file_path.read_text(encoding="utf-8"))

    def flush(self):
        """
        Executa todos os JavaScripts pendentes de uma só vez.
        """
        if not self._js_buffer and not self._pending_translations:
            return

        if self._pending_translations:
            self._flush_translations_to_buffer()

        if self._js_buffer:
            combined = "\n;\n".join(self._js_buffer)
            
            # CORREÇÃO: Usar o bridge para injetar JavaScript
            if self.bridge and hasattr(self.bridge, 'injectJavaScript'):
                self.bridge.injectJavaScript(combined)
            elif self.workspace and hasattr(self.workspace, 'runJavaScript'):
                self.workspace.runJavaScript(combined)
            else:
                print("[API] ERROR: No way to inject JavaScript!")

        self._js_buffer.clear()
        self._pending_translations.clear()

    def _flush_translations_to_buffer(self):
        """Converte traduções acumuladas em uma única injeção JS."""
        if not self._pending_translations:
            return
        entries = []
        for lang, trans in self._pending_translations.items():
            for key, text in trans.items():
                escaped = text.replace("\\", "\\\\").replace('"', '\\"')
                entries.append(f'Blockly.Msg["{key}_{lang}"] = "{escaped}";')
        if entries:
            js = "(function() {\n  if (typeof Blockly !== 'undefined') {\n    "
            js += "\n    ".join(entries)
            js += "\n  }\n})();"
            self._js_buffer.append(js)
        self._pending_translations.clear()

    # ============================================================
    # MANIPULAÇÃO DA TOOLBOX
    # ============================================================

    def add_category(self, parent: str, name: str, colour: str = "#666666", icon: str = ""):
        """
        Adiciona uma subcategoria à toolbox.
        Não chama updateToolbox() aqui – é feito UMA VEZ no final pelo manager.
        """
        icon_line = f"nc.setAttribute('icon', '{icon}');" if icon else ""
        self.inject_js(f"""
(function() {{
    var toolbox = document.getElementById('toolbox');
    if (!toolbox) return;
    var parentCat = null;
    var cats = toolbox.querySelectorAll('category');
    for (var i = 0; i < cats.length; i++) {{
        if (cats[i].getAttribute('name') === '{parent}') {{ parentCat = cats[i]; break; }}
    }}
    if (!parentCat) {{
        parentCat = document.createElement('category');
        parentCat.setAttribute('name', '{parent}');
        parentCat.setAttribute('colour', '{colour}');
        toolbox.appendChild(parentCat);
    }}
    if (!parentCat.querySelector('category[name="{name}"]')) {{
        var nc = document.createElement('category');
        nc.setAttribute('name', '{name}');
        nc.setAttribute('colour', '{colour}');
        {icon_line}
        parentCat.appendChild(nc);
    }}
}})();""")

    def add_block(self, name: str, block_type: str, category: str, colour: str,
                  inputs: List[Dict] = None, tooltip: Dict = None,
                  subcategory: str = None, inline: bool = None):
        """
        Adiciona um novo bloco e o registra na toolbox.

        Parâmetros:
            inline: None = decide automaticamente (True se ≤3 inputs),
                    True/False = força o modo.

        FIXES:
            - .setCheck() usa null JS quando check não especificado.
            - setInputsInline(true) ativado para blocos simples.
            - updateToolbox() NÃO é chamado aqui – feito em lote pelo manager.
        """
        inputs = inputs or []
        inputs_js = ""

        for inp in inputs:
            inp_type = inp.get("type", "dummy")
            inp_name = inp.get("name", "")
            inp_label = inp.get("label", "").replace("'", "\\'")
            raw_check = inp.get("check")          # None se não especificado
            inp_default = inp.get("default", "").replace("'", "\\'")
            inp_options = inp.get("options", [])

            # Converte check para JS: None → null JS; string → 'String'
            if raw_check is None or raw_check == "null":
                check_js = "null"
            else:
                check_js = f"'{raw_check}'"

            if inp_type == "dummy":
                inputs_js += f"\n        this.appendDummyInput().appendField('{inp_label}');"

            elif inp_type == "value":
                inputs_js += f"""
        this.appendValueInput('{inp_name}')
            .setCheck({check_js})
            .appendField('{inp_label}');"""

            elif inp_type == "statement":
                inputs_js += f"""
        this.appendStatementInput('{inp_name}')
            .setCheck({check_js})
            .appendField('{inp_label}');"""

            elif inp_type == "field":
                if inp_options:
                    opts = ", ".join([f"['{o}','{o}']" for o in inp_options])
                    inputs_js += f"""
        this.appendDummyInput()
            .appendField('{inp_label}')
            .appendField(new Blockly.FieldDropdown([{opts}]), '{inp_name}');"""
                else:
                    inputs_js += f"""
        this.appendDummyInput()
            .appendField('{inp_label}')
            .appendField(new Blockly.FieldTextInput('{inp_default}'), '{inp_name}');"""

        # Decide setInputsInline automaticamente
        if inline is None:
            # Blocos com ≤3 inputs e sem statement ficam inline (como os nativos)
            has_statement_input = any(i.get("type") == "statement" for i in inputs)
            inline = (len(inputs) <= 3) and not has_statement_input

        inline_js = "this.setInputsInline(true);" if inline else "this.setInputsInline(false);"

        # Conexões
        if block_type == "statement":
            connections_js = "this.setPreviousStatement(true);\n        this.setNextStatement(true);"
        elif block_type == "value":
            connections_js = "this.setOutput(true, null);"
        else:
            connections_js = ""

        # Tooltip
        if tooltip:
            tip = tooltip.get("en", next(iter(tooltip.values()), "")).replace('"', '\\"')
            tooltip_js = f'this.setTooltip("{tip}");'
        else:
            tooltip_js = ""

        # Subcategoria alvo
        subcat_js = ""
        if subcategory:
            subcat_js = f"""
    var subCat = tgt.querySelector('category[name="{subcategory}"]');
    if (subCat) tgt = subCat;"""

        self.inject_js(f"""
(function() {{
    if (!Blockly.Blocks['{name}']) {{
        Blockly.Blocks['{name}'] = {{
            init: function() {{
                this.setColour('{colour}');
                {inputs_js}
                {inline_js}
                {connections_js}
                {tooltip_js}
            }}
        }};
    }}
    var toolbox = document.getElementById('toolbox');
    if (!toolbox) return;
    var cats = toolbox.querySelectorAll('category');
    var tgt = null;
    for (var i = 0; i < cats.length; i++) {{
        if (cats[i].getAttribute('name') === '{category}') {{ tgt = cats[i]; break; }}
    }}
    if (!tgt) return;
    {subcat_js}
    if (!tgt.querySelector('block[type="{name}"]')) {{
        var b = document.createElement('block');
        b.setAttribute('type', '{name}');
        tgt.appendChild(b);
    }}
}})();""")

    def add_separator(self, category: str):
        """Adiciona um separador visual na categoria."""
        self.inject_js(f"""
(function() {{
    var toolbox = document.getElementById('toolbox');
    if (!toolbox) return;
    var cats = toolbox.querySelectorAll('category');
    for (var i = 0; i < cats.length; i++) {{
        if (cats[i].getAttribute('name') === '{category}') {{
            cats[i].appendChild(document.createElement('sep'));
            break;
        }}
    }}
}})();""")

    def refresh_toolbox(self):
        """
        Força atualização da toolbox.
        Chame APENAS quando necessário – cada chamada é cara.
        O manager chama isso uma única vez depois de flush().
        """
        self.inject_js("""
(function() {
    var toolbox = document.getElementById('toolbox');
    if (toolbox && window.workspace) {
        try { workspace.updateToolbox(toolbox); } catch(e) { console.warn('[API] updateToolbox:', e); }
    }
})();""")

    # ============================================================
    # GERADORES DE CÓDIGO
    # FIX: não cria 'var ArduinoGen' local que sombreava o global
    # ============================================================

    def add_generator(self, block_name: str, generator_func: str):
        """
        Adiciona um gerador de código Arduino para o bloco.

        FIX: A versão anterior criava `var ArduinoGen` DENTRO do IIFE,
        sombreando a variável global e fazendo com que o gerador nunca
        fosse registrado no objeto correto.
        """
        self.inject_js(f"""
(function() {{
    if (typeof ArduinoGen === 'undefined') {{
        console.warn('[Extension] ArduinoGen not defined yet when registering {block_name}');
        return;
    }}
    if (!ArduinoGen.forBlock['{block_name}']) {{
        ArduinoGen.forBlock['{block_name}'] = {generator_func};
    }}
}})();""")

    # ============================================================
    # CONSTANTES E FUNÇÕES GLOBAIS ARDUINO
    # ============================================================

    def add_global_constant(self, name: str, value: str):
        """Adiciona uma constante global no código Arduino gerado."""
        self.inject_js(f"""
(function() {{
    if (typeof ArduinoGen !== 'undefined') {{
        ArduinoGen._globals = ArduinoGen._globals || {{}};
        if (!ArduinoGen._globals['{name}']) {{
            ArduinoGen._globals['{name}'] = '{value}';
        }}
    }}
}})();""")

    def add_global_function(self, name: str, func_code: str):
        """Adiciona uma função auxiliar global no código Arduino gerado."""
        escaped_func = func_code.replace("`", "\\`")
        self.inject_js(f"""
(function() {{
    if (typeof ArduinoGen !== 'undefined') {{
        ArduinoGen._globals = ArduinoGen._globals || {{}};
        if (!ArduinoGen._globals['{name}']) {{
            ArduinoGen._globals['{name}'] = `{escaped_func}`;
        }}
    }}
}})();""")

    def add_include(self, header: str):
        """Adiciona um #include no código Arduino gerado."""
        self.inject_js(f"""
(function() {{
    if (typeof ArduinoGen !== 'undefined') {{
        ArduinoGen._includes = ArduinoGen._includes || {{}};
        ArduinoGen._includes['{header}'] = '#include <{header}>';
    }}
}})();""")

    # ============================================================
    # TRADUÇÕES – acumula em dict e injeta EM LOTE no flush()
    # ============================================================

    def add_translation(self, key: str, translations: Dict[str, str]):
        """Acumula uma tradução para ser injetada em lote."""
        for lang, text in translations.items():
            if lang not in self._pending_translations:
                self._pending_translations[lang] = {}
            self._pending_translations[lang][key] = text

    def add_translations(self, translations: Dict[str, Dict[str, str]]):
        """
        Acumula múltiplas traduções para injeção em lote.

        FIX: A versão anterior chamava inject_js() UMA VEZ POR CHAVE,
        gerando dezenas de eval() separados. Agora tudo é acumulado e
        injetado em uma única chamada JS no flush().
        """
        for lang, trans in translations.items():
            if lang not in self._pending_translations:
                self._pending_translations[lang] = {}
            self._pending_translations[lang].update(trans)

    # ============================================================
    # UI
    # ============================================================

    def add_toolbar_button(self, button_id: str, label: str, icon: str, callback: str):
        """Adiciona um botão na toolbar principal."""
        self.inject_js(f"""
(function() {{
    var header = document.getElementById('header');
    if (!header || document.getElementById('{button_id}')) return;
    var btn = document.createElement('button');
    btn.id = '{button_id}';
    btn.className = 'btn btn-serial';
    btn.innerHTML = '<span class="material-icons">{icon}</span> {label}';
    btn.onclick = function() {{ {callback} }};
    var spacer = header.querySelector('.spacer');
    if (spacer) spacer.parentNode.insertBefore(btn, spacer);
    else header.appendChild(btn);
}})();""")

    def add_status_message(self, message: str, msg_type: str = "info"):
        """Loga mensagem no console da IDE."""
        safe = message.replace("'", "\\'")
        self.inject_js(
            f"if (window.log) window.log('{safe}', '{msg_type}'); "
            f"console.log('[Extension] {safe}');"
        )

    # ============================================================
    # UTILIDADES
    # ============================================================

    def get_current_language(self) -> str:
        """Retorna o idioma atual da interface."""
        if self.bridge and hasattr(self.bridge, "tr"):
            return self.bridge.tr.language
        return "en"

    def get_workspace(self):
        """Retorna o workspace do Blockly."""
        return self.workspace

    def get_extension_path(self) -> Path:
        """Retorna o caminho da pasta da extensão."""
        return self._ext_path

    def load_json(self, filename: str) -> dict:
        """Carrega um arquivo JSON da extensão."""
        if self._ext_path:
            file_path = self._ext_path / filename
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        return {}


# ================================================================
# Tipos auxiliares (mantidos para compatibilidade de importação)
# ================================================================

from enum import Enum
from dataclasses import dataclass, field as dc_field


class BlockType(str, Enum):
    STATEMENT = "statement"
    VALUE = "value"
    HAT = "hat"


class InputType(str, Enum):
    VALUE = "value"
    STATEMENT = "statement"
    DUMMY = "dummy"
    FIELD = "field"


@dataclass
class BlockInput:
    name: str = ""
    type: str = "dummy"
    label: str = ""
    check: Optional[str] = None
    default: str = ""
    options: List[str] = dc_field(default_factory=list)


@dataclass
class BlockDefinition:
    name: str
    block_type: str = "statement"
    category: str = ""
    colour: str = "#666666"
    inputs: List[BlockInput] = dc_field(default_factory=list)
    tooltip: Dict[str, str] = dc_field(default_factory=dict)
    subcategory: str = ""
    inline: Optional[bool] = None


@dataclass
class CategoryDefinition:
    name: str
    parent: str = ""
    colour: str = "#666666"
    icon: str = ""