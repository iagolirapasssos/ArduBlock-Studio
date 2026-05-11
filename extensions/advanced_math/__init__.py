"""
Advanced Mathematics Extension - Versão Corrigida
Matemática Avançada para ArduBlock Studio
"""

def initialize(api):
    """Inicializa a extensão de matemática avançada"""
    print("[Advanced Math] Initializing...")
    
    # ============================================================
    # CONSTANTES GLOBAIS
    # ============================================================
    api.add_global_constant("PI", "#define PI 3.14159265358979323846")
    
    # ============================================================
    # FUNÇÕES AUXILIARES (CORRIGIDAS - USANDO FUNÇÕES DEF CORRETAMENTE)
    # ============================================================
    
    # Fatorial - NÃO nativo no Arduino
    api.add_global_function("factorial_func", """
unsigned long long factorial(int n) {
    if (n <= 1) return 1;
    unsigned long long result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}""")
    
    # Raiz Cúbica - NÃO nativo no Arduino
    api.add_global_function("cbrt_func", """
double cbrt(double x) {
    if (x < 0) return -pow(-x, 1.0/3.0);
    return pow(x, 1.0/3.0);
}""")
    
    # Raiz Enésima - NÃO nativo no Arduino
    api.add_global_function("nth_root_func", """
double nth_root(double x, double n) {
    if (n == 0) return 1;
    if (x < 0 && fmod(n, 2) != 0) return -pow(-x, 1.0/n);
    return pow(x, 1.0/n);
}""")
    
    # Logaritmo com base personalizada - NÃO nativo no Arduino
    api.add_global_function("log_base_func", """
double log_base(double x, double base) {
    if (x <= 0 || base <= 0 || base == 1) return 0;
    return log(x) / log(base);
}""")
    
    # MDC (GCD) - NÃO nativo no Arduino
    api.add_global_function("gcd_func", """
int gcd(int a, int b) {
    a = abs(a);
    b = abs(b);
    while (b != 0) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}""")
    
    # MMC (LCM) - NÃO nativo no Arduino
    api.add_global_function("lcm_func", """
int lcm(int a, int b) {
    if (a == 0 || b == 0) return 0;
    return abs(a) / gcd(a, b) * abs(b);
}""")
    
    # Verificador de número primo - NÃO nativo no Arduino
    api.add_global_function("is_prime_func", """
bool isPrime(int n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;
    for (int i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) return false;
    }
    return true;
}""")
    
    # Número aleatório em intervalo - NÃO nativo (random tem outras regras)
    api.add_global_function("random_range_func", """
long randomRange(long min, long max) {
    if (min >= max) return min;
    return min + random(max - min);
}""")
    
    # Arredondamento para casas decimais - NÃO nativo
    api.add_global_function("round_to_func", """
double roundTo(double value, int decimals) {
    double factor = pow(10, decimals);
    return round(value * factor) / factor;
}""")
    
    # ============================================================
    # CRIAÇÃO DAS SUBCATEGORIAS
    # ============================================================
    
    api.add_category("Mathematics", "Basic Numbers", "#1a7a6e", "numbers")
    api.add_category("Mathematics", "Trigonometry", "#1a7a6e", "show_chart")
    api.add_category("Mathematics", "Roots & Powers", "#00acc1", "graphic_eq")
    api.add_category("Mathematics", "Logarithms", "#7cb342", "timeline")
    api.add_category("Mathematics", "Geometry", "#ff7043", "square_foot")
    api.add_category("Mathematics", "Number Theory", "#ab47bc", "numbers")
    api.add_category("Mathematics", "Combinatorics", "#ec407a", "calculate")
    api.add_category("Mathematics", "Angle Conversion", "#26a69a", "swap_horiz")
    api.add_category("Mathematics", "Random Numbers", "#ff9800", "casino")
    api.add_category("Mathematics", "Rounding", "#795548", "format_align_center")
    
    api.add_separator("Mathematics")
    
    # ============================================================
    # BLOCOS DE NÚMEROS BÁSICOS
    # ============================================================
    
    # Número inteiro
    api.add_block(
        name="ab_math_number",
        block_type="value",
        category="Mathematics",
        subcategory="Basic Numbers",
        colour="#1a7a6e",
        inputs=[{"name": "NUM", "type": "field", "label": "", "default": "0"}],
        tooltip={"en": "A number", "pt": "Um número"}
    )
    api.add_generator("ab_math_number", """function(block, gen) {
        var num = block.getFieldValue('NUM');
        return [num, gen.ORDER_ATOMIC];
    }""")
    
    # Número decimal
    api.add_block(
        name="ab_math_float",
        block_type="value",
        category="Mathematics",
        subcategory="Basic Numbers",
        colour="#1a7a6e",
        inputs=[{"name": "NUM", "type": "field", "label": "", "default": "0.0"}],
        tooltip={"en": "A decimal number", "pt": "Um número decimal"}
    )
    api.add_generator("ab_math_float", """function(block, gen) {
        var num = block.getFieldValue('NUM');
        return [num, gen.ORDER_ATOMIC];
    }""")
    
    # ============================================================
    # TRIGONOMETRIA
    # ============================================================
    
    api.add_block(
        name="ab_math_sin",
        block_type="value",
        category="Mathematics",
        subcategory="Trigonometry",
        colour="#1a7a6e",
        inputs=[{"name": "ANGLE", "type": "value", "label": "sin(", "check": "Number"}],
        tooltip={"en": "Sine of angle (degrees)", "pt": "Seno do ângulo (graus)"}
    )
    api.add_generator("ab_math_sin", """function(block, gen) {
        var a = gen.valueToCode(block, 'ANGLE', gen.ORDER_NONE) || '0';
        return ['sin(' + a + ' * PI / 180.0)', gen.ORDER_ATOMIC];
    }""")
    
    api.add_block(
        name="ab_math_cos",
        block_type="value",
        category="Mathematics",
        subcategory="Trigonometry",
        colour="#1a7a6e",
        inputs=[{"name": "ANGLE", "type": "value", "label": "cos(", "check": "Number"}],
        tooltip={"en": "Cosine of angle (degrees)", "pt": "Cosseno do ângulo (graus)"}
    )
    api.add_generator("ab_math_cos", """function(block, gen) {
        var a = gen.valueToCode(block, 'ANGLE', gen.ORDER_NONE) || '0';
        return ['cos(' + a + ' * PI / 180.0)', gen.ORDER_ATOMIC];
    }""")
    
    api.add_block(
        name="ab_math_tan",
        block_type="value",
        category="Mathematics",
        subcategory="Trigonometry",
        colour="#1a7a6e",
        inputs=[{"name": "ANGLE", "type": "value", "label": "tan(", "check": "Number"}],
        tooltip={"en": "Tangent of angle (degrees)", "pt": "Tangente do ângulo (graus)"}
    )
    api.add_generator("ab_math_tan", """function(block, gen) {
        var a = gen.valueToCode(block, 'ANGLE', gen.ORDER_NONE) || '0';
        return ['tan(' + a + ' * PI / 180.0)', gen.ORDER_ATOMIC];
    }""")
    
    # ============================================================
    # RAÍZES E POTÊNCIAS
    # ============================================================
    
    api.add_block(
        name="ab_math_sqrt",
        block_type="value",
        category="Mathematics",
        subcategory="Roots & Powers",
        colour="#00acc1",
        inputs=[{"name": "VALUE", "type": "value", "label": "√", "check": "Number"}],
        tooltip={"en": "Square root", "pt": "Raiz quadrada"}
    )
    api.add_generator("ab_math_sqrt", """function(block, gen) {
        var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
        return ['sqrt(' + v + ')', gen.ORDER_ATOMIC];
    }""")
    
    api.add_block(
        name="ab_math_cbrt",
        block_type="value",
        category="Mathematics",
        subcategory="Roots & Powers",
        colour="#00acc1",
        inputs=[{"name": "VALUE", "type": "value", "label": "∛", "check": "Number"}],
        tooltip={"en": "Cube root", "pt": "Raiz cúbica"}
    )
    api.add_generator("ab_math_cbrt", """function(block, gen) {
        var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
        return ['cbrt(' + v + ')', gen.ORDER_ATOMIC];
    }""")
    
    api.add_block(
        name="ab_math_pow",
        block_type="value",
        category="Mathematics",
        subcategory="Roots & Powers",
        colour="#00acc1",
        inputs=[
            {"name": "BASE", "type": "value", "label": "power(", "check": "Number"},
            {"name": "EXP", "type": "value", "label": "^", "check": "Number"}
        ],
        tooltip={"en": "Power (base^exp)", "pt": "Potência (base^exp)"}
    )
    api.add_generator("ab_math_pow", """function(block, gen) {
        var b = gen.valueToCode(block, 'BASE', gen.ORDER_ATOMIC) || '0';
        var e = gen.valueToCode(block, 'EXP', gen.ORDER_ATOMIC) || '0';
        return ['pow(' + b + ', ' + e + ')', gen.ORDER_ATOMIC];
    }""")
    
    # ============================================================
    # LOGARITMOS
    # ============================================================
    
    api.add_block(
        name="ab_math_log",
        block_type="value",
        category="Mathematics",
        subcategory="Logarithms",
        colour="#7cb342",
        inputs=[{"name": "VALUE", "type": "value", "label": "ln(", "check": "Number"}],
        tooltip={"en": "Natural log (base e)", "pt": "Log natural (base e)"}
    )
    api.add_generator("ab_math_log", """function(block, gen) {
        var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
        return ['log(' + v + ')', gen.ORDER_ATOMIC];
    }""")
    
    api.add_block(
        name="ab_math_log10",
        block_type="value",
        category="Mathematics",
        subcategory="Logarithms",
        colour="#7cb342",
        inputs=[{"name": "VALUE", "type": "value", "label": "log₁₀(", "check": "Number"}],
        tooltip={"en": "Base-10 log", "pt": "Log base 10"}
    )
    api.add_generator("ab_math_log10", """function(block, gen) {
        var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
        return ['log10(' + v + ')', gen.ORDER_ATOMIC];
    }""")
    
    # ============================================================
    # COMBINATÓRIA - FATORIAL CORRIGIDO
    # ============================================================
    
    api.add_block(
        name="ab_math_factorial",
        block_type="value",
        category="Mathematics",
        subcategory="Combinatorics",
        colour="#ec407a",
        inputs=[{"name": "N", "type": "value", "label": "!", "check": "Number"}],
        tooltip={"en": "Factorial (n!)", "pt": "Fatorial (n!)"}
    )
    api.add_generator("ab_math_factorial", """function(block, gen) {
        var n = gen.valueToCode(block, 'N', gen.ORDER_NONE) || '0';
        return ['factorial(' + n + ')', gen.ORDER_ATOMIC];
    }""")
    
    # ============================================================
    # TEORIA DOS NÚMEROS
    # ============================================================
    
    api.add_block(
        name="ab_math_gcd",
        block_type="value",
        category="Mathematics",
        subcategory="Number Theory",
        colour="#ab47bc",
        inputs=[
            {"name": "A", "type": "value", "label": "gcd(", "check": "Number"},
            {"name": "B", "type": "value", "label": ",", "check": "Number"}
        ],
        tooltip={"en": "GCD (Greatest Common Divisor)", "pt": "MDC (Máximo Divisor Comum)"}
    )
    api.add_generator("ab_math_gcd", """function(block, gen) {
        var a = gen.valueToCode(block, 'A', gen.ORDER_NONE) || '0';
        var b = gen.valueToCode(block, 'B', gen.ORDER_NONE) || '0';
        return ['gcd(' + a + ', ' + b + ')', gen.ORDER_ATOMIC];
    }""")
    
    api.add_block(
        name="ab_math_lcm",
        block_type="value",
        category="Mathematics",
        subcategory="Number Theory",
        colour="#ab47bc",
        inputs=[
            {"name": "A", "type": "value", "label": "lcm(", "check": "Number"},
            {"name": "B", "type": "value", "label": ",", "check": "Number"}
        ],
        tooltip={"en": "LCM (Least Common Multiple)", "pt": "MMC (Mínimo Múltiplo Comum)"}
    )
    api.add_generator("ab_math_lcm", """function(block, gen) {
        var a = gen.valueToCode(block, 'A', gen.ORDER_NONE) || '0';
        var b = gen.valueToCode(block, 'B', gen.ORDER_NONE) || '0';
        return ['lcm(' + a + ', ' + b + ')', gen.ORDER_ATOMIC];
    }""")
    
    api.add_block(
        name="ab_math_is_prime",
        block_type="value",
        category="Mathematics",
        subcategory="Number Theory",
        colour="#ab47bc",
        inputs=[{"name": "N", "type": "value", "label": "is prime?(", "check": "Number"}],
        tooltip={"en": "Check if number is prime", "pt": "Verifica se número é primo"}
    )
    api.add_generator("ab_math_is_prime", """function(block, gen) {
        var n = gen.valueToCode(block, 'N', gen.ORDER_NONE) || '0';
        return ['isPrime(' + n + ')', gen.ORDER_ATOMIC];
    }""")
    
    # ============================================================
    # NÚMEROS ALEATÓRIOS
    # ============================================================
    
    api.add_block(
        name="ab_math_random",
        block_type="value",
        category="Mathematics",
        subcategory="Random Numbers",
        colour="#ff9800",
        inputs=[
            {"name": "MIN", "type": "value", "label": "random(", "check": "Number"},
            {"name": "MAX", "type": "value", "label": "to", "check": "Number"}
        ],
        tooltip={"en": "Random number between min and max", "pt": "Número aleatório entre min e max"}
    )
    api.add_generator("ab_math_random", """function(block, gen) {
        var min = gen.valueToCode(block, 'MIN', gen.ORDER_NONE) || '0';
        var max = gen.valueToCode(block, 'MAX', gen.ORDER_NONE) || '100';
        return ['random(' + min + ', ' + max + ')', gen.ORDER_ATOMIC];
    }""")
    
    # ============================================================
    # ARREDONDAMENTO
    # ============================================================
    
    api.add_block(
        name="ab_math_round",
        block_type="value",
        category="Mathematics",
        subcategory="Rounding",
        colour="#795548",
        inputs=[{"name": "VALUE", "type": "value", "label": "round(", "check": "Number"}],
        tooltip={"en": "Round to nearest integer", "pt": "Arredonda para inteiro mais próximo"}
    )
    api.add_generator("ab_math_round", """function(block, gen) {
        var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
        return ['round(' + v + ')', gen.ORDER_ATOMIC];
    }""")
    
    api.add_block(
        name="ab_math_ceil",
        block_type="value",
        category="Mathematics",
        subcategory="Rounding",
        colour="#795548",
        inputs=[{"name": "VALUE", "type": "value", "label": "ceil(", "check": "Number"}],
        tooltip={"en": "Round up (ceiling)", "pt": "Arredonda para cima (teto)"}
    )
    api.add_generator("ab_math_ceil", """function(block, gen) {
        var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
        return ['ceil(' + v + ')', gen.ORDER_ATOMIC];
    }""")
    
    api.add_block(
        name="ab_math_floor",
        block_type="value",
        category="Mathematics",
        subcategory="Rounding",
        colour="#795548",
        inputs=[{"name": "VALUE", "type": "value", "label": "floor(", "check": "Number"}],
        tooltip={"en": "Round down (floor)", "pt": "Arredonda para baixo (piso)"}
    )
    api.add_generator("ab_math_floor", """function(block, gen) {
        var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
        return ['floor(' + v + ')', gen.ORDER_ATOMIC];
    }""")
    
    # ============================================================
    # CONVERSÃO DE ÂNGULOS
    # ============================================================
    
    api.add_block(
        name="ab_math_degrees_to_radians",
        block_type="value",
        category="Mathematics",
        subcategory="Angle Conversion",
        colour="#26a69a",
        inputs=[{"name": "DEGREES", "type": "value", "label": "degrees → radians(", "check": "Number"}],
        tooltip={"en": "Degrees to radians", "pt": "Graus para radianos"}
    )
    api.add_generator("ab_math_degrees_to_radians", """function(block, gen) {
        var d = gen.valueToCode(block, 'DEGREES', gen.ORDER_NONE) || '0';
        return ['(' + d + ' * PI / 180.0)', gen.ORDER_ATOMIC];
    }""")
    
    api.add_block(
        name="ab_math_radians_to_degrees",
        block_type="value",
        category="Mathematics",
        subcategory="Angle Conversion",
        colour="#26a69a",
        inputs=[{"name": "RADIANS", "type": "value", "label": "radians → degrees(", "check": "Number"}],
        tooltip={"en": "Radians to degrees", "pt": "Radianos para graus"}
    )
    api.add_generator("ab_math_radians_to_degrees", """function(block, gen) {
        var r = gen.valueToCode(block, 'RADIANS', gen.ORDER_NONE) || '0';
        return ['(' + r + ' * 180.0 / PI)', gen.ORDER_ATOMIC];
    }""")
    
    # ============================================================
    # TRADUÇÕES
    # ============================================================
    
    api.add_translations({
        "en": {
            "ab_math_sin_tooltip": "Sine of an angle (in degrees)",
            "ab_math_cos_tooltip": "Cosine of an angle (in degrees)",
            "ab_math_tan_tooltip": "Tangent of an angle (in degrees)",
            "ab_math_sqrt_tooltip": "Square root",
            "ab_math_cbrt_tooltip": "Cube root",
            "ab_math_pow_tooltip": "Power (base^exponent)",
            "ab_math_log_tooltip": "Natural logarithm (base e)",
            "ab_math_log10_tooltip": "Base-10 logarithm",
            "ab_math_factorial_tooltip": "Factorial (n!)",
            "ab_math_gcd_tooltip": "Greatest common divisor",
            "ab_math_lcm_tooltip": "Least common multiple",
            "ab_math_is_prime_tooltip": "Check if number is prime",
            "ab_math_random_tooltip": "Random number between min and max",
            "ab_math_round_tooltip": "Round to nearest integer",
            "ab_math_ceil_tooltip": "Round up (ceiling)",
            "ab_math_floor_tooltip": "Round down (floor)",
            "ab_math_number_tooltip": "A number",
            "ab_math_float_tooltip": "A decimal number",
            "ab_math_degrees_to_radians_tooltip": "Convert degrees to radians",
            "ab_math_radians_to_degrees_tooltip": "Convert radians to degrees"
        },
        "pt": {
            "ab_math_sin_tooltip": "Seno de um ângulo (em graus)",
            "ab_math_cos_tooltip": "Cosseno de um ângulo (em graus)",
            "ab_math_tan_tooltip": "Tangente de um ângulo (em graus)",
            "ab_math_sqrt_tooltip": "Raiz quadrada",
            "ab_math_cbrt_tooltip": "Raiz cúbica",
            "ab_math_pow_tooltip": "Potência (base^expoente)",
            "ab_math_log_tooltip": "Logaritmo natural (base e)",
            "ab_math_log10_tooltip": "Logaritmo base 10",
            "ab_math_factorial_tooltip": "Fatorial (n!)",
            "ab_math_gcd_tooltip": "Máximo divisor comum",
            "ab_math_lcm_tooltip": "Mínimo múltiplo comum",
            "ab_math_is_prime_tooltip": "Verifica se número é primo",
            "ab_math_random_tooltip": "Número aleatório entre min e max",
            "ab_math_round_tooltip": "Arredonda para inteiro mais próximo",
            "ab_math_ceil_tooltip": "Arredonda para cima (teto)",
            "ab_math_floor_tooltip": "Arredonda para baixo (piso)",
            "ab_math_number_tooltip": "Um número",
            "ab_math_float_tooltip": "Um número decimal",
            "ab_math_degrees_to_radians_tooltip": "Converter graus para radianos",
            "ab_math_radians_to_degrees_tooltip": "Converter radianos para graus"
        }
    })
    
    # ============================================================
    # MENSAGEM DE CONCLUSÃO
    # ============================================================
    
    api.add_status_message("Advanced Mathematics extension loaded! (23 blocks)", "ok")
    print("[Advanced Math] Extension loaded successfully with 23 blocks!")
    
    return True