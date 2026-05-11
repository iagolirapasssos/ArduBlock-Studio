"""
Advanced Logic Extension
========================
Lógica Avançada: comparação de strings, operações com caracteres e
operadores lógicos avançados para Arduino.

CHANGELOG (fixes):
- Removidas chamadas manuais a workspace.updateToolbox() por bloco/categoria.
  O manager agora faz isso UMA ÚNICA VEZ depois do flush().
- Bloco ab_text foi marcado com inline=True para ficar igual aos nativos.
- setInputsInline é controlado automaticamente pela API para blocos simples.
- Removido o bloco duplicado 'ab_text' que conflitava com o bloco nativo
  de mesmo nome (cor diferente causava inconsistência visual).
"""

EXT_COLOUR = "#9c3a1a"


def initialize(api):
    """Inicializa a extensão de lógica avançada."""
    print("[Advanced Logic] Initializing...")

    # ------------------------------------------------------------------
    # 1. FUNÇÕES AUXILIARES ARDUINO (injetadas no código gerado)
    # ------------------------------------------------------------------

    api.add_global_function("string_equals_ignore_case", """
bool stringEqualsIgnoreCase(const String& s1, const String& s2) {
    if (s1.length() != s2.length()) return false;
    for (unsigned int i = 0; i < s1.length(); i++) {
        if (tolower(s1[i]) != tolower(s2[i])) return false;
    }
    return true;
}""")

    api.add_global_function("string_contains", """
bool stringContains(const String& str, const String& substr) {
    return str.indexOf(substr) != -1;
}""")

    api.add_global_function("is_numeric_func", """
bool isNumeric(const String& str) {
    if (str.length() == 0) return false;
    for (unsigned int i = 0; i < str.length(); i++) {
        if (i == 0 && str[i] == '-') continue;
        if (!isDigit(str[i])) return false;
    }
    return true;
}""")

    # ------------------------------------------------------------------
    # 2. CATEGORIAS
    # ------------------------------------------------------------------

    api.add_category("Logic", "Text",     EXT_COLOUR, "text_fields")
    api.add_category("Logic", "Char",     EXT_COLOUR, "abc")
    api.add_category("Logic", "Advanced", EXT_COLOUR, "toggle_on")

    # ------------------------------------------------------------------
    # 3. BLOCOS – TEXT (String)
    # ------------------------------------------------------------------

    # ab_text_literal: string literal (renomeado para evitar conflito com
    # o bloco nativo ab_text que tem cor diferente)
    api.add_block(
        name="ab_text_literal",
        block_type="value",
        category="Logic",
        subcategory="Text",
        colour=EXT_COLOUR,
        inputs=[{"name": "TEXT", "type": "field", "label": '""', "default": "text"}],
        tooltip={"en": "A text string value", "pt": "Um valor de texto (string)"},
        inline=True,
    )
    api.add_generator("ab_text_literal", """function(block, gen) {
        var text = block.getFieldValue('TEXT');
        return ['"' + text.replace(/"/g, '\\\\"') + '"', gen.ORDER_ATOMIC];
    }""")

    # Equals
    api.add_block(
        name="ab_text_equals",
        block_type="value",
        category="Logic",
        subcategory="Text",
        colour=EXT_COLOUR,
        inputs=[
            {"name": "A", "type": "value", "label": "",  "check": "String"},
            {"name": "B", "type": "value", "label": "=", "check": "String"},
        ],
        tooltip={"en": "Compare two strings (case-sensitive)", "pt": "Compara duas strings"},
        inline=True,
    )
    api.add_generator("ab_text_equals", """function(block, gen) {
        var a = gen.valueToCode(block, 'A', gen.ORDER_NONE) || '""';
        var b = gen.valueToCode(block, 'B', gen.ORDER_NONE) || '""';
        return ['(' + a + ' == ' + b + ')', gen.ORDER_RELATIONAL];
    }""")

    # Equals ignore case
    api.add_block(
        name="ab_text_equals_ic",
        block_type="value",
        category="Logic",
        subcategory="Text",
        colour=EXT_COLOUR,
        inputs=[
            {"name": "A", "type": "value", "label": "",       "check": "String"},
            {"name": "B", "type": "value", "label": "≈ (ic)", "check": "String"},
        ],
        tooltip={"en": "Compare strings ignoring case", "pt": "Compara strings sem diferenciar maiúsculas"},
        inline=True,
    )
    api.add_generator("ab_text_equals_ic", """function(block, gen) {
        var a = gen.valueToCode(block, 'A', gen.ORDER_NONE) || '""';
        var b = gen.valueToCode(block, 'B', gen.ORDER_NONE) || '""';
        return ['stringEqualsIgnoreCase(' + a + ', ' + b + ')', gen.ORDER_ATOMIC];
    }""")

    # Contains
    api.add_block(
        name="ab_text_contains",
        block_type="value",
        category="Logic",
        subcategory="Text",
        colour=EXT_COLOUR,
        inputs=[
            {"name": "STR", "type": "value", "label": "",    "check": "String"},
            {"name": "SUB", "type": "value", "label": "has", "check": "String"},
        ],
        tooltip={"en": "Check if string contains substring", "pt": "Verifica se contém substring"},
        inline=True,
    )
    api.add_generator("ab_text_contains", """function(block, gen) {
        var s   = gen.valueToCode(block, 'STR', gen.ORDER_NONE) || '""';
        var sub = gen.valueToCode(block, 'SUB', gen.ORDER_NONE) || '""';
        return ['stringContains(' + s + ', ' + sub + ')', gen.ORDER_ATOMIC];
    }""")

    # Length
    api.add_block(
        name="ab_text_length",
        block_type="value",
        category="Logic",
        subcategory="Text",
        colour=EXT_COLOUR,
        inputs=[{"name": "STR", "type": "value", "label": "length of", "check": "String"}],
        tooltip={"en": "String length", "pt": "Tamanho da string"},
        inline=True,
    )
    api.add_generator("ab_text_length", """function(block, gen) {
        var s = gen.valueToCode(block, 'STR', gen.ORDER_NONE) || '""';
        return [s + '.length()', gen.ORDER_MEMBER];
    }""")

    # Empty
    api.add_block(
        name="ab_text_empty",
        block_type="value",
        category="Logic",
        subcategory="Text",
        colour=EXT_COLOUR,
        inputs=[{"name": "STR", "type": "value", "label": "is empty?", "check": "String"}],
        tooltip={"en": "Is string empty?", "pt": "A string está vazia?"},
        inline=True,
    )
    api.add_generator("ab_text_empty", """function(block, gen) {
        var s = gen.valueToCode(block, 'STR', gen.ORDER_NONE) || '""';
        return [s + '.length() == 0', gen.ORDER_EQUALITY];
    }""")

    # Join
    api.add_block(
        name="ab_text_join",
        block_type="value",
        category="Logic",
        subcategory="Text",
        colour=EXT_COLOUR,
        inputs=[
            {"name": "A", "type": "value", "label": "",   "check": "String"},
            {"name": "B", "type": "value", "label": "+", "check": "String"},
        ],
        tooltip={"en": "Concatenate two strings", "pt": "Concatena duas strings"},
        inline=True,
    )
    api.add_generator("ab_text_join", """function(block, gen) {
        var a = gen.valueToCode(block, 'A', gen.ORDER_ADDITION) || '""';
        var b = gen.valueToCode(block, 'B', gen.ORDER_ADDITION) || '""';
        return [a + ' + ' + b, gen.ORDER_ADDITION];
    }""")

    # ------------------------------------------------------------------
    # 4. BLOCOS – CHAR
    # ------------------------------------------------------------------

    api.add_block(
        name="ab_char_digit",
        block_type="value",
        category="Logic",
        subcategory="Char",
        colour=EXT_COLOUR,
        inputs=[{"name": "CH", "type": "value", "label": "digit?", "check": "String"}],
        tooltip={"en": "Is character a digit?", "pt": "É um dígito?"},
        inline=True,
    )
    api.add_generator("ab_char_digit", """function(block, gen) {
        var c = gen.valueToCode(block, 'CH', gen.ORDER_NONE) || "' '";
        return ['isDigit(' + c + ')', gen.ORDER_ATOMIC];
    }""")

    api.add_block(
        name="ab_char_letter",
        block_type="value",
        category="Logic",
        subcategory="Char",
        colour=EXT_COLOUR,
        inputs=[{"name": "CH", "type": "value", "label": "letter?", "check": "String"}],
        tooltip={"en": "Is character a letter?", "pt": "É uma letra?"},
        inline=True,
    )
    api.add_generator("ab_char_letter", """function(block, gen) {
        var c = gen.valueToCode(block, 'CH', gen.ORDER_NONE) || "' '";
        return ['isAlpha(' + c + ')', gen.ORDER_ATOMIC];
    }""")

    api.add_block(
        name="ab_char_upper",
        block_type="value",
        category="Logic",
        subcategory="Char",
        colour=EXT_COLOUR,
        inputs=[{"name": "CH", "type": "value", "label": "to upper", "check": "String"}],
        tooltip={"en": "Convert char to uppercase", "pt": "Converte para maiúsculo"},
        inline=True,
    )
    api.add_generator("ab_char_upper", """function(block, gen) {
        var c = gen.valueToCode(block, 'CH', gen.ORDER_NONE) || "' '";
        return ['toupper(' + c + ')', gen.ORDER_ATOMIC];
    }""")

    api.add_block(
        name="ab_char_lower",
        block_type="value",
        category="Logic",
        subcategory="Char",
        colour=EXT_COLOUR,
        inputs=[{"name": "CH", "type": "value", "label": "to lower", "check": "String"}],
        tooltip={"en": "Convert char to lowercase", "pt": "Converte para minúsculo"},
        inline=True,
    )
    api.add_generator("ab_char_lower", """function(block, gen) {
        var c = gen.valueToCode(block, 'CH', gen.ORDER_NONE) || "' '";
        return ['tolower(' + c + ')', gen.ORDER_ATOMIC];
    }""")

    # ------------------------------------------------------------------
    # 5. BLOCOS – ADVANCED LOGIC
    # ------------------------------------------------------------------

    api.add_block(
        name="ab_logic_xor",
        block_type="value",
        category="Logic",
        subcategory="Advanced",
        colour=EXT_COLOUR,
        inputs=[
            {"name": "A", "type": "value", "label": "",   "check": "Boolean"},
            {"name": "B", "type": "value", "label": "⊕", "check": "Boolean"},
        ],
        tooltip={"en": "XOR (exclusive or): true if exactly one input is true",
                 "pt": "XOR: verdadeiro se exatamente um input for verdadeiro"},
        inline=True,
    )
    api.add_generator("ab_logic_xor", """function(block, gen) {
        var a = gen.valueToCode(block, 'A', gen.ORDER_LOGICAL_NOT) || 'false';
        var b = gen.valueToCode(block, 'B', gen.ORDER_LOGICAL_NOT) || 'false';
        return ['((' + a + ' && !' + b + ') || (!' + a + ' && ' + b + '))', gen.ORDER_LOGICAL_OR];
    }""")

    api.add_block(
        name="ab_number_between",
        block_type="value",
        category="Logic",
        subcategory="Advanced",
        colour=EXT_COLOUR,
        inputs=[
            {"name": "VALUE", "type": "value", "label": "",    "check": "Number"},
            {"name": "MIN",   "type": "value", "label": "∈ [", "check": "Number"},
            {"name": "MAX",   "type": "value", "label": "]",   "check": "Number"},
        ],
        tooltip={"en": "True if value is between min and max (inclusive)",
                 "pt": "Verdadeiro se valor estiver entre min e max (inclusive)"},
        inline=True,
    )
    api.add_generator("ab_number_between", """function(block, gen) {
        var v   = gen.valueToCode(block, 'VALUE', gen.ORDER_RELATIONAL) || '0';
        var min = gen.valueToCode(block, 'MIN',   gen.ORDER_RELATIONAL) || '0';
        var max = gen.valueToCode(block, 'MAX',   gen.ORDER_RELATIONAL) || '0';
        return ['(' + v + ' >= ' + min + ' && ' + v + ' <= ' + max + ')', gen.ORDER_LOGICAL_AND];
    }""")

    api.add_block(
        name="ab_number_tolerance",
        block_type="value",
        category="Logic",
        subcategory="Advanced",
        colour=EXT_COLOUR,
        inputs=[
            {"name": "VAL",    "type": "value", "label": "",  "check": "Number"},
            {"name": "TARGET", "type": "value", "label": "≈", "check": "Number"},
            {"name": "TOL",    "type": "value", "label": "±", "check": "Number"},
        ],
        tooltip={"en": "True if value is within tolerance of target",
                 "pt": "Verdadeiro se valor estiver dentro da tolerância do alvo"},
        inline=True,
    )
    api.add_generator("ab_number_tolerance", """function(block, gen) {
        var v   = gen.valueToCode(block, 'VAL',    gen.ORDER_NONE) || '0';
        var t   = gen.valueToCode(block, 'TARGET', gen.ORDER_NONE) || '0';
        var tol = gen.valueToCode(block, 'TOL',    gen.ORDER_NONE) || '0';
        return ['(abs(' + v + ' - ' + t + ') <= ' + tol + ')', gen.ORDER_RELATIONAL];
    }""")

    api.add_block(
        name="ab_text_is_number",
        block_type="value",
        category="Logic",
        subcategory="Advanced",
        colour=EXT_COLOUR,
        inputs=[{"name": "TEXT", "type": "value", "label": "is number?", "check": "String"}],
        tooltip={"en": "Check if string represents a number",
                 "pt": "Verifica se a string representa um número"},
        inline=True,
    )
    api.add_generator("ab_text_is_number", """function(block, gen) {
        var s = gen.valueToCode(block, 'TEXT', gen.ORDER_NONE) || '""';
        return ['isNumeric(' + s + ')', gen.ORDER_ATOMIC];
    }""")

    # ------------------------------------------------------------------
    # 6. TRADUÇÕES (em lote – uma única injeção JS)
    # ------------------------------------------------------------------

    api.add_translations({
        "en": {
            "ab_text_literal_tooltip":    "A text string value",
            "ab_text_equals_tooltip":     "Compare two strings",
            "ab_text_equals_ic_tooltip":  "Compare ignoring case",
            "ab_text_contains_tooltip":   "Check if contains",
            "ab_text_length_tooltip":     "String length",
            "ab_text_empty_tooltip":      "Is empty?",
            "ab_text_join_tooltip":       "Join strings",
            "ab_char_digit_tooltip":      "Is digit?",
            "ab_char_letter_tooltip":     "Is letter?",
            "ab_char_upper_tooltip":      "To uppercase",
            "ab_char_lower_tooltip":      "To lowercase",
            "ab_logic_xor_tooltip":       "XOR (exclusive or)",
            "ab_number_between_tooltip":  "Value between min and max",
            "ab_number_tolerance_tooltip":"Within tolerance",
            "ab_text_is_number_tooltip":  "Is numeric string?",
        },
        "pt": {
            "ab_text_literal_tooltip":    "Um valor de texto (string)",
            "ab_text_equals_tooltip":     "Compara duas strings",
            "ab_text_equals_ic_tooltip":  "Compara sem diferenciar maiúsculas",
            "ab_text_contains_tooltip":   "Verifica se contém",
            "ab_text_length_tooltip":     "Tamanho da string",
            "ab_text_empty_tooltip":      "Está vazio?",
            "ab_text_join_tooltip":       "Junta strings",
            "ab_char_digit_tooltip":      "É dígito?",
            "ab_char_letter_tooltip":     "É letra?",
            "ab_char_upper_tooltip":      "Para maiúsculo",
            "ab_char_lower_tooltip":      "Para minúsculo",
            "ab_logic_xor_tooltip":       "XOR (ou exclusivo)",
            "ab_number_between_tooltip":  "Entre min e max",
            "ab_number_tolerance_tooltip":"Dentro da tolerância",
            "ab_text_is_number_tooltip":  "É string numérica?",
        },
    })

    api.add_status_message("Advanced Logic loaded (15 blocks)", "ok")
    print("[Advanced Logic] Extension initialized successfully!")
    return True