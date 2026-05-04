"""Blockly HTML template builder with full Blockly integration."""
from i18n.translations import Translations

def get_blockly_html(translations: Translations) -> str:
    """Generate the complete Blockly HTML interface with translations."""
    
    return f'''<!DOCTYPE html>
<html lang="{translations.language}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{translations.get('app_title')}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Orbitron:wght@700;900&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<script src="https://unpkg.com/blockly@11.2.1/blockly.min.js"></script>
<script src="qrc:///qtwebchannel/qwebchannel.js"></script>
<style>
:root {{
  --bg:      #080d1a;
  --surface: #0f1729;
  --card:    #162040;
  --border:  #1e3058;
  --accent1: #00d2ff;
  --accent2: #ff5ecc;
  --accent3: #00ff88;
  --accent4: #ffb347;
  --text:    #d8eaff;
  --muted:   #5a7aa0;
  --danger:  #ff4d6d;
  --radius:  12px;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  background: var(--bg);
  color: var(--text);
  font-family: 'Nunito', sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-image:
    radial-gradient(ellipse at 20% 50%, rgba(0,80,160,0.08) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(100,0,180,0.08) 0%, transparent 60%);
}}

#header {{
  background: linear-gradient(135deg, #0a1628 0%, #111d3a 100%);
  border-bottom: 2px solid var(--accent1);
  box-shadow: 0 4px 24px rgba(0,210,255,0.18);
  padding: 0 10px;
  height: 50px;
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  z-index: 10;
  overflow-x: auto;
  overflow-y: hidden;
}}
#header::-webkit-scrollbar {{ height: 2px; }}
#header::-webkit-scrollbar-thumb {{ background: var(--accent1); border-radius: 2px; }}

#logo {{
  font-family: 'Orbitron', sans-serif;
  font-weight: 900;
  font-size: 14px;
  background: linear-gradient(90deg, var(--accent1), #a78bfa, var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 1px;
  white-space: nowrap;
  animation: shimmer 4s linear infinite;
  background-size: 200% auto;
}}
@keyframes shimmer {{ to {{ background-position: 200% center; }} }}

.material-icons {{ font-size: 18px; vertical-align: middle; }}
.logo-icon {{ font-size: 20px; animation: spin 6s linear infinite; display: inline-block; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}

.sep {{ width: 1px; height: 28px; background: var(--border); margin: 0 2px; flex-shrink: 0; }}

.ctrl-group {{
  display: flex; align-items: center; gap: 4px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 3px 7px;
  flex-shrink: 0;
}}
.ctrl-label {{
  font-size: 9px; font-weight: 800;
  text-transform: uppercase; letter-spacing: 1px;
  color: var(--muted); white-space: nowrap;
}}
select {{
  background: rgba(0,0,0,0.4);
  border: 1px solid var(--accent1);
  border-radius: 5px;
  color: var(--text);
  padding: 3px 6px;
  font-family: 'Nunito', sans-serif;
  font-size: 11px; font-weight: 700;
  cursor: pointer; outline: none;
  max-width: 160px;
}}
select:focus {{ border-color: var(--accent2); box-shadow: 0 0 6px rgba(255,94,204,0.3); }}

.btn {{
  border: none; border-radius: 6px;
  padding: 5px 10px;
  font-family: 'Nunito', sans-serif;
  font-weight: 800; font-size: 11px;
  cursor: pointer;
  display: flex; align-items: center; gap: 4px;
  transition: all .2s;
  white-space: nowrap; flex-shrink: 0;
}}
.btn:active {{ transform: scale(0.97); }}
.btn:disabled {{ opacity: 0.4; cursor: not-allowed; }}

.btn-refresh {{ background: rgba(255,255,255,0.08); color: var(--muted); border: 1px solid var(--border); padding: 4px 7px; }}
.btn-refresh:hover {{ background: rgba(255,255,255,0.14); color: var(--text); }}

.btn-new {{ background: rgba(0,255,136,0.1); color: var(--accent3); border: 1px solid rgba(0,255,136,0.3); }}
.btn-new:hover {{ background: rgba(0,255,136,0.2); }}
.btn-save {{ background: rgba(0,210,255,0.1); color: var(--accent1); border: 1px solid rgba(0,210,255,0.3); }}
.btn-save:hover {{ background: rgba(0,210,255,0.2); }}
.btn-load {{ background: rgba(167,139,250,0.1); color: #a78bfa; border: 1px solid rgba(167,139,250,0.3); }}
.btn-load:hover {{ background: rgba(167,139,250,0.2); }}

.btn-compile {{
  background: linear-gradient(135deg, #1a4a8a, #1e6cc8);
  color: white; box-shadow: 0 2px 10px rgba(30,108,200,0.4);
  padding: 5px 12px;
}}
.btn-compile:hover {{ transform: translateY(-1px); box-shadow: 0 4px 16px rgba(30,108,200,0.6); }}

.btn-upload {{
  background: linear-gradient(135deg, #15652a, #1da648);
  color: white; box-shadow: 0 2px 10px rgba(29,166,72,0.4);
  padding: 5px 12px;
}}
.btn-upload:hover {{ transform: translateY(-1px); box-shadow: 0 4px 16px rgba(29,166,72,0.6); }}

.btn-serial {{ background: rgba(255,179,71,0.12); color: var(--accent4); border: 1px solid rgba(255,179,71,0.3); }}
.btn-serial:hover {{ background: rgba(255,179,71,0.22); }}

.btn-lang {{
  background: rgba(255,255,255,0.08);
  color: var(--text);
  border: 1px solid var(--border);
  padding: 5px 8px;
  font-size: 10px;
}}
.btn-lang:hover {{ background: rgba(255,255,255,0.14); }}
.btn-lang.active {{ background: var(--accent1); color: #080d1a; border-color: var(--accent1); }}

.spacer {{ flex: 1; min-width: 4px; }}

#main {{ display: flex; flex: 1; overflow: hidden; }}
#blockly-wrap {{ flex: 1; position: relative; overflow: hidden; }}
#blocklyDiv {{ width: 100%; height: 100%; }}

#code-panel {{
  width: 340px; display: flex; flex-direction: column;
  background: var(--surface); border-left: 2px solid var(--border);
}}
#code-panel-hdr {{
  padding: 10px 14px; background: var(--card);
  border-bottom: 1px solid var(--border);
  font-family: 'Orbitron', sans-serif;
  font-size: 11px; font-weight: 700;
  color: var(--accent1);
  display: flex; justify-content: space-between; align-items: center;
}}
#code-lines {{ font-size: 11px; color: var(--muted); font-family: 'Nunito', sans-serif; }}
#code-view {{
  flex: 1; overflow: auto;
  background: #0d1117; padding: 12px;
  font-family: 'Fira Code', monospace;
  font-size: 11.5px; line-height: 1.65;
  color: #cdd9e5; white-space: pre; tab-size: 2;
}}

#log-wrap {{
  height: 130px; flex-shrink: 0;
  display: flex; flex-direction: column;
  border-top: 2px solid var(--border);
}}
#log-hdr {{
  padding: 5px 14px; background: var(--card);
  border-bottom: 1px solid var(--border);
  font-family: 'Orbitron', sans-serif;
  font-size: 10px; font-weight: 700; color: var(--muted);
  display: flex; align-items: center; gap: 8px;
}}
#log {{
  flex: 1; overflow-y: auto;
  padding: 6px 12px; background: #080b13;
  font-family: 'Fira Code', monospace;
  font-size: 11px; line-height: 1.5;
}}
.log-info {{ color: #5a7aa0; }}
.log-ok   {{ color: #00e676; }}
.log-err  {{ color: #ff5252; }}
.log-warn {{ color: #ffb347; }}
.log-step {{ color: #00d2ff; }}

#status {{
  background: #060a14; border-top: 1px solid var(--border);
  padding: 3px 16px; font-size: 10.5px; color: var(--muted);
  display: flex; align-items: center; gap: 14px; flex-shrink: 0;
}}
.dot {{
  width: 7px; height: 7px; border-radius: 50%;
  background: #2a3f5f; display: inline-block; margin-right: 4px;
}}
.dot.ok {{ background: var(--accent3); box-shadow: 0 0 6px var(--accent3); }}
.dot.err {{ background: var(--danger); }}
.dot.blink {{ animation: blink .8s step-end infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}

#loading {{
  position: fixed; inset: 0;
  background: rgba(8,13,26,0.94);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  z-index: 9999; gap: 16px;
}}
.spinner {{
  width: 50px; height: 50px;
  border: 4px solid var(--border);
  border-top-color: var(--accent1);
  border-radius: 50%;
  animation: rotate 1s linear infinite;
}}
@keyframes rotate {{ to {{ transform: rotate(360deg); }} }}
.loading-text {{ font-family: 'Orbitron', sans-serif; font-size: 14px; color: var(--accent1); }}

#examples-bar {{
  display: flex; align-items: center; gap: 6px;
  padding: 4px 14px; background: rgba(0,0,0,0.3);
  border-bottom: 1px solid var(--border);
  font-size: 11px; flex-shrink: 0; overflow-x: auto;
}}
.ex-btn {{
  border: 1px solid rgba(0,210,255,0.25);
  background: rgba(0,210,255,0.06);
  color: var(--accent1);
  border-radius: 20px; padding: 3px 12px;
  font-family: 'Nunito', sans-serif;
  font-size: 11px; font-weight: 700;
  cursor: pointer; white-space: nowrap;
  transition: all .2s;
}}
.ex-btn:hover {{ background: rgba(0,210,255,0.15); border-color: var(--accent1); }}
.ex-label {{ color: var(--muted); font-weight: 700; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; white-space: nowrap; }}
</style>
</head>
<body>

<div id="loading">
  <div class="spinner"></div>
  <div class="loading-text">{translations.get('app_title')}</div>
</div>

<div id="header">
  <span class="material-icons logo-icon">memory</span>
  <div id="logo">ARDUBLOCK</div>
  <div class="sep"></div>

  <div class="ctrl-group">
    <button class="btn btn-new" title="{translations.get('menu_new')}" onclick="newProject()">
      <span class="material-icons">add</span>
    </button>
    <button class="btn btn-save" title="{translations.get('menu_save')}" onclick="saveProject()">
      <span class="material-icons">save</span>
    </button>
    <button class="btn btn-load" title="{translations.get('menu_open')}" onclick="loadProject()">
      <span class="material-icons">folder_open</span>
    </button>
  </div>

  <div class="sep"></div>

  <div class="ctrl-group">
    <span class="ctrl-label">{translations.get('board_label')}</span>
    <select id="boardSelect" onchange="onBoardChange()"></select>
  </div>

  <div class="ctrl-group">
    <span class="ctrl-label">{translations.get('port_label')}</span>
    <select id="portSelect"></select>
    <button class="btn btn-refresh" title="Detect boards" onclick="detectBoards()">
      <span class="material-icons">refresh</span>
    </button>
  </div>

  <div class="sep"></div>

  <div class="ctrl-group">
    <span class="ctrl-label">Programmer</span>
    <select id="programmerSelect" onchange="onProgrammerChange()">
      <option value="">-- Default --</option>
    </select>
  </div>

  <div class="sep"></div>

  <button class="btn btn-compile" onclick="doCompile()">
    <span class="material-icons">build</span> {translations.get('btn_verify')}
  </button>
  <button class="btn btn-upload" onclick="doUpload()">
    <span class="material-icons">cloud_upload</span> {translations.get('btn_upload')}
  </button>
  <button class="btn btn-serial" onclick="openSerial()">
    <span class="material-icons">terminal</span> {translations.get('btn_serial')}
  </button>

  <button class="btn btn-serial" onclick="openLibraryManager()">
    <span class="material-icons">inventory_2</span> Libraries
  </button>

  <div class="spacer"></div>

  <div class="ctrl-group">
    <button class="btn btn-lang active" id="btnLangEN" onclick="changeLanguage('en')">EN</button>
    <button class="btn btn-lang" id="btnLangPT" onclick="changeLanguage('pt')">PT</button>
  </div>

  <span style="font-size:10px;color:var(--muted);font-family:'Orbitron',sans-serif;white-space:nowrap;" id="cliVer">CLI: ?</span>
</div>

<div id="examples-bar">
  <span class="ex-label"><span class="material-icons">school</span> {translations.get('examples_label')}</span>
  <button class="ex-btn" onclick="loadExample('blink')"><span class="material-icons">lightbulb</span> {translations.get('ex_blink')}</button>
  <button class="ex-btn" onclick="loadExample('traffic')"><span class="material-icons">traffic</span> {translations.get('ex_traffic')}</button>
  <button class="ex-btn" onclick="loadExample('serial')"><span class="material-icons">textsms</span> {translations.get('ex_serial_hello')}</button>
  <button class="ex-btn" onclick="loadExample('servo')"><span class="material-icons">settings</span> {translations.get('ex_servo')}</button>
  <button class="ex-btn" onclick="loadExample('ultrasonic')"><span class="material-icons">straighten</span> {translations.get('ex_ultrasonic')}</button>
  <button class="ex-btn" onclick="loadExample('analog')"><span class="material-icons">show_chart</span> {translations.get('ex_analog')}</button>
  <button class="ex-btn" onclick="loadExample('pwm')"><span class="material-icons">flare</span> {translations.get('ex_pwm')}</button>
  <button class="ex-btn" onclick="loadExample('tone')"><span class="material-icons">music_note</span> {translations.get('ex_tone')}</button>
</div>

<div id="main">
  <div id="blockly-wrap"><div id="blocklyDiv"></div></div>
  <div id="code-panel">
    <div id="code-panel-hdr">
      <span><span class="material-icons">code</span> {translations.get('code_title')}</span>
      <span id="code-lines">0 lines</span>
    </div>
    <pre id="code-view">// Add blocks to generate code!</pre>
  </div>
</div>

<div id="log-wrap">
  <div id="log-hdr">
    <span><span class="material-icons">terminal</span> {translations.get('console_title')}</span>
    <button class="btn btn-refresh" style="font-size:10px;padding:2px 8px;" onclick="clearLog()">Clear</button>
  </div>
  <div id="log"></div>
</div>

<div id="status">
  <span><span class="dot" id="cliDot"></span><span id="cliStatus">CLI not found</span></span>
  <span><span class="dot" id="boardDot"></span><span id="boardStatus">No board</span></span>
  <span id="blockCount">0 blocks</span>
  <div style="flex:1"></div>
  <span>{translations.get('app_title')} 1.1</span>
</div>

<xml id="toolbox" style="display:none">
  <category name="{translations.get('category_structure')}" colour="#c97a1e">
    <block type="ab_program"></block>
    <block type="ab_comment"><field name="TEXT">Write your comment here</field></block>
  </category>
  <sep></sep>
  <category name="{translations.get('category_functions')}" colour="#6b46c1">
    <block type="procedures_defnoreturn">
      <mutation><arg name="x"></arg></mutation>
      <field name="NAME">myFunction</field>
    </block>
    <block type="procedures_defreturn">
      <mutation><arg name="x"></arg></mutation>
      <field name="NAME">myFunction</field>
      <field name="RETTYPE">int</field>
    </block>
    <block type="procedures_callnoreturn">
      <mutation><arg name="x"></arg></mutation>
      <field name="NAME">myFunction</field>
    </block>
    <block type="ab_return"></block>
  </category>
  <sep></sep>
  <category name="{translations.get('category_digital')}" colour="#1a5eb5">
    <block type="ab_pin_mode"><field name="PIN">13</field><field name="MODE">OUTPUT</field></block>
    <block type="ab_digital_write"><field name="PIN">13</field><field name="STATE">HIGH</field></block>
    <block type="ab_digital_read"><field name="PIN">2</field></block>
  </category>
  <category name="{translations.get('category_analog')}" colour="#0a7a6e">
    <block type="ab_analog_write"><field name="PIN">9</field><value name="VALUE"><shadow type="ab_number"><field name="NUM">128</field></shadow></value></block>
    <block type="ab_analog_read"><field name="PIN">A0</field></block>
  </category>
  <sep></sep>
  <category name="{translations.get('category_time')}" colour="#2d7a2d">
    <block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">1000</field></shadow></value></block>
    <block type="ab_delay_sec"><value name="SEC"><shadow type="ab_number"><field name="NUM">1</field></shadow></value></block>
    <block type="ab_millis"></block>
    <block type="ab_micros"></block>
  </category>
  <category name="{translations.get('category_serial')}" colour="#7a1a9c">
    <block type="ab_serial_begin"><field name="BAUD">9600</field></block>
    <block type="ab_serial_print"><value name="TEXT"><shadow type="ab_text"><field name="TEXT">Hello, World!</field></shadow></value></block>
    <block type="ab_serial_println"><value name="TEXT"><shadow type="ab_text"><field name="TEXT">Hello, World!</field></shadow></value></block>
    <block type="ab_serial_available"></block>
    <block type="ab_serial_read"></block>
  </category>
  <sep></sep>
  <category name="{translations.get('category_control')}" colour="#9c1a4a">
    <block type="controls_if"><mutation elseif="1" else="1"></mutation><value name="IF0"><shadow type="ab_bool"><field name="BOOL">true</field></shadow></value></block>
    <block type="ab_while"><value name="COND"><shadow type="ab_bool"><field name="BOOL">true</field></shadow></value></block>
    <block type="ab_for"><field name="VAR">i</field><field name="FROM">0</field><field name="TO">9</field><field name="STEP">1</field></block>
    <block type="ab_break"></block>
  </category>
  <category name="{translations.get('category_math')}" colour="#1a7a6e">
    <block type="ab_number"><field name="NUM">0</field></block>
    <block type="ab_arithmetic"><value name="A"><shadow type="ab_number"><field name="NUM">0</field></shadow></value><value name="B"><shadow type="ab_number"><field name="NUM">0</field></shadow></value></block>
    <block type="ab_map"><value name="VAL"><shadow type="ab_number"><field name="NUM">0</field></shadow></value><value name="FL"><shadow type="ab_number"><field name="NUM">0</field></shadow></value><value name="FH"><shadow type="ab_number"><field name="NUM">1023</field></shadow></value><value name="TL"><shadow type="ab_number"><field name="NUM">0</field></shadow></value><value name="TH"><shadow type="ab_number"><field name="NUM">255</field></shadow></value></block>
    <block type="ab_constrain"><value name="VAL"><shadow type="ab_number"><field name="NUM">0</field></shadow></value><value name="LO"><shadow type="ab_number"><field name="NUM">0</field></shadow></value><value name="HI"><shadow type="ab_number"><field name="NUM">100</field></shadow></value></block>
    <block type="ab_random"><value name="MIN"><shadow type="ab_number"><field name="NUM">0</field></shadow></value><value name="MAX"><shadow type="ab_number"><field name="NUM">100</field></shadow></value></block>
    <block type="ab_abs"><value name="VAL"><shadow type="ab_number"><field name="NUM">-1</field></shadow></value></block>
  </category>
  <category name="{translations.get('category_logic')}" colour="#9c3a1a">
    <block type="ab_compare"><value name="A"><shadow type="ab_number"><field name="NUM">0</field></shadow></value><value name="B"><shadow type="ab_number"><field name="NUM">0</field></shadow></value></block>
    <block type="ab_logic_op"><value name="A"><shadow type="ab_bool"><field name="BOOL">true</field></shadow></value><value name="B"><shadow type="ab_bool"><field name="BOOL">true</field></shadow></value></block>
    <block type="ab_not"><value name="BOOL"><shadow type="ab_bool"><field name="BOOL">true</field></shadow></value></block>
    <block type="ab_bool"><field name="BOOL">true</field></block>
  </category>
  <category name="{translations.get('category_variables')}" colour="#c97a1e">
    <block type="ab_global_var">
      <field name="TYPE">int</field>
      <field name="NAME">counter</field>
      <value name="VALUE"><shadow type="ab_number"><field name="NUM">0</field></shadow></value>
    </block>
    <block type="ab_local_var">
      <field name="TYPE">int</field>
      <field name="NAME">counter</field>
      <value name="VALUE"><shadow type="ab_number"><field name="NUM">0</field></shadow></value>
    </block>
    <block type="ab_var_set">
      <field name="NAME">counter</field>
      <value name="VALUE"><shadow type="ab_number"><field name="NUM">0</field></shadow></value>
    </block>
    <block type="ab_var_get"><field name="NAME">counter</field></block>
    <block type="ab_text"><field name="TEXT">text</field></block>
  </category>
  <sep></sep>
  <category name="{translations.get('category_leds')}" colour="#c97a00">
    <block type="ab_led_on"><field name="PIN">13</field></block>
    <block type="ab_led_off"><field name="PIN">13</field></block>
    <block type="ab_pwm_set"><field name="PIN">9</field><value name="VAL"><shadow type="ab_number"><field name="NUM">128</field></shadow></value></block>
    <block type="ab_tone"><field name="PIN">8</field><value name="FREQ"><shadow type="ab_number"><field name="NUM">440</field></shadow></value><value name="DUR"><shadow type="ab_number"><field name="NUM">500</field></shadow></value></block>
    <block type="ab_notone"><field name="PIN">8</field></block>
  </category>
  <category name="{translations.get('category_servo')}" colour="#9c1a1a">
    <block type="ab_servo_attach"><field name="OBJ">myServo</field><field name="PIN">9</field></block>
    <block type="ab_servo_write"><field name="OBJ">myServo</field><value name="ANGLE"><shadow type="ab_number"><field name="NUM">90</field></shadow></value></block>
    <block type="ab_servo_read"><field name="OBJ">myServo</field></block>
  </category>
  <category name="{translations.get('category_sensors')}" colour="#1a1a9c">
    <block type="ab_ultrasonic"><field name="TRIG">9</field><field name="ECHO">10</field></block>
    <block type="ab_dht"><field name="PIN">2</field><field name="TYPE">DHT11</field><field name="WHAT">temperature</field></block>
    <block type="ab_ldr"><field name="PIN">A0</field></block>
    <block type="ab_button"><field name="PIN">2</field></block>
  </category>
</xml>

<script>
'use strict';

function loadProgrammers() {{
    if (!pyBridge || typeof pyBridge.getProgrammers !== 'function') return;
    pyBridge.getProgrammers(programmersJson => {{
        try {{
            const programmers = JSON.parse(programmersJson);
            const sel = document.getElementById('programmerSelect');
            sel.innerHTML = '<option value="">-- Default --</option>';
            programmers.forEach(prog => {{
                const opt = document.createElement('option');
                opt.value = prog.id;
                opt.textContent = prog.name;
                sel.appendChild(opt);
            }});
        }} catch(e) {{
            console.error('Error loading programmers:', e);
        }}
    }});
}}

function onProgrammerChange() {{
    const programmer = document.getElementById('programmerSelect').value;
    if (pyBridge && typeof pyBridge.setProgrammer === 'function') {{
        pyBridge.setProgrammer(programmer);
    }}
    log('Programmer: ' + (programmer || 'Default'), 'info');
}}

function doUpload() {{
    if (!pyBridge) return;
    const fqbn = document.getElementById('boardSelect').value;
    const port = document.getElementById('portSelect').value;
    const programmer = document.getElementById('programmerSelect').value;
    if (!fqbn || !port) {{
        log('Select board and port!', 'err');
        return;
    }}
    pyBridge.upload(getGeneratedCode(), fqbn, port, programmer);
}}

function openLibraryManager() {{
  if (pyBridge && typeof pyBridge.openLibraryManager === 'function') {{
    pyBridge.openLibraryManager();
  }} else {{
    log('Library Manager not available (CLI required)', 'warn');
  }}
}}

// ============================================================
// TRANSLATION UPDATER
// ============================================================
let currentTranslations = {{}};

function updateTranslations(translationsJson) {{
  try {{
    currentTranslations = JSON.parse(translationsJson);
    console.log('[i18n] Translations updated: ' + Object.keys(currentTranslations).length + ' keys');
    
    // Atualizar categorias SEM recriar o toolbox
    updateCategoryNames();
    
    // Atualizar labels da interface
    updateUILabels();
    
    log('Language changed to: ' + (currentLanguage === 'pt' ? 'Português' : 'English'), 'ok');
  }} catch(e) {{
    console.error('[i18n] Error updating translations:', e);
  }}
}}

function updateCategoryNames() {{
  if (!currentTranslations || Object.keys(currentTranslations).length === 0) return;
  
  // Mapa fixo: chave_traducao -> nome_em_ingles
  var nameMap = {{
    'category_structure': 'Structure',
    'category_functions': 'Functions',
    'category_digital': 'Digital Pins',
    'category_analog': 'Analog Pins',
    'category_time': 'Time',
    'category_serial': 'Serial Monitor',
    'category_control': 'Control Flow',
    'category_math': 'Mathematics',
    'category_logic': 'Logic',
    'category_variables': 'Variables',
    'category_leds': 'LEDs and Outputs',
    'category_servo': 'Servo Motor',
    'category_sensors': 'Sensors'
  }};
  
  var toolbox = document.getElementById('toolbox');
  if (!toolbox) return;
  
  var categories = toolbox.querySelectorAll('category');
  var updatedCount = 0;
  
  categories.forEach(function(cat) {{
    var currentName = cat.getAttribute('name');
    
    // Procurar qual chave corresponde a esta categoria
    for (var key in nameMap) {{
      var enName = nameMap[key];
      var ptName = currentTranslations[key] || enName;
      
      // Se o nome atual bate com inglês OU português, atualizar
      if (currentName === enName || currentName === ptName) {{
        var newName = currentTranslations[key] || enName;
        cat.setAttribute('name', newName);
        updatedCount++;
        console.log('[i18n] Category: ' + currentName + ' -> ' + newName);
        break;
      }}
    }}
  }});
  
  console.log('[i18n] Updated ' + updatedCount + ' categories');
  
  // Atualizar o Blockly para refletir as mudanças
  if (workspace && typeof workspace.updateToolbox === 'function') {{
    try {{
      workspace.updateToolbox(toolbox);
    }} catch(e) {{
      console.warn('[i18n] Blockly updateToolbox failed:', e);
    }}
  }}
}}

function updateUILabels() {{
  var t = currentTranslations;
  
  // Atualizar labels do header
  var ctrlLabels = document.querySelectorAll('.ctrl-label');
  if (ctrlLabels.length >= 1 && t['board_label']) ctrlLabels[0].textContent = t['board_label'];
  if (ctrlLabels.length >= 2 && t['port_label']) ctrlLabels[1].textContent = t['port_label'];
  
  // Atualizar botão Verify
  if (t['btn_verify']) {{
    var btn = document.querySelector('.btn-compile');
    if (btn) btn.innerHTML = '<span class="material-icons">build</span> ' + t['btn_verify'];
  }}
  
  // Atualizar botão Upload
  if (t['btn_upload']) {{
    var btn = document.querySelector('.btn-upload');
    if (btn) btn.innerHTML = '<span class="material-icons">cloud_upload</span> ' + t['btn_upload'];
  }}
  
  // Atualizar botão Serial
  if (t['btn_serial']) {{
    var btns = document.querySelectorAll('.btn-serial');
    btns.forEach(function(btn) {{
      if (btn.querySelector('.material-icons') && 
          (btn.textContent.includes('Serial') || btn.textContent.includes('Libraries'))) {{
        // Não alterar botão Libraries
        if (btn.textContent.includes('Libraries') || btn.textContent.includes('Extensions')) return;
        btn.innerHTML = '<span class="material-icons">terminal</span> ' + t['btn_serial'];
      }}
    }});
  }}
  
  // Atualizar painel de código
  if (t['code_title']) {{
    var el = document.querySelector('#code-panel-hdr span');
    if (el) el.innerHTML = '<span class="material-icons">code</span> ' + t['code_title'];
  }}
  
  // Atualizar console
  if (t['console_title']) {{
    var el = document.querySelector('#log-hdr span');
    if (el) el.innerHTML = '<span class="material-icons">terminal</span> ' + t['console_title'];
  }}
  
  // Atualizar exemplos
  if (t['examples_label']) {{
    var el = document.querySelector('.ex-label');
    if (el) el.innerHTML = '<span class="material-icons">school</span> ' + t['examples_label'];
  }}
  
  // Atualizar botões de exemplos
  var exKeys = ['ex_blink', 'ex_traffic', 'ex_serial_hello', 'ex_servo', 
                'ex_ultrasonic', 'ex_analog', 'ex_pwm', 'ex_tone'];
  var exBtns = document.querySelectorAll('.ex-btn');
  exKeys.forEach(function(key, idx) {{
    if (t[key] && exBtns[idx]) {{
      var icon = exBtns[idx].querySelector('.material-icons');
      if (icon) {{
        exBtns[idx].innerHTML = icon.outerHTML + ' ' + t[key];
      }}
    }}
  }});
  
  // Atualizar títulos dos botões (tooltips)
  if (t['menu_new']) {{
    var btn = document.querySelector('.btn-new');
    if (btn) btn.title = t['menu_new'];
  }}
  if (t['menu_save']) {{
    var btn = document.querySelector('.btn-save');
    if (btn) btn.title = t['menu_save'];
  }}
  if (t['menu_open']) {{
    var btn = document.querySelector('.btn-load');
    if (btn) btn.title = t['menu_open'];
  }}
  
  // Atualizar status
  if (t['status_ready']) {{
    var statusBar = document.querySelector('#status span:last-child');
    // Não alterar o nome do app na barra de status
  }}
}}


function changeLanguage(lang) {{
  currentLanguage = lang;
  
  document.getElementById('btnLangEN').classList.toggle('active', lang === 'en');
  document.getElementById('btnLangPT').classList.toggle('active', lang === 'pt');
  
  if (pyBridge && typeof pyBridge.setLanguage === 'function') {{
    pyBridge.setLanguage(lang);
  }}
  
  log('Changing to: ' + lang.toUpperCase(), 'info');
}}

// ============================================================
// POLYFILL: Blockly v11.2 compatibility
// ============================================================
(function() {{
  if (typeof Blockly !== 'undefined' && Blockly.utils && Blockly.utils.style) {{
    if (!Blockly.utils.style.getSize) {{
      Blockly.utils.style.getSize = function(element) {{
        if (Blockly.utils.style.getSizeWithDisplay) {{
          return Blockly.utils.style.getSizeWithDisplay(element);
        }}
        var style = window.getComputedStyle(element);
        if (style.display === 'none') {{
          var original = element.style.display;
          element.style.display = 'block';
          var size = {{
            width: element.offsetWidth,
            height: element.offsetHeight
          }};
          element.style.display = original;
          return size;
        }}
        return {{
          width: element.offsetWidth,
          height: element.offsetHeight
        }};
      }};
    }}
  }}
}})();

// ============================================================
// GLOBAL STATE
// ============================================================
let workspace = null;
let pyBridge  = null;
let currentFQBN = 'arduino:avr:uno';
let allBoards = [];
let connectedBoards = [];
let codeUpdateTimer = null;
let currentLanguage = 'en';

// ============================================================
// CUSTOM BLOCK DEFINITIONS
// ============================================================

// -- Main Program Block --
Blockly.Blocks['ab_program'] = {{
  init: function() {{
    this.setColour('#c97a1e');
    this.appendDummyInput().appendField("Arduino Program");
    this.appendStatementInput('SETUP').setCheck(null).appendField("Setup");
    this.appendStatementInput('LOOP').setCheck(null).appendField("Loop");
    this.setTooltip("Main block. Setup runs once; Loop runs forever.");
    this.setDeletable(true);
    this.setMovable(true);
  }}
}};

// -- Comment --
Blockly.Blocks['ab_comment'] = {{
  init: function() {{
    this.setColour('#4a5568');
    this.appendDummyInput().appendField(new Blockly.FieldTextInput('comment'), 'TEXT');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- Function Definition without Return --
Blockly.Blocks['procedures_defnoreturn'] = {{
  init: function() {{
    this.setColour('#6b46c1');
    this.appendDummyInput()
        .appendField("Create function")
        .appendField(new Blockly.FieldTextInput('myFunction'), 'NAME');
    this.appendStatementInput('STACK').setCheck(null).appendField("do:");
    this.setMutator(new Blockly.icons.MutatorIcon(['procedures_mutatorarg'], this));
    this.arguments_ = [];
    this.setTooltip("Define a function without return value. Goes outside setup/loop.");
  }},
  
  updateParams_: function() {{
    let i = 1;
    while (this.getInput('ARG' + i)) {{ this.removeInput('ARG' + i); i++; }}
    for (let j = 0; j < this.arguments_.length; j++) {{
      this.appendDummyInput('ARG' + (j + 1))
          .appendField(new Blockly.FieldDropdown([['int','int'],['float','float'],['bool','bool'],['String','String'],['long','long'],['byte','byte'],['char','char']]), 'TYPE' + (j + 1))
          .appendField(new Blockly.FieldTextInput('x' + (j + 1)), 'NAME' + (j + 1));
    }}
  }},
  
  mutationToDom: function() {{
    const container = Blockly.utils.xml.createElement('mutation');
    for (let i = 0; i < this.arguments_.length; i++) {{
      const param = Blockly.utils.xml.createElement('arg');
      param.setAttribute('name', this.arguments_[i]);
      container.appendChild(param);
    }}
    return container;
  }},
  
  domToMutation: function(xmlElement) {{
    this.arguments_ = [];
    const children = xmlElement.children || xmlElement.childNodes || [];
    for (let i = 0; i < children.length; i++) {{
      if (children[i].nodeName.toLowerCase() === 'arg') {{
        this.arguments_.push(children[i].getAttribute('name'));
      }}
    }}
    this.updateParams_();
  }},
  
  decompose: function(workspace) {{
    const containerBlock = workspace.newBlock('procedures_mutatorcontainer');
    containerBlock.initSvg();
    let connection = containerBlock.getInput('STACK').connection;
    for (let i = 0; i < this.arguments_.length; i++) {{
      const paramBlock = workspace.newBlock('procedures_mutatorarg');
      paramBlock.initSvg();
      paramBlock.setFieldValue(this.arguments_[i], 'NAME');
      connection.connect(paramBlock.previousConnection);
      connection = paramBlock.nextConnection;
    }}
    return containerBlock;
  }},
  
  compose: function(containerBlock) {{
    this.arguments_ = [];
    let paramBlock = containerBlock.getInputTargetBlock('STACK');
    while (paramBlock) {{
      this.arguments_.push(paramBlock.getFieldValue('NAME'));
      paramBlock = paramBlock.nextConnection && paramBlock.nextConnection.targetBlock();
    }}
    this.updateParams_();
  }}
}};

// -- Function Definition with Return --
Blockly.Blocks['procedures_defreturn'] = {{
  init: function() {{
    this.setColour('#6b46c1');
    this.appendDummyInput()
        .appendField("Create function with return")
        .appendField(new Blockly.FieldTextInput('myFunction'), 'NAME');
    this.appendDummyInput()
        .appendField("return type:")
        .appendField(new Blockly.FieldDropdown([
          ['int','int'],['float','float'],['bool','bool'],
          ['String','String'],['long','long']
        ]), 'RETTYPE');
    this.appendStatementInput('STACK').setCheck(null).appendField("do:");
    this.setMutator(new Blockly.icons.MutatorIcon(['procedures_mutatorarg'], this));
    this.arguments_ = [];
    this.setTooltip("Define a function with return value. Goes outside setup/loop.");
  }},
  updateParams_: Blockly.Blocks['procedures_defnoreturn'].updateParams_,
  mutationToDom: Blockly.Blocks['procedures_defnoreturn'].mutationToDom,
  domToMutation: Blockly.Blocks['procedures_defnoreturn'].domToMutation,
  decompose: Blockly.Blocks['procedures_defnoreturn'].decompose,
  compose: Blockly.Blocks['procedures_defnoreturn'].compose
}};

// -- Function Call --
Blockly.Blocks['procedures_callnoreturn'] = {{
  init: function() {{
    this.setColour('#6b46c1');
    this.appendDummyInput().appendField("Call").appendField(new Blockly.FieldTextInput('myFunction'), 'NAME');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.arguments_ = [];
  }},
  updateParams_: function() {{
    let i = 1;
    while (this.getInput('ARG' + i)) {{ this.removeInput('ARG' + i); i++; }}
    for (let j = 0; j < this.arguments_.length; j++) {{
      this.appendValueInput('ARG' + (j + 1)).setCheck(null).appendField(this.arguments_[j] + ':');
    }}
  }},
  mutationToDom: function() {{
    const container = Blockly.utils.xml.createElement('mutation');
    for (let i = 0; i < this.arguments_.length; i++) {{
      const param = Blockly.utils.xml.createElement('arg');
      param.setAttribute('name', this.arguments_[i]);
      container.appendChild(param);
    }}
    return container;
  }},
  domToMutation: function(xmlElement) {{
    this.arguments_ = [];
    const children = xmlElement.children || xmlElement.childNodes || [];
    for (let i = 0; i < children.length; i++) {{
      if (children[i].nodeName.toLowerCase() === 'arg') {{
        this.arguments_.push(children[i].getAttribute('name'));
      }}
    }}
    this.updateParams_();
  }}
}};

// Mutator helper blocks
Blockly.Blocks['procedures_mutatorcontainer'] = {{
  init: function() {{
    this.setColour('#6b46c1');
    this.appendDummyInput().appendField("Parameters");
    this.appendStatementInput('STACK');
    this.contextMenu = false;
  }}
}};

Blockly.Blocks['procedures_mutatorarg'] = {{
  init: function() {{
    this.setColour('#6b46c1');
    this.appendDummyInput().appendField("parameter:").appendField(new Blockly.FieldTextInput('x'), 'NAME');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.contextMenu = false;
  }}
}};

// -- Return --
Blockly.Blocks['ab_return'] = {{
  init: function() {{
    this.setColour('#6b46c1');
    this.appendValueInput('VAL').setCheck(null).appendField("Return");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
  }}
}};

// -- pinMode --
Blockly.Blocks['ab_pin_mode'] = {{
  init: function() {{
    this.setColour('#1a5eb5');
    this.appendDummyInput()
        .appendField("Pin")
        .appendField(new Blockly.FieldDropdown([['0','0'],['1','1'],['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9'],['10','10'],['11','11'],['12','12'],['13','13']]), 'PIN')
        .appendField("as")
        .appendField(new Blockly.FieldDropdown([['OUTPUT','OUTPUT'],['INPUT','INPUT'],['INPUT_PULLUP','INPUT_PULLUP']]), 'MODE');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- digitalWrite --
Blockly.Blocks['ab_digital_write'] = {{
  init: function() {{
    this.setColour('#1a5eb5');
    this.appendDummyInput()
        .appendField("Pin")
        .appendField(new Blockly.FieldDropdown([['0','0'],['1','1'],['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9'],['10','10'],['11','11'],['12','12'],['13','13']]), 'PIN')
        .appendField("=")
        .appendField(new Blockly.FieldDropdown([['HIGH','HIGH'],['LOW','LOW']]), 'STATE');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- digitalRead --
Blockly.Blocks['ab_digital_read'] = {{
  init: function() {{
    this.setColour('#1a5eb5');
    this.appendDummyInput().appendField("Read digital pin").appendField(new Blockly.FieldDropdown([['0','0'],['1','1'],['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9'],['10','10'],['11','11'],['12','12'],['13','13']]), 'PIN');
    this.setOutput(true, 'Boolean');
  }}
}};

// -- analogWrite --
Blockly.Blocks['ab_analog_write'] = {{
  init: function() {{
    this.setColour('#0a7a6e');
    this.appendValueInput('VALUE').setCheck('Number').appendField("PWM Pin").appendField(new Blockly.FieldDropdown([['3','3'],['5','5'],['6','6'],['9','9'],['10','10'],['11','11']]), 'PIN').appendField("= (0-255)");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- analogRead --
Blockly.Blocks['ab_analog_read'] = {{
  init: function() {{
    this.setColour('#0a7a6e');
    this.appendDummyInput().appendField("Read analog pin").appendField(new Blockly.FieldDropdown([['A0','A0'],['A1','A1'],['A2','A2'],['A3','A3'],['A4','A4'],['A5','A5']]), 'PIN');
    this.setOutput(true, 'Number');
  }}
}};

// -- delay (ms) --
Blockly.Blocks['ab_delay_ms'] = {{
  init: function() {{
    this.setColour('#2d7a2d');
    this.appendValueInput('MS').setCheck('Number').appendField("Wait");
    this.appendDummyInput().appendField("milliseconds");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- delay (sec) --
Blockly.Blocks['ab_delay_sec'] = {{
  init: function() {{
    this.setColour('#2d7a2d');
    this.appendValueInput('SEC').setCheck('Number').appendField("Wait");
    this.appendDummyInput().appendField("seconds");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- millis --
Blockly.Blocks['ab_millis'] = {{
  init: function() {{
    this.setColour('#2d7a2d');
    this.appendDummyInput().appendField("Elapsed time (ms)");
    this.setOutput(true, 'Number');
  }}
}};

// -- micros --
Blockly.Blocks['ab_micros'] = {{
  init: function() {{
    this.setColour('#2d7a2d');
    this.appendDummyInput().appendField("Elapsed time (us)");
    this.setOutput(true, 'Number');
  }}
}};

// -- Serial.begin --
Blockly.Blocks['ab_serial_begin'] = {{
  init: function() {{
    this.setColour('#7a1a9c');
    this.appendDummyInput().appendField("Start Serial").appendField(new Blockly.FieldDropdown([['9600','9600'],['19200','19200'],['38400','38400'],['57600','57600'],['115200','115200'],['250000','250000']]), 'BAUD').appendField("baud");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- Serial.print --
Blockly.Blocks['ab_serial_print'] = {{
  init: function() {{
    this.setColour('#7a1a9c');
    this.appendValueInput('TEXT').setCheck(null).appendField("Print");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- Serial.println --
Blockly.Blocks['ab_serial_println'] = {{
  init: function() {{
    this.setColour('#7a1a9c');
    this.appendValueInput('TEXT').setCheck(null).appendField("Print line");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- Serial.available --
Blockly.Blocks['ab_serial_available'] = {{
  init: function() {{
    this.setColour('#7a1a9c');
    this.appendDummyInput().appendField("Data available on Serial?");
    this.setOutput(true, 'Boolean');
  }}
}};

// -- Serial.read --
Blockly.Blocks['ab_serial_read'] = {{
  init: function() {{
    this.setColour('#7a1a9c');
    this.appendDummyInput().appendField("Read byte from Serial");
    this.setOutput(true, 'Number');
  }}
}};

// -- IF/ELSE IF/ELSE with Mutator --
Blockly.Blocks['controls_if'] = {{
  init: function() {{
    this.setColour('#9c1a4a');
    this.appendValueInput('IF0').setCheck('Boolean').appendField("IF");
    this.appendStatementInput('DO0').setCheck(null).appendField("do:");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setMutator(new Blockly.icons.MutatorIcon(['controls_if_elseif', 'controls_if_else'], this));
    this.elseifCount_ = 0;
    this.elseCount_ = 0;
  }},
  
  mutationToDom: function() {{
    if (!this.elseifCount_ && !this.elseCount_) return null;
    const container = Blockly.utils.xml.createElement('mutation');
    if (this.elseifCount_) container.setAttribute('elseif', this.elseifCount_);
    if (this.elseCount_) container.setAttribute('else', 1);
    return container;
  }},
  
  domToMutation: function(xmlElement) {{
    this.elseifCount_ = parseInt(xmlElement.getAttribute('elseif'), 10) || 0;
    this.elseCount_ = parseInt(xmlElement.getAttribute('else'), 10) || 0;
    this.updateShape_();
  }},
  
  decompose: function(workspace) {{
    const containerBlock = workspace.newBlock('controls_if_if');
    containerBlock.initSvg();
    let connection = containerBlock.nextConnection;
    for (let i = 1; i <= this.elseifCount_; i++) {{
      const elseifBlock = workspace.newBlock('controls_if_elseif');
      elseifBlock.initSvg();
      connection.connect(elseifBlock.previousConnection);
      connection = elseifBlock.nextConnection;
    }}
    if (this.elseCount_) {{
      const elseBlock = workspace.newBlock('controls_if_else');
      elseBlock.initSvg();
      connection.connect(elseBlock.previousConnection);
    }}
    return containerBlock;
  }},
  
  compose: function(containerBlock) {{
    let clauseBlock = containerBlock.nextConnection.targetBlock();
    this.elseifCount_ = 0;
    this.elseCount_ = 0;
    while (clauseBlock) {{
      if (clauseBlock.type === 'controls_if_elseif') this.elseifCount_++;
      else if (clauseBlock.type === 'controls_if_else') this.elseCount_++;
      clauseBlock = clauseBlock.nextConnection && clauseBlock.nextConnection.targetBlock();
    }}
    this.updateShape_();
  }},
  
  updateShape_: function() {{
    for (let i = 1; i <= 10; i++) {{
      if (this.getInput('IF' + i)) {{ this.removeInput('IF' + i); this.removeInput('DO' + i); }}
    }}
    if (this.getInput('ELSE')) this.removeInput('ELSE');
    
    for (let i = 1; i <= this.elseifCount_; i++) {{
      this.appendValueInput('IF' + i).setCheck('Boolean').appendField("ELSE IF");
      this.appendStatementInput('DO' + i).setCheck(null).appendField("do:");
    }}
    if (this.elseCount_) {{
      this.appendStatementInput('ELSE').setCheck(null).appendField("ELSE");
    }}
  }}
}};

Blockly.Blocks['controls_if_elseif'] = {{
  init: function() {{
    this.setColour('#9c1a4a');
    this.appendDummyInput().appendField("ELSE IF");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.contextMenu = false;
  }}
}};

Blockly.Blocks['controls_if_else'] = {{
  init: function() {{
    this.setColour('#9c1a4a');
    this.appendDummyInput().appendField("ELSE");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.contextMenu = false;
  }}
}};

Blockly.Blocks['controls_if_if'] = {{
  init: function() {{
    this.setColour('#9c1a4a');
    this.appendDummyInput().appendField("IF");
    this.setNextStatement(true);
    this.contextMenu = false;
  }}
}};

// -- while --
Blockly.Blocks['ab_while'] = {{
  init: function() {{
    this.setColour('#9c1a4a');
    this.appendValueInput('COND').setCheck('Boolean').appendField("WHILE");
    this.appendStatementInput('DO').setCheck(null).appendField("do:");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- for --
Blockly.Blocks['ab_for'] = {{
  init: function() {{
    this.setColour('#9c1a4a');
    this.appendDummyInput()
        .appendField("REPEAT variable")
        .appendField(new Blockly.FieldTextInput('i'), 'VAR')
        .appendField("from")
        .appendField(new Blockly.FieldNumber(0, -Infinity, Infinity, 1), 'FROM')
        .appendField("to")
        .appendField(new Blockly.FieldNumber(9, -Infinity, Infinity, 1), 'TO')
        .appendField("step")
        .appendField(new Blockly.FieldNumber(1, -Infinity, Infinity, 1), 'STEP');
    this.appendStatementInput('DO').setCheck(null).appendField("do:");
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- break --
Blockly.Blocks['ab_break'] = {{
  init: function() {{
    this.setColour('#9c1a4a');
    this.appendDummyInput().appendField("Stop loop (break)");
    this.setPreviousStatement(true);
  }}
}};

// -- Number --
Blockly.Blocks['ab_number'] = {{
  init: function() {{
    this.setColour('#1a7a6e');
    this.appendDummyInput().appendField(new Blockly.FieldNumber(0, -Infinity, Infinity), 'NUM');
    this.setOutput(true, 'Number');
  }}
}};

// -- Arithmetic --
Blockly.Blocks['ab_arithmetic'] = {{
  init: function() {{
    this.setColour('#1a7a6e');
    this.appendValueInput('A').setCheck('Number');
    this.appendDummyInput().appendField(new Blockly.FieldDropdown([['+', '+'], ['-', '-'], ['x', '*'], ['/', '/'], ['% mod', '%']]), 'OP');
    this.appendValueInput('B').setCheck('Number');
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
  }}
}};

// -- map() --
Blockly.Blocks['ab_map'] = {{
  init: function() {{
    this.setColour('#1a7a6e');
    this.appendValueInput('VAL').setCheck('Number').appendField("Map");
    this.appendValueInput('FL').setCheck('Number').appendField("from [");
    this.appendValueInput('FH').setCheck('Number').appendField(",");
    this.appendValueInput('TL').setCheck('Number').appendField("] to [");
    this.appendValueInput('TH').setCheck('Number').appendField(",");
    this.appendDummyInput().appendField("]");
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
  }}
}};

// -- constrain() --
Blockly.Blocks['ab_constrain'] = {{
  init: function() {{
    this.setColour('#1a7a6e');
    this.appendValueInput('VAL').setCheck('Number').appendField("Constrain");
    this.appendValueInput('LO').setCheck('Number').appendField("between");
    this.appendValueInput('HI').setCheck('Number').appendField("and");
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
  }}
}};

// -- random() --
Blockly.Blocks['ab_random'] = {{
  init: function() {{
    this.setColour('#1a7a6e');
    this.appendValueInput('MIN').setCheck('Number').appendField("Random between");
    this.appendValueInput('MAX').setCheck('Number').appendField("and");
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
  }}
}};

// -- abs() --
Blockly.Blocks['ab_abs'] = {{
  init: function() {{
    this.setColour('#1a7a6e');
    this.appendValueInput('VAL').setCheck('Number').appendField("| absolute value |");
    this.setInputsInline(true);
    this.setOutput(true, 'Number');
  }}
}};

// -- Comparison --
Blockly.Blocks['ab_compare'] = {{
  init: function() {{
    this.setColour('#9c3a1a');
    this.appendValueInput('A').setCheck('Number');
    this.appendDummyInput().appendField(new Blockly.FieldDropdown([['= equal to', '=='], ['not equal to', '!='], ['< less than', '<'], ['> greater than', '>'], ['<= less or equal', '<='], ['>= greater or equal', '>=']]), 'OP');
    this.appendValueInput('B').setCheck('Number');
    this.setInputsInline(true);
    this.setOutput(true, 'Boolean');
  }}
}};

// -- Logical Operator --
Blockly.Blocks['ab_logic_op'] = {{
  init: function() {{
    this.setColour('#9c3a1a');
    this.appendValueInput('A').setCheck('Boolean');
    this.appendDummyInput().appendField(new Blockly.FieldDropdown([['AND (&&)', '&&'], ['OR (||)', '||']]), 'OP');
    this.appendValueInput('B').setCheck('Boolean');
    this.setInputsInline(true);
    this.setOutput(true, 'Boolean');
  }}
}};

// -- NOT --
Blockly.Blocks['ab_not'] = {{
  init: function() {{
    this.setColour('#9c3a1a');
    this.appendValueInput('BOOL').setCheck('Boolean').appendField("NOT");
    this.setInputsInline(true);
    this.setOutput(true, 'Boolean');
  }}
}};

// -- Boolean Literal --
Blockly.Blocks['ab_bool'] = {{
  init: function() {{
    this.setColour('#9c3a1a');
    this.appendDummyInput().appendField(new Blockly.FieldDropdown([['true','true'],['false','false']]), 'BOOL');
    this.setOutput(true, 'Boolean');
  }}
}};

// -- Global Variable Declaration --
Blockly.Blocks['ab_global_var'] = {{
  init: function() {{
    this.setColour('#c97a1e');
    this.appendDummyInput()
        .appendField("Global")
        .appendField(new Blockly.FieldDropdown([
          ['int','int'],['float','float'],['bool','bool'],
          ['String','String'],['long','long'],['byte','byte'],['char','char']
        ]), 'TYPE')
        .appendField(new Blockly.FieldTextInput('counter'), 'NAME');
    this.appendValueInput('VALUE')
        .setCheck(null)
        .appendField("=");
    this.setInputsInline(true);
    this.setTooltip("Create a global variable (accessible everywhere)");
  }}
}};

// -- Local Variable Declaration --
Blockly.Blocks['ab_local_var'] = {{
  init: function() {{
    this.setColour('#c97a1e');
    this.appendDummyInput()
        .appendField("Local")
        .appendField(new Blockly.FieldDropdown([
          ['int','int'],['float','float'],['bool','bool'],
          ['String','String'],['long','long'],['byte','byte'],['char','char']
        ]), 'TYPE')
        .appendField(new Blockly.FieldTextInput('counter'), 'NAME');
    this.appendValueInput('VALUE')
        .setCheck(null)
        .appendField("=");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip("Create a local variable (only accessible in this block)");
  }}
}};

// -- Set Variable --
Blockly.Blocks['ab_var_set'] = {{
  init: function() {{
    this.setColour('#c97a1e');
    this.appendValueInput('VALUE')
        .setCheck(null)
        .appendField(new Blockly.FieldTextInput('counter'), 'NAME')
        .appendField("=");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip("Change the value of an existing variable");
  }}
}};

// -- Get Variable --
Blockly.Blocks['ab_var_get'] = {{
  init: function() {{
    this.setColour('#c97a1e');
    this.appendDummyInput()
        .appendField(new Blockly.FieldTextInput('counter'), 'NAME');
    this.setOutput(true, null);
    this.setTooltip("Use the value of a variable");
  }}
}};

// -- Text --
Blockly.Blocks['ab_text'] = {{
  init: function() {{
    this.setColour('#1a5e20');
    this.appendDummyInput().appendField('"').appendField(new Blockly.FieldTextInput('Hello!'), 'TEXT').appendField('"');
    this.setOutput(true, 'String');
  }}
}};

// -- LED ON --
Blockly.Blocks['ab_led_on'] = {{
  init: function() {{
    this.setColour('#c97a00');
    this.appendDummyInput().appendField("Turn on LED pin").appendField(new Blockly.FieldDropdown([['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9'],['10','10'],['11','11'],['12','12'],['13','13']]), 'PIN');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- LED OFF --
Blockly.Blocks['ab_led_off'] = {{
  init: function() {{
    this.setColour('#c97a00');
    this.appendDummyInput().appendField("Turn off LED pin").appendField(new Blockly.FieldDropdown([['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9'],['10','10'],['11','11'],['12','12'],['13','13']]), 'PIN');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- PWM LED --
Blockly.Blocks['ab_pwm_set'] = {{
  init: function() {{
    this.setColour('#c97a00');
    this.appendValueInput('VAL').setCheck('Number').appendField("LED brightness pin").appendField(new Blockly.FieldDropdown([['3','3'],['5','5'],['6','6'],['9','9'],['10','10'],['11','11']]), 'PIN').appendField("= (0-255)");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- tone() --
Blockly.Blocks['ab_tone'] = {{
  init: function() {{
    this.setColour('#c97a00');
    this.appendValueInput('FREQ').setCheck('Number').appendField("Sound on pin").appendField(new Blockly.FieldDropdown([['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9']]), 'PIN').appendField("freq:");
    this.appendValueInput('DUR').setCheck('Number').appendField("for (ms)");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- noTone() --
Blockly.Blocks['ab_notone'] = {{
  init: function() {{
    this.setColour('#c97a00');
    this.appendDummyInput().appendField("Stop sound on pin").appendField(new Blockly.FieldDropdown([['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9']]), 'PIN');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- Servo.attach() --
Blockly.Blocks['ab_servo_attach'] = {{
  init: function() {{
    this.setColour('#9c1a1a');
    this.appendDummyInput().appendField("Connect servo").appendField(new Blockly.FieldTextInput('myServo'), 'OBJ').appendField("on pin").appendField(new Blockly.FieldDropdown([['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9'],['10','10'],['11','11']]), 'PIN');
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- Servo.write() --
Blockly.Blocks['ab_servo_write'] = {{
  init: function() {{
    this.setColour('#9c1a1a');
    this.appendValueInput('ANGLE').setCheck('Number').appendField("Move servo").appendField(new Blockly.FieldTextInput('myServo'), 'OBJ').appendField("to (degrees)");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
  }}
}};

// -- Servo.read() --
Blockly.Blocks['ab_servo_read'] = {{
  init: function() {{
    this.setColour('#9c1a1a');
    this.appendDummyInput().appendField("Read servo position").appendField(new Blockly.FieldTextInput('myServo'), 'OBJ');
    this.setOutput(true, 'Number');
  }}
}};

// -- HC-SR04 Ultrasonic --
Blockly.Blocks['ab_ultrasonic'] = {{
  init: function() {{
    this.setColour('#1a1a9c');
    this.appendDummyInput().appendField("Distance (cm) Trig:").appendField(new Blockly.FieldDropdown([['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9'],['10','10'],['11','11'],['12','12']]), 'TRIG').appendField("Echo:").appendField(new Blockly.FieldDropdown([['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9'],['10','10'],['11','11'],['12','12']]), 'ECHO');
    this.setOutput(true, 'Number');
  }}
}};

// -- DHT Sensor --
Blockly.Blocks['ab_dht'] = {{
  init: function() {{
    this.setColour('#1a1a9c');
    this.appendDummyInput().appendField("DHT Sensor pin").appendField(new Blockly.FieldDropdown([['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9']]), 'PIN').appendField(new Blockly.FieldDropdown([['DHT11','DHT11'],['DHT22','DHT22']]), 'TYPE').appendField(new Blockly.FieldDropdown([['temperature (C)','temperature'],['humidity (%)','humidity']]), 'WHAT');
    this.setOutput(true, 'Number');
  }}
}};

// -- LDR Sensor --
Blockly.Blocks['ab_ldr'] = {{
  init: function() {{
    this.setColour('#1a1a9c');
    this.appendDummyInput().appendField("Luminosity (LDR) pin").appendField(new Blockly.FieldDropdown([['A0','A0'],['A1','A1'],['A2','A2'],['A3','A3'],['A4','A4'],['A5','A5']]), 'PIN');
    this.setOutput(true, 'Number');
  }}
}};

// -- Button --
Blockly.Blocks['ab_button'] = {{
  init: function() {{
    this.setColour('#1a1a9c');
    this.appendDummyInput().appendField("Button pressed on pin").appendField(new Blockly.FieldDropdown([['2','2'],['3','3'],['4','4'],['5','5'],['6','6'],['7','7'],['8','8'],['9','9'],['10','10'],['11','11'],['12','12']]), 'PIN');
    this.setOutput(true, 'Boolean');
  }}
}};

// ============================================================
// ARDUINO CODE GENERATOR
// ============================================================
const ArduinoGen = new Blockly.Generator('Arduino');
ArduinoGen.ORDER_ATOMIC = 0;
ArduinoGen.ORDER_UNARY = 2;
ArduinoGen.ORDER_MULTIPLY = 3;
ArduinoGen.ORDER_ADD = 4;
ArduinoGen.ORDER_RELATIONAL = 6;
ArduinoGen.ORDER_EQUALITY = 7;
ArduinoGen.ORDER_AND = 11;
ArduinoGen.ORDER_OR = 12;
ArduinoGen.ORDER_NONE = 99;

ArduinoGen.scrub_ = function(block, code, thisOnly) {{
  const next = block.nextConnection && block.nextConnection.targetBlock();
  return code + (thisOnly ? '' : ArduinoGen.blockToCode(next));
}};

ArduinoGen._includes = {{}};
ArduinoGen._globals = {{}};
ArduinoGen._funcs = '';

function generateArduinoCode(ws) {{
  ArduinoGen._includes = {{}};
  ArduinoGen._globals = {{}};
  ArduinoGen._funcs = '';
  
  let setupCode = '';
  let loopCode = '';

  ws.getTopBlocks(true).forEach(b => {{
    if (b.type === 'ab_program') {{
      setupCode = ArduinoGen.statementToCode(b, 'SETUP');
      loopCode  = ArduinoGen.statementToCode(b, 'LOOP');
    }} else if (b.type === 'procedures_defnoreturn' || b.type === 'procedures_defreturn') {{
      ArduinoGen._funcs += ArduinoGen.blockToCode(b) + '\\n';
    }} else if (b.type === 'ab_global_var') {{
      ArduinoGen.blockToCode(b);
    }}
  }});

  const globalVars = Object.values(ArduinoGen._globals).filter(v => v.startsWith('int ') || v.startsWith('float ') || v.startsWith('bool ') || v.startsWith('String ') || v.startsWith('long ') || v.startsWith('byte ') || v.startsWith('char '));
  const otherGlobals = Object.values(ArduinoGen._globals).filter(v => !globalVars.includes(v));
  
  const inc = Object.values(ArduinoGen._includes).join('\\n');
  let out = '// Generated by ArduBlock Studio\\n\\n';
  if (inc) out += inc + '\\n\\n';
  if (globalVars.length) out += '// Global variables\\n' + globalVars.join('\\n') + '\\n\\n';
  if (otherGlobals.length) out += otherGlobals.join('\\n') + '\\n\\n';
  if (ArduinoGen._funcs) out += ArduinoGen._funcs + '\\n';
  out += 'void setup() {{\\n' + setupCode + '}}\\n\\n';
  out += 'void loop() {{\\n' + loopCode + '}}\\n';
  return out;
}}

function gen(type, fn) {{ ArduinoGen.forBlock[type] = fn; }}

gen('ab_program', (b, g) => '');
gen('ab_comment', (b, g) => `// ${{b.getFieldValue('TEXT')}}\\n`);
gen('procedures_defnoreturn', (b, g) => {{
  const name = b.getFieldValue('NAME');
  const body = g.statementToCode(b, 'STACK');
  let params = [];
  let i = 1;
  while (b.getFieldValue('TYPE' + i)) {{
    params.push(`${{b.getFieldValue('TYPE' + i)}} ${{b.getFieldValue('NAME' + i)}}`);
    i++;
  }}
  return `void ${{name}}(${{params.join(', ')}}) {{\\n${{body}}}}\\n`;
}});
gen('procedures_defreturn', (b, g) => {{
  const name = b.getFieldValue('NAME');
  const rettype = b.getFieldValue('RETTYPE');
  const body = g.statementToCode(b, 'STACK');
  let params = [];
  let i = 1;
  while (b.getFieldValue('TYPE' + i)) {{
    params.push(`${{b.getFieldValue('TYPE' + i)}} ${{b.getFieldValue('NAME' + i)}}`);
    i++;
  }}
  return `${{rettype}} ${{name}}(${{params.join(', ')}}) {{\\n${{body}}}}\\n`;
}});
gen('procedures_callnoreturn', (b, g) => {{
  const name = b.getFieldValue('NAME');
  let args = [];
  let i = 1;
  while (b.getInput('ARG' + i)) {{
    args.push(g.valueToCode(b, 'ARG' + i, g.ORDER_NONE) || '0');
    i++;
  }}
  return `${{name}}(${{args.join(', ')}});\\n`;
}});
gen('ab_return', (b, g) => {{
  const v = g.valueToCode(b, 'VAL', g.ORDER_NONE) || '';
  return `return${{v ? ' ' + v : ''}};\\n`;
}});
gen('ab_pin_mode', (b, g) => `pinMode(${{b.getFieldValue('PIN')}}, ${{b.getFieldValue('MODE')}});\\n`);
gen('ab_digital_write', (b, g) => `digitalWrite(${{b.getFieldValue('PIN')}}, ${{b.getFieldValue('STATE')}});\\n`);
gen('ab_digital_read', (b, g) => [`digitalRead(${{b.getFieldValue('PIN')}})`, g.ORDER_ATOMIC]);
gen('ab_analog_write', (b, g) => {{
  const val = g.valueToCode(b, 'VALUE', g.ORDER_NONE) || '0';
  return `analogWrite(${{b.getFieldValue('PIN')}}, ${{val}});\\n`;
}});
gen('ab_analog_read', (b, g) => [`analogRead(${{b.getFieldValue('PIN')}})`, g.ORDER_ATOMIC]);
gen('ab_delay_ms', (b, g) => `delay(${{g.valueToCode(b, 'MS', g.ORDER_NONE) || '1000'}});\\n`);
gen('ab_delay_sec', (b, g) => `delay((unsigned long)(${{g.valueToCode(b, 'SEC', g.ORDER_NONE) || '1'}}) * 1000UL);\\n`);
gen('ab_millis', (b, g) => [`millis()`, g.ORDER_ATOMIC]);
gen('ab_micros', (b, g) => [`micros()`, g.ORDER_ATOMIC]);
gen('ab_serial_begin', (b, g) => `Serial.begin(${{b.getFieldValue('BAUD')}});\\n`);
gen('ab_serial_print', (b, g) => `Serial.print(${{g.valueToCode(b, 'TEXT', g.ORDER_NONE) || '""'}});\\n`);
gen('ab_serial_println', (b, g) => `Serial.println(${{g.valueToCode(b, 'TEXT', g.ORDER_NONE) || '""'}});\\n`);
gen('ab_serial_available', (b, g) => [`Serial.available()`, g.ORDER_ATOMIC]);
gen('ab_serial_read', (b, g) => [`Serial.read()`, g.ORDER_ATOMIC]);
gen('controls_if', (b, g) => {{
  let code = `if (${{g.valueToCode(b, 'IF0', g.ORDER_NONE) || 'false'}}) {{\\n${{g.statementToCode(b, 'DO0')}}}}`;
  for (let i = 1; i <= (b.elseifCount_ || 0); i++) {{
    code += ` else if (${{g.valueToCode(b, 'IF' + i, g.ORDER_NONE) || 'false'}}) {{\\n${{g.statementToCode(b, 'DO' + i)}}}}`;
  }}
  if (b.elseCount_) code += ` else {{\\n${{g.statementToCode(b, 'ELSE')}}}}`;
  return code + '\\n';
}});
gen('ab_while', (b, g) => `while (${{g.valueToCode(b, 'COND', g.ORDER_NONE) || 'false'}}) {{\\n${{g.statementToCode(b, 'DO')}}}}\\n`);
gen('ab_for', (b, g) => {{
  const v = b.getFieldValue('VAR'), fr = b.getFieldValue('FROM'), to = b.getFieldValue('TO');
  const st = parseInt(b.getFieldValue('STEP')), d = g.statementToCode(b, 'DO');
  const op = st >= 0 ? '+=' : '-=';
  return `for (int ${{v}} = ${{fr}}; ${{v}} <= ${{to}}; ${{v}} ${{op}} ${{Math.abs(st)}}) {{\\n${{d}}}}\\n`;
}});
gen('ab_break', (b, g) => `break;\\n`);
gen('ab_number', (b, g) => [`${{b.getFieldValue('NUM')}}`, g.ORDER_ATOMIC]);
gen('ab_arithmetic', (b, g) => [`(${{g.valueToCode(b, 'A', g.ORDER_ADD) || '0'}} ${{b.getFieldValue('OP')}} ${{g.valueToCode(b, 'B', g.ORDER_ADD) || '0'}})`, g.ORDER_ADD]);
gen('ab_map', (b, g) => [`map(${{g.valueToCode(b, 'VAL', g.ORDER_NONE) || '0'}}, ${{g.valueToCode(b, 'FL', g.ORDER_NONE) || '0'}}, ${{g.valueToCode(b, 'FH', g.ORDER_NONE) || '1023'}}, ${{g.valueToCode(b, 'TL', g.ORDER_NONE) || '0'}}, ${{g.valueToCode(b, 'TH', g.ORDER_NONE) || '255'}})`, g.ORDER_ATOMIC]);
gen('ab_constrain', (b, g) => [`constrain(${{g.valueToCode(b, 'VAL', g.ORDER_NONE) || '0'}}, ${{g.valueToCode(b, 'LO', g.ORDER_NONE) || '0'}}, ${{g.valueToCode(b, 'HI', g.ORDER_NONE) || '255'}})`, g.ORDER_ATOMIC]);
gen('ab_random', (b, g) => [`random(${{g.valueToCode(b, 'MIN', g.ORDER_NONE) || '0'}}, ${{g.valueToCode(b, 'MAX', g.ORDER_NONE) || '100'}})`, g.ORDER_ATOMIC]);
gen('ab_abs', (b, g) => [`abs(${{g.valueToCode(b, 'VAL', g.ORDER_NONE) || '0'}})`, g.ORDER_ATOMIC]);
gen('ab_compare', (b, g) => [`(${{g.valueToCode(b, 'A', g.ORDER_RELATIONAL) || '0'}} ${{b.getFieldValue('OP')}} ${{g.valueToCode(b, 'B', g.ORDER_RELATIONAL) || '0'}})`, g.ORDER_EQUALITY]);
gen('ab_logic_op', (b, g) => {{
  const op = b.getFieldValue('OP');
  return [`(${{g.valueToCode(b, 'A', g.ORDER_AND) || 'false'}} ${{op}} ${{g.valueToCode(b, 'B', g.ORDER_AND) || 'false'}})`, op === '&&' ? g.ORDER_AND : g.ORDER_OR];
}});
gen('ab_not', (b, g) => [`!${{g.valueToCode(b, 'BOOL', g.ORDER_UNARY) || 'false'}}`, g.ORDER_UNARY]);
gen('ab_bool', (b, g) => [`${{b.getFieldValue('BOOL')}}`, g.ORDER_ATOMIC]);
gen('ab_global_var', (b, g) => {{
  const type = b.getFieldValue('TYPE');
  const name = b.getFieldValue('NAME');
  const value = g.valueToCode(b, 'VALUE', g.ORDER_NONE) || '0';
  ArduinoGen._globals[`global_${{name}}`] = `${{type}} ${{name}} = ${{value}};`;
  return '';
}});
gen('ab_local_var', (b, g) => {{
  const type = b.getFieldValue('TYPE');
  const name = b.getFieldValue('NAME');
  const value = g.valueToCode(b, 'VALUE', g.ORDER_NONE) || '0';
  return `${{type}} ${{name}} = ${{value}};\\n`;
}});
gen('ab_var_set', (b, g) => {{
  const name = b.getFieldValue('NAME');
  const value = g.valueToCode(b, 'VALUE', g.ORDER_NONE) || '0';
  return `${{name}} = ${{value}};\\n`;
}});
gen('ab_var_get', (b, g) => {{
  return [`${{b.getFieldValue('NAME')}}`, g.ORDER_ATOMIC];
}});
gen('ab_text', (b, g) => [`"${{b.getFieldValue('TEXT')}}"`, g.ORDER_ATOMIC]);
gen('ab_led_on', (b, g) => `digitalWrite(${{b.getFieldValue('PIN')}}, HIGH);\\n`);
gen('ab_led_off', (b, g) => `digitalWrite(${{b.getFieldValue('PIN')}}, LOW);\\n`);
gen('ab_pwm_set', (b, g) => `analogWrite(${{b.getFieldValue('PIN')}}, ${{g.valueToCode(b, 'VAL', g.ORDER_NONE) || '0'}});\\n`);
gen('ab_tone', (b, g) => `tone(${{b.getFieldValue('PIN')}}, ${{g.valueToCode(b, 'FREQ', g.ORDER_NONE) || '440'}}, ${{g.valueToCode(b, 'DUR', g.ORDER_NONE) || '500'}});\\n`);
gen('ab_notone', (b, g) => `noTone(${{b.getFieldValue('PIN')}});\\n`);
gen('ab_servo_attach', (b, g) => {{
  const obj = b.getFieldValue('OBJ');
  ArduinoGen._includes['servo'] = '#include <Servo.h>';
  ArduinoGen._globals[`servo_${{obj}}`] = `Servo ${{obj}};`;
  return `${{obj}}.attach(${{b.getFieldValue('PIN')}});\\n`;
}});
gen('ab_servo_write', (b, g) => `${{b.getFieldValue('OBJ')}}.write(${{g.valueToCode(b, 'ANGLE', g.ORDER_NONE) || '90'}});\\n`);
gen('ab_servo_read', (b, g) => [`${{b.getFieldValue('OBJ')}}.read()`, g.ORDER_ATOMIC]);
gen('ab_ultrasonic', (b, g) => {{
  ArduinoGen._globals['ult_func'] = `float ultrasonicCM(int trig, int echo) {{\\n  pinMode(trig, OUTPUT);\\n  digitalWrite(trig, LOW); delayMicroseconds(2);\\n  digitalWrite(trig, HIGH); delayMicroseconds(10);\\n  digitalWrite(trig, LOW);\\n  return pulseIn(echo, HIGH) * 0.034 / 2.0;\\n}}`;
  return [`ultrasonicCM(${{b.getFieldValue('TRIG')}}, ${{b.getFieldValue('ECHO')}})`, g.ORDER_ATOMIC];
}});
gen('ab_dht', (b, g) => {{
  const pin = b.getFieldValue('PIN'), type = b.getFieldValue('TYPE'), what = b.getFieldValue('WHAT');
  ArduinoGen._includes['dht'] = '#include <DHT.h>';
  ArduinoGen._globals[`dht_${{pin}}`] = `DHT dht${{pin}}(${{pin}}, ${{type}});`;
  return [`dht${{pin}}.${{what === 'temperature' ? 'readTemperature()' : 'readHumidity()'}}`, g.ORDER_ATOMIC];
}});
gen('ab_ldr', (b, g) => [`analogRead(${{b.getFieldValue('PIN')}})`, g.ORDER_ATOMIC]);
gen('ab_button', (b, g) => [`(digitalRead(${{b.getFieldValue('PIN')}}) == LOW)`, g.ORDER_ATOMIC]);

function xmlTextToDom(text) {{
  if (Blockly.utils && Blockly.utils.xml && Blockly.utils.xml.textToDom) return Blockly.utils.xml.textToDom(text);
  return Blockly.Xml.textToDom(text);
}}
function xmlDomToText(dom) {{
  if (Blockly.utils && Blockly.utils.xml && Blockly.utils.xml.domToText) return Blockly.utils.xml.domToText(dom);
  return Blockly.Xml.domToText(dom);
}}

// ============================================================
// EXAMPLES
// ============================================================
const EXAMPLES = {{
  blink: `<xml><block type="ab_program" x="30" y="20"><statement name="SETUP"><block type="ab_pin_mode"><field name="PIN">13</field><field name="MODE">OUTPUT</field></block></statement><statement name="LOOP"><block type="ab_led_on"><field name="PIN">13</field><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">1000</field></shadow></value><next><block type="ab_led_off"><field name="PIN">13</field><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">1000</field></shadow></value></block></next></block></next></block></next></block></statement></block></xml>`,
  traffic: `<xml><block type="ab_program" x="30" y="20"><statement name="SETUP"><block type="ab_pin_mode"><field name="PIN">12</field><field name="MODE">OUTPUT</field><next><block type="ab_pin_mode"><field name="PIN">11</field><field name="MODE">OUTPUT</field><next><block type="ab_pin_mode"><field name="PIN">10</field><field name="MODE">OUTPUT</field></block></next></block></next></block></statement><statement name="LOOP"><block type="ab_digital_write"><field name="PIN">12</field><field name="STATE">HIGH</field><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">5000</field></shadow></value><next><block type="ab_digital_write"><field name="PIN">12</field><field name="STATE">LOW</field><next><block type="ab_digital_write"><field name="PIN">11</field><field name="STATE">HIGH</field><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">2000</field></shadow></value><next><block type="ab_digital_write"><field name="PIN">11</field><field name="STATE">LOW</field><next><block type="ab_digital_write"><field name="PIN">10</field><field name="STATE">HIGH</field><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">5000</field></shadow></value><next><block type="ab_digital_write"><field name="PIN">10</field><field name="STATE">LOW</field><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">1000</field></shadow></value></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></next></block></statement></block></xml>`,
  serial: `<xml><block type="ab_program" x="30" y="20"><statement name="SETUP"><block type="ab_serial_begin"><field name="BAUD">9600</field></block></statement><statement name="LOOP"><block type="ab_serial_println"><value name="TEXT"><block type="ab_text"><field name="TEXT">Hello, ArduBlock Studio!</field></block></value><next><block type="ab_delay_sec"><value name="SEC"><shadow type="ab_number"><field name="NUM">1</field></shadow></value></block></next></block></statement></block></xml>`,
  servo: `<xml><block type="ab_program" x="30" y="20"><statement name="SETUP"><block type="ab_servo_attach"><field name="OBJ">myServo</field><field name="PIN">9</field></block></statement><statement name="LOOP"><block type="ab_servo_write"><field name="OBJ">myServo</field><value name="ANGLE"><block type="ab_number"><field name="NUM">0</field></block></value><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">1000</field></shadow></value><next><block type="ab_servo_write"><field name="OBJ">myServo</field><value name="ANGLE"><block type="ab_number"><field name="NUM">90</field></block></value><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">1000</field></shadow></value><next><block type="ab_servo_write"><field name="OBJ">myServo</field><value name="ANGLE"><block type="ab_number"><field name="NUM">180</field></block></value><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">1000</field></shadow></value></block></next></block></next></block></next></block></next></block></next></block></statement></block></xml>`,
  ultrasonic: `<xml><block type="ab_program" x="30" y="20"><statement name="SETUP"><block type="ab_serial_begin"><field name="BAUD">9600</field></block></statement><statement name="LOOP"><block type="ab_local_var"><field name="TYPE">float</field><field name="NAME">distance</field><value name="VALUE"><block type="ab_ultrasonic"><field name="TRIG">9</field><field name="ECHO">10</field></block></value><next><block type="ab_serial_print"><value name="TEXT"><block type="ab_text"><field name="TEXT">Distance: </field></block></value><next><block type="ab_serial_print"><value name="TEXT"><block type="ab_var_get"><field name="NAME">distance</field></block></value><next><block type="ab_serial_println"><value name="TEXT"><block type="ab_text"><field name="TEXT"> cm</field></block></value><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">500</field></shadow></value></block></next></block></next></block></next></block></next></block></statement></block></xml>`,
  analog: `<xml><block type="ab_program" x="30" y="20"><statement name="SETUP"><block type="ab_serial_begin"><field name="BAUD">9600</field></block></statement><statement name="LOOP"><block type="ab_local_var"><field name="TYPE">int</field><field name="NAME">reading</field><value name="VALUE"><block type="ab_analog_read"><field name="PIN">A0</field></block></value><next><block type="ab_serial_print"><value name="TEXT"><block type="ab_text"><field name="TEXT">Sensor A0: </field></block></value><next><block type="ab_serial_println"><value name="TEXT"><block type="ab_var_get"><field name="NAME">reading</field></block></value><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">200</field></shadow></value></block></next></block></next></block></next></block></statement></block></xml>`,
  pwm: `<xml><block type="ab_program" x="30" y="20"><statement name="LOOP"><block type="ab_for"><field name="VAR">b</field><field name="FROM">0</field><field name="TO">255</field><field name="STEP">5</field><statement name="DO"><block type="ab_pwm_set"><field name="PIN">9</field><value name="VAL"><block type="ab_var_get"><field name="NAME">b</field></block></value><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">20</field></shadow></value></block></next></block></statement><next><block type="ab_for"><field name="VAR">b</field><field name="FROM">255</field><field name="TO">0</field><field name="STEP">-5</field><statement name="DO"><block type="ab_pwm_set"><field name="PIN">9</field><value name="VAL"><block type="ab_var_get"><field name="NAME">b</field></block></value><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">20</field></shadow></value></block></next></block></statement></block></next></block></statement></block></xml>`,
  tone: `<xml><block type="ab_program" x="30" y="20"><statement name="LOOP"><block type="ab_tone"><field name="PIN">8</field><value name="FREQ"><block type="ab_number"><field name="NUM">262</field></block></value><value name="DUR"><block type="ab_number"><field name="NUM">400</field></block></value><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">500</field></shadow></value><next><block type="ab_tone"><field name="PIN">8</field><value name="FREQ"><block type="ab_number"><field name="NUM">330</field></block></value><value name="DUR"><block type="ab_number"><field name="NUM">400</field></block></value><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">500</field></shadow></value><next><block type="ab_tone"><field name="PIN">8</field><value name="FREQ"><block type="ab_number"><field name="NUM">392</field></block></value><value name="DUR"><block type="ab_number"><field name="NUM">800</field></block></value><next><block type="ab_delay_ms"><value name="MS"><shadow type="ab_number"><field name="NUM">1000</field></shadow></value></block></next></block></next></block></next></block></next></block></statement></block></xml>`,
}};

// ============================================================
// BLOCKLY THEME & INIT
// ============================================================
const arduinoTheme = Blockly.Theme.defineTheme('ardublock', {{
  base: Blockly.Themes.Classic,
  componentStyles: {{
    workspaceBackgroundColour: '#0f1729', toolboxBackgroundColour: '#080d1a',
    toolboxForegroundColour: '#d8eaff', flyoutBackgroundColour: '#0f1729',
    flyoutForegroundColour: '#d8eaff', flyoutOpacity: 1,
    scrollbarColour: '#1e3058', scrollbarOpacity: 0.6,
    insertionMarkerColour: '#00d2ff', insertionMarkerOpacity: 0.5,
    cursorColour: '#00ff88',
  }},
  fontStyle: {{ family: 'Nunito', weight: 'bold', size: 12 }},
}});

function initBlockly() {{
  workspace = Blockly.inject('blocklyDiv', {{
    toolbox: document.getElementById('toolbox'), theme: arduinoTheme,
    renderer: 'zelos',
    grid: {{ spacing: 24, length: 3, colour: '#141f38', snap: true }},
    zoom: {{ controls: true, wheel: true, startScale: 0.95, maxScale: 3, minScale: 0.3, scaleSpeed: 1.2 }},
    trashcan: true, scrollbars: true, sounds: false,
    move: {{ scrollbars: true, drag: true, wheel: true }},
  }});
  workspace.addChangeListener(e => {{
    if (e.isUiEvent) return;
    clearTimeout(codeUpdateTimer);
    codeUpdateTimer = setTimeout(updateCode, 200);
    updateBlockCount();
  }});
  loadExample('blink');
  updateCode();
  log('ArduBlock Studio ready!', 'ok');
}}

function updateCode() {{
  try {{
    const code = generateArduinoCode(workspace);
    document.getElementById('code-view').textContent = code;
    document.getElementById('code-lines').textContent = code.split('\\n').length + ' lines';
  }} catch(e) {{ console.error(e); }}
}}

function getGeneratedCode() {{ return generateArduinoCode(workspace); }}

function updateBlockCount() {{
  document.getElementById('blockCount').textContent = workspace.getAllBlocks(false).length + ' blocks';
}}

// ============================================================
// BRIDGE INITIALIZATION
// ============================================================
function initBridge() {{
  if (typeof QWebChannel === 'undefined') {{
    log('Running without Qt bridge (browser mode)', 'warn');
    document.getElementById('cliVer').textContent = 'CLI: browser';
    allBoards = [
      {{"name":"Arduino UNO R3","fqbn":"arduino:avr:uno","family":"UNO"}},
      {{"name":"Arduino UNO R4 WiFi","fqbn":"arduino:renesas_uno:unor4wifi","family":"UNO"}},
      {{"name":"Arduino Nano","fqbn":"arduino:avr:nano","family":"Nano"}},
      {{"name":"Arduino Mega 2560","fqbn":"arduino:avr:mega","family":"Mega"}},
    ];
    initBlockly();
    populateBoardSelect();
    hideLoading();
    document.getElementById('btnLangEN').classList.add('active');
    return;
  }}

  new QWebChannel(qt.webChannelTransport, ch => {{
    pyBridge = ch.objects.bridge;
    
    if (pyBridge.boardsDetected) pyBridge.boardsDetected.connect(onBoardsDetected);
    if (pyBridge.compileResult) pyBridge.compileResult.connect(onCompileResult);
    if (pyBridge.uploadResult) pyBridge.uploadResult.connect(onUploadResult);
    if (pyBridge.logMsg) pyBridge.logMsg.connect(msg => log(msg, 'step'));
    if (pyBridge.languageChanged) pyBridge.languageChanged.connect(updateTranslations);
    
    pyBridge.getCLIVersion(ver => {{
      document.getElementById('cliVer').textContent = `CLI: ${{ver}}`;
      const d = document.getElementById('cliDot'), s = document.getElementById('cliStatus');
      if (ver && ver !== 'Not installed') {{ 
        d.classList.add('ok'); 
        s.textContent = `arduino-cli ${{ver}}`; 
      }} else {{ 
        d.classList.add('err'); 
        s.textContent = 'arduino-cli not found'; 
      }}
      
      pyBridge.getAllBoards(raw => {{
        try {{ allBoards = JSON.parse(raw); }} catch(e) {{ allBoards = []; }}
        populateBoardSelect();
        initBlockly();
        detectBoards();
        hideLoading();
        document.getElementById('btnLangEN').classList.add('active');
        currentLanguage = 'en';
        
        // Get initial translations
        if (pyBridge && typeof pyBridge.getTranslations === 'function') {{
          pyBridge.getTranslations(translationsJson => {{
            if (translationsJson) updateTranslations(translationsJson);
          }});
        }}
      }});
    }});
  }});
}}

function populateBoardSelect() {{
  const sel = document.getElementById('boardSelect');
  sel.innerHTML = '';
  const families = {{}};
  allBoards.forEach(b => {{ if (!families[b.family]) families[b.family] = []; families[b.family].push(b); }});
  Object.entries(families).forEach(([fam, bds]) => {{
    const grp = document.createElement('optgroup');
    grp.label = '-- ' + fam + ' --';
    bds.forEach(b => {{
      const opt = document.createElement('option');
      opt.value = b.fqbn; opt.textContent = b.name;
      if (b.fqbn === 'arduino:avr:uno') opt.selected = true;
      grp.appendChild(opt);
    }});
    sel.appendChild(grp);
  }});
}}

function onBoardChange() {{ currentFQBN = document.getElementById('boardSelect').value; }}

function detectBoards() {{
  if (!pyBridge) return;
  document.getElementById('boardDot').className = 'dot blink';
  pyBridge.detectBoards();
}}

loadProgrammers();

function onBoardsDetected(json) {{
  connectedBoards = JSON.parse(json);
  const ps = document.getElementById('portSelect');
  ps.innerHTML = '<option value="">-- Select port --</option>';
  const dot = document.getElementById('boardDot');
  const st = document.getElementById('boardStatus');
  dot.className = 'dot';
  
  if (!connectedBoards.length) {{ 
    st.textContent = 'No board';
    dot.classList.add('err');
    
    // ========== MENSAGENS DE DIAGNÓSTICO ==========
    log('⚠️ No Arduino board detected!', 'warn');
    log('💡 Troubleshooting:', 'info');
    
    var os = navigator.platform || '';
    if (os.indexOf('Win') !== -1) {{
      log('  [Windows] Check Device Manager > Ports (COM & LPT)', 'info');
      log('  [Windows] Install CH340 driver: wch.cn/downloads/CH341SER_EXE.html', 'info');
      log('  [Windows] Use a DATA USB cable (not charge-only)', 'info');
      log('  [Windows] Try USB 2.0 port (black, not blue)', 'info');
    }} else if (os.indexOf('Linux') !== -1) {{
      log('  [Linux] Run: ls -la /dev/ttyUSB* /dev/ttyACM*', 'info');
      log('  [Linux] Run: sudo usermod -aG dialout $USER', 'info');
      log('  [Linux] Logout and login after adding to dialout group', 'info');
    }} else if (os.indexOf('Mac') !== -1) {{
      log('  [macOS] Run: ls -la /dev/cu.* /dev/tty.*', 'info');
      log('  [macOS] Install CH340 driver for macOS', 'info');
    }}
    log('  Use a DATA USB cable (not charge-only)', 'info');
    log('  Test with Arduino IDE first to verify board works', 'info');
    // ==============================================
    
    return;
  }}
  
  dot.classList.add('ok');
  st.textContent = connectedBoards.length + ' board(s)';
  connectedBoards.forEach(b => {{
    const opt = document.createElement('option');
    opt.value = b.port;
    opt.textContent = b.port + ' -- ' + b.name;
    ps.appendChild(opt);
    if (b.fqbn) {{
      const bs = document.getElementById('boardSelect');
      for (let o of bs.options) {{
        if (o.value === b.fqbn) {{
          o.selected = true;
          currentFQBN = b.fqbn;
          break;
        }}
      }}
    }}
  }});
}}

function doCompile() {{
  if (!pyBridge) return;
  const fqbn = document.getElementById('boardSelect').value;
  if (!fqbn) {{ log('Select a board!', 'err'); return; }}
  pyBridge.compile(getGeneratedCode(), fqbn);
}}

function onCompileResult(json) {{
  const r = JSON.parse(json);
  if (r.ok) {{ log('Compilation successful!', 'ok'); document.getElementById('cliDot').className = 'dot ok'; }}
  else {{ r.msg.split('\\n').filter(l=>l.trim()).forEach(l => log(l, 'err')); }}
}}

function doUpload() {{
  if (!pyBridge) return;
  const fqbn = document.getElementById('boardSelect').value;
  const port = document.getElementById('portSelect').value;
  if (!fqbn || !port) {{ log('Select board and port!', 'err'); return; }}
  pyBridge.upload(getGeneratedCode(), fqbn, port);
}}

function onUploadResult(json) {{
  const r = JSON.parse(json);
  if (r.ok) log('Upload successful!', 'ok');
  else {{
    let errMsg = r.msg || '';
    errMsg.split('\\n').filter(l=>l.trim()).forEach(l => log(l, 'err'));
  }}
}}

function openSerial() {{
  const port = document.getElementById('portSelect').value;
  if (!port) {{ log('Select port first!', 'err'); return; }}
  if (pyBridge) pyBridge.openSerial(port);
}}

function newProject() {{ if (confirm('Create new project? All unsaved work will be lost!')) {{ workspace.clear(); log('New project created!', 'ok'); }} }}
function saveProject() {{ const xml = xmlDomToText(Blockly.Xml.workspaceToDom(workspace)); if (pyBridge) pyBridge.saveWorkspace(xml); }}
function loadProject() {{ if (pyBridge) pyBridge.loadWorkspace(xml => {{ if (xml) {{ workspace.clear(); Blockly.Xml.domToWorkspace(xmlTextToDom(xml), workspace); log('Project loaded!', 'ok'); }} }}); }}

function loadExample(name) {{
  const xml = EXAMPLES[name];
  if (!xml) return;
  workspace.clear();
  Blockly.Xml.domToWorkspace(xmlTextToDom(xml), workspace);
  workspace.scrollCenter();
  log('Example loaded: ' + name, 'ok');
}}

function log(msg, type='info') {{
  const el = document.getElementById('log');
  const line = document.createElement('div');
  line.className = 'log-line log-' + type;
  line.textContent = `[${{new Date().toLocaleTimeString('en-US', {{hour:'2-digit',minute:'2-digit',second:'2-digit'}})}}] ${{msg}}`;
  el.appendChild(line);
  el.scrollTop = el.scrollHeight;
}}

function clearLog() {{ document.getElementById('log').innerHTML = ''; }}
function hideLoading() {{ const ld = document.getElementById('loading'); ld.style.transition = 'opacity 0.5s'; ld.style.opacity = '0'; setTimeout(() => ld.style.display = 'none', 500); }}

function openExtensionManager() {{
    if (pyBridge && typeof pyBridge.openExtensionManager === 'function') {{
        pyBridge.openExtensionManager();
    }}
}}

// Adicionar botão na toolbar
var extBtn = document.createElement('button');
extBtn.className = 'btn btn-serial';
extBtn.innerHTML = '<span class="material-icons">extension</span> Extensions';
extBtn.onclick = openExtensionManager;

window.addEventListener('DOMContentLoaded', () => {{
  initBridge();
  new ResizeObserver(() => {{ if (workspace) Blockly.svgResize(workspace); }}).observe(document.getElementById('blockly-wrap'));
}});
</script>
</body>
</html>'''
