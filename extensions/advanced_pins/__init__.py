"""
Advanced Pins Extension
=======================
Pinos Digitais e Analógicos com suporte a variáveis (pino como expressão).

CHANGELOG (fixes):
- Removidas chamadas manuais a workspace.updateToolbox() por bloco/categoria.
- setInputsInline(true) ativado automaticamente pela API para blocos inline.
- check=null agora é passado corretamente para Blockly.setCheck(null).
- Traduções em lote (uma única injeção JS).
"""

DIGITAL_COLOUR = "#1a5eb5"
ANALOG_COLOUR  = "#0a7a6e"


def initialize(api):
    """Inicializa a extensão de pinos avançados."""
    print("[Advanced Pins] Initializing...")

    # ------------------------------------------------------------------
    # 1. FUNÇÕES AUXILIARES ARDUINO
    # ------------------------------------------------------------------

    api.add_global_function("is_pwm_pin", """
bool isPwmPin(int pin) {
    // ATmega328P (UNO/Nano) and ATmega2560 (Mega)
    #if defined(__AVR_ATmega328P__)
    int pwmPins[] = {3, 5, 6, 9, 10, 11};
    for (int i = 0; i < 6; i++) { if (pin == pwmPins[i]) return true; }
    #elif defined(__AVR_ATmega2560__)
    int pwmPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 44, 45, 46};
    for (int i = 0; i < 15; i++) { if (pin == pwmPins[i]) return true; }
    #endif
    return false;
}""")

    api.add_global_function("pin_to_string", """
String pinToString(int pin) {
    if (pin >= A0 && pin <= A5) {
        return "A" + String(pin - A0);
    }
    return "D" + String(pin);
}""")

    # ------------------------------------------------------------------
    # 2. CATEGORIAS
    # ------------------------------------------------------------------

    api.add_category("Digital Pins", "Dynamic", DIGITAL_COLOUR, "settings")
    api.add_category("Analog Pins",  "Dynamic", ANALOG_COLOUR,  "settings")

    # ------------------------------------------------------------------
    # 3. BLOCOS DIGITAIS
    # ------------------------------------------------------------------

    api.add_block(
        name="ab_pin_mode_var",
        block_type="statement",
        category="Digital Pins",
        subcategory="Dynamic",
        colour=DIGITAL_COLOUR,
        inputs=[
            {"name": "PIN",  "type": "value", "label": "pin",  "check": "Number"},
            {"name": "MODE", "type": "field",  "label": "mode",
             "options": ["OUTPUT", "INPUT", "INPUT_PULLUP"]},
        ],
        tooltip={"en": "Set pin mode using a variable or expression",
                 "pt": "Define o modo de um pino via variável ou expressão"},
        inline=True,
    )
    api.add_generator("ab_pin_mode_var", """function(block, gen) {
        var pin  = gen.valueToCode(block, 'PIN', gen.ORDER_NONE) || '0';
        var mode = block.getFieldValue('MODE');
        return 'pinMode(' + pin + ', ' + mode + ');\\n';
    }""")

    api.add_block(
        name="ab_digital_write_var",
        block_type="statement",
        category="Digital Pins",
        subcategory="Dynamic",
        colour=DIGITAL_COLOUR,
        inputs=[
            {"name": "PIN",   "type": "value", "label": "pin",   "check": "Number"},
            {"name": "STATE", "type": "field",  "label": "value",
             "options": ["HIGH", "LOW"]},
        ],
        tooltip={"en": "Write digital value to pin (variable)",
                 "pt": "Escreve valor digital em pino (variável)"},
        inline=True,
    )
    api.add_generator("ab_digital_write_var", """function(block, gen) {
        var pin   = gen.valueToCode(block, 'PIN', gen.ORDER_NONE) || '0';
        var state = block.getFieldValue('STATE');
        return 'digitalWrite(' + pin + ', ' + state + ');\\n';
    }""")

    api.add_block(
        name="ab_digital_read_var",
        block_type="value",
        category="Digital Pins",
        subcategory="Dynamic",
        colour=DIGITAL_COLOUR,
        inputs=[{"name": "PIN", "type": "value", "label": "read pin", "check": "Number"}],
        tooltip={"en": "Read digital value from pin (variable)",
                 "pt": "Lê valor digital de pino (variável)"},
        inline=True,
    )
    api.add_generator("ab_digital_read_var", """function(block, gen) {
        var pin = gen.valueToCode(block, 'PIN', gen.ORDER_NONE) || '0';
        return ['digitalRead(' + pin + ')', gen.ORDER_ATOMIC];
    }""")

    api.add_block(
        name="ab_pin_to_string",
        block_type="value",
        category="Digital Pins",
        subcategory="Dynamic",
        colour=DIGITAL_COLOUR,
        inputs=[{"name": "PIN", "type": "value", "label": "pin name", "check": "Number"}],
        tooltip={"en": "Get pin name string (e.g. 'D13', 'A0')",
                 "pt": "Retorna nome do pino como string (ex: 'D13', 'A0')"},
        inline=True,
    )
    api.add_generator("ab_pin_to_string", """function(block, gen) {
        var pin = gen.valueToCode(block, 'PIN', gen.ORDER_NONE) || '0';
        return ['pinToString(' + pin + ')', gen.ORDER_ATOMIC];
    }""")

    # ------------------------------------------------------------------
    # 4. BLOCOS ANALÓGICOS
    # ------------------------------------------------------------------

    api.add_block(
        name="ab_analog_write_var",
        block_type="statement",
        category="Analog Pins",
        subcategory="Dynamic",
        colour=ANALOG_COLOUR,
        inputs=[
            {"name": "PIN",   "type": "value", "label": "PWM pin", "check": "Number"},
            {"name": "VALUE", "type": "value", "label": "=",       "check": "Number"},
        ],
        tooltip={"en": "Write PWM value to pin (0-255), pin as variable",
                 "pt": "Escreve valor PWM em pino (0-255), pino como variável"},
        inline=True,
    )
    api.add_generator("ab_analog_write_var", """function(block, gen) {
        var pin = gen.valueToCode(block, 'PIN',   gen.ORDER_NONE) || '0';
        var val = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
        return 'analogWrite(' + pin + ', ' + val + ');\\n';
    }""")

    api.add_block(
        name="ab_analog_read_var",
        block_type="value",
        category="Analog Pins",
        subcategory="Dynamic",
        colour=ANALOG_COLOUR,
        inputs=[{"name": "PIN", "type": "value", "label": "read analog pin", "check": "Number"}],
        tooltip={"en": "Read analog value (0-1023), pin as variable",
                 "pt": "Lê valor analógico (0-1023), pino como variável"},
        inline=True,
    )
    api.add_generator("ab_analog_read_var", """function(block, gen) {
        var pin = gen.valueToCode(block, 'PIN', gen.ORDER_NONE) || '0';
        return ['analogRead(' + pin + ')', gen.ORDER_ATOMIC];
    }""")

    api.add_block(
        name="ab_is_pwm_pin",
        block_type="value",
        category="Analog Pins",
        subcategory="Dynamic",
        colour=ANALOG_COLOUR,
        inputs=[{"name": "PIN", "type": "value", "label": "is PWM pin?", "check": "Number"}],
        tooltip={"en": "Check if pin supports PWM output",
                 "pt": "Verifica se o pino suporta saída PWM"},
        inline=True,
    )
    api.add_generator("ab_is_pwm_pin", """function(block, gen) {
        var pin = gen.valueToCode(block, 'PIN', gen.ORDER_NONE) || '0';
        return ['isPwmPin(' + pin + ')', gen.ORDER_ATOMIC];
    }""")

    # ------------------------------------------------------------------
    # 5. TRADUÇÕES EM LOTE
    # ------------------------------------------------------------------

    api.add_translations({
        "en": {
            "ab_pin_mode_var_tooltip":      "Set pin mode (variable)",
            "ab_digital_write_var_tooltip": "Write digital (variable pin)",
            "ab_digital_read_var_tooltip":  "Read digital (variable pin)",
            "ab_pin_to_string_tooltip":     "Pin name as string",
            "ab_analog_write_var_tooltip":  "Write PWM (variable pin)",
            "ab_analog_read_var_tooltip":   "Read analog (variable pin)",
            "ab_is_pwm_pin_tooltip":        "Pin supports PWM?",
        },
        "pt": {
            "ab_pin_mode_var_tooltip":      "Define modo do pino (variável)",
            "ab_digital_write_var_tooltip": "Escreve digital (pino variável)",
            "ab_digital_read_var_tooltip":  "Lê digital (pino variável)",
            "ab_pin_to_string_tooltip":     "Nome do pino como string",
            "ab_analog_write_var_tooltip":  "Escreve PWM (pino variável)",
            "ab_analog_read_var_tooltip":   "Lê analógico (pino variável)",
            "ab_is_pwm_pin_tooltip":        "Pino suporta PWM?",
        },
    })

    api.add_status_message("Advanced Pins loaded (7 blocks)", "ok")
    print("[Advanced Pins] Extension initialized successfully!")
    return True