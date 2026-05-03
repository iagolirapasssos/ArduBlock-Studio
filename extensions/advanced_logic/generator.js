/**
 * Advanced Logic Extension - Arduino Code Generators
 *
 * FIXES:
 * - Adicionado limite máximo de tentativas (MAX_RETRIES=20) no loop
 *   setTimeout(init, 100) para evitar loop infinito caso ArduinoGen
 *   nunca seja definido.
 * - Removidos geradores duplicados (já registrados via api.add_generator()
 *   no __init__.py). Este arquivo é um fallback para garantir que os
 *   geradores sejam registrados mesmo se o Python não puder injetar.
 */

(function() {
    var MAX_RETRIES = 20;
    var retries = 0;

    function init() {
        if (typeof ArduinoGen === 'undefined') {
            retries++;
            if (retries >= MAX_RETRIES) {
                console.warn('[Advanced Logic] ArduinoGen not available after ' + MAX_RETRIES + ' attempts. Generators not registered.');
                return;
            }
            setTimeout(init, 150);
            return;
        }

        console.log('[Advanced Logic] Registering code generators...');

        // TEXT
        if (!ArduinoGen.forBlock['ab_text_literal']) {
            ArduinoGen.forBlock['ab_text_literal'] = function(block, gen) {
                var text = block.getFieldValue('TEXT');
                return ['"' + text.replace(/"/g, '\\"') + '"', gen.ORDER_ATOMIC];
            };
        }
        if (!ArduinoGen.forBlock['ab_text_equals']) {
            ArduinoGen.forBlock['ab_text_equals'] = function(block, gen) {
                var a = gen.valueToCode(block, 'A', gen.ORDER_NONE) || '""';
                var b = gen.valueToCode(block, 'B', gen.ORDER_NONE) || '""';
                return ['(' + a + ' == ' + b + ')', gen.ORDER_RELATIONAL];
            };
        }
        if (!ArduinoGen.forBlock['ab_text_equals_ic']) {
            ArduinoGen.forBlock['ab_text_equals_ic'] = function(block, gen) {
                var a = gen.valueToCode(block, 'A', gen.ORDER_NONE) || '""';
                var b = gen.valueToCode(block, 'B', gen.ORDER_NONE) || '""';
                return ['stringEqualsIgnoreCase(' + a + ', ' + b + ')', gen.ORDER_ATOMIC];
            };
        }
        if (!ArduinoGen.forBlock['ab_text_contains']) {
            ArduinoGen.forBlock['ab_text_contains'] = function(block, gen) {
                var s   = gen.valueToCode(block, 'STR', gen.ORDER_NONE) || '""';
                var sub = gen.valueToCode(block, 'SUB', gen.ORDER_NONE) || '""';
                return ['stringContains(' + s + ', ' + sub + ')', gen.ORDER_ATOMIC];
            };
        }
        if (!ArduinoGen.forBlock['ab_text_length']) {
            ArduinoGen.forBlock['ab_text_length'] = function(block, gen) {
                var s = gen.valueToCode(block, 'STR', gen.ORDER_NONE) || '""';
                return [s + '.length()', gen.ORDER_MEMBER];
            };
        }
        if (!ArduinoGen.forBlock['ab_text_empty']) {
            ArduinoGen.forBlock['ab_text_empty'] = function(block, gen) {
                var s = gen.valueToCode(block, 'STR', gen.ORDER_NONE) || '""';
                return [s + '.length() == 0', gen.ORDER_EQUALITY];
            };
        }
        if (!ArduinoGen.forBlock['ab_text_join']) {
            ArduinoGen.forBlock['ab_text_join'] = function(block, gen) {
                var a = gen.valueToCode(block, 'A', gen.ORDER_ADDITION) || '""';
                var b = gen.valueToCode(block, 'B', gen.ORDER_ADDITION) || '""';
                return [a + ' + ' + b, gen.ORDER_ADDITION];
            };
        }

        // CHAR
        if (!ArduinoGen.forBlock['ab_char_digit']) {
            ArduinoGen.forBlock['ab_char_digit'] = function(block, gen) {
                var c = gen.valueToCode(block, 'CH', gen.ORDER_NONE) || "' '";
                return ['isDigit(' + c + ')', gen.ORDER_ATOMIC];
            };
        }
        if (!ArduinoGen.forBlock['ab_char_letter']) {
            ArduinoGen.forBlock['ab_char_letter'] = function(block, gen) {
                var c = gen.valueToCode(block, 'CH', gen.ORDER_NONE) || "' '";
                return ['isAlpha(' + c + ')', gen.ORDER_ATOMIC];
            };
        }
        if (!ArduinoGen.forBlock['ab_char_upper']) {
            ArduinoGen.forBlock['ab_char_upper'] = function(block, gen) {
                var c = gen.valueToCode(block, 'CH', gen.ORDER_NONE) || "' '";
                return ['toupper(' + c + ')', gen.ORDER_ATOMIC];
            };
        }
        if (!ArduinoGen.forBlock['ab_char_lower']) {
            ArduinoGen.forBlock['ab_char_lower'] = function(block, gen) {
                var c = gen.valueToCode(block, 'CH', gen.ORDER_NONE) || "' '";
                return ['tolower(' + c + ')', gen.ORDER_ATOMIC];
            };
        }

        // ADVANCED
        if (!ArduinoGen.forBlock['ab_logic_xor']) {
            ArduinoGen.forBlock['ab_logic_xor'] = function(block, gen) {
                var a = gen.valueToCode(block, 'A', gen.ORDER_LOGICAL_NOT) || 'false';
                var b = gen.valueToCode(block, 'B', gen.ORDER_LOGICAL_NOT) || 'false';
                return ['((' + a + ' && !' + b + ') || (!' + a + ' && ' + b + '))', gen.ORDER_LOGICAL_OR];
            };
        }
        if (!ArduinoGen.forBlock['ab_number_between']) {
            ArduinoGen.forBlock['ab_number_between'] = function(block, gen) {
                var v   = gen.valueToCode(block, 'VALUE', gen.ORDER_RELATIONAL) || '0';
                var min = gen.valueToCode(block, 'MIN',   gen.ORDER_RELATIONAL) || '0';
                var max = gen.valueToCode(block, 'MAX',   gen.ORDER_RELATIONAL) || '0';
                return ['(' + v + ' >= ' + min + ' && ' + v + ' <= ' + max + ')', gen.ORDER_LOGICAL_AND];
            };
        }
        if (!ArduinoGen.forBlock['ab_number_tolerance']) {
            ArduinoGen.forBlock['ab_number_tolerance'] = function(block, gen) {
                var v   = gen.valueToCode(block, 'VAL',    gen.ORDER_NONE) || '0';
                var t   = gen.valueToCode(block, 'TARGET', gen.ORDER_NONE) || '0';
                var tol = gen.valueToCode(block, 'TOL',    gen.ORDER_NONE) || '0';
                return ['(abs(' + v + ' - ' + t + ') <= ' + tol + ')', gen.ORDER_RELATIONAL];
            };
        }
        if (!ArduinoGen.forBlock['ab_text_is_number']) {
            ArduinoGen.forBlock['ab_text_is_number'] = function(block, gen) {
                var s = gen.valueToCode(block, 'TEXT', gen.ORDER_NONE) || '""';
                return ['isNumeric(' + s + ')', gen.ORDER_ATOMIC];
            };
        }

        console.log('[Advanced Logic] Code generators registered successfully!');
    }

    init();
})();