/**
 * Advanced Pins Extension - Arduino Code Generators
 *
 * FIXES:
 * - Adicionado limite MAX_RETRIES=20 no loop setTimeout para evitar
 *   loop infinito se ArduinoGen nunca for definido.
 * - Todos os geradores verificam se já estão registrados (idempotente).
 */

(function() {
    var MAX_RETRIES = 20;
    var retries = 0;

    function init() {
        if (typeof ArduinoGen === 'undefined') {
            retries++;
            if (retries >= MAX_RETRIES) {
                console.warn('[Advanced Pins] ArduinoGen not available after ' + MAX_RETRIES + ' attempts.');
                return;
            }
            setTimeout(init, 150);
            return;
        }

        console.log('[Advanced Pins] Registering code generators...');

        if (!ArduinoGen.forBlock['ab_pin_mode_var']) {
            ArduinoGen.forBlock['ab_pin_mode_var'] = function(block, gen) {
                var pin  = gen.valueToCode(block, 'PIN', gen.ORDER_NONE) || '0';
                var mode = block.getFieldValue('MODE');
                return 'pinMode(' + pin + ', ' + mode + ');\n';
            };
        }
        if (!ArduinoGen.forBlock['ab_digital_write_var']) {
            ArduinoGen.forBlock['ab_digital_write_var'] = function(block, gen) {
                var pin   = gen.valueToCode(block, 'PIN', gen.ORDER_NONE) || '0';
                var state = block.getFieldValue('STATE');
                return 'digitalWrite(' + pin + ', ' + state + ');\n';
            };
        }
        if (!ArduinoGen.forBlock['ab_digital_read_var']) {
            ArduinoGen.forBlock['ab_digital_read_var'] = function(block, gen) {
                var pin = gen.valueToCode(block, 'PIN', gen.ORDER_NONE) || '0';
                return ['digitalRead(' + pin + ')', gen.ORDER_ATOMIC];
            };
        }
        if (!ArduinoGen.forBlock['ab_analog_write_var']) {
            ArduinoGen.forBlock['ab_analog_write_var'] = function(block, gen) {
                var pin = gen.valueToCode(block, 'PIN',   gen.ORDER_NONE) || '0';
                var val = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
                return 'analogWrite(' + pin + ', ' + val + ');\n';
            };
        }
        if (!ArduinoGen.forBlock['ab_analog_read_var']) {
            ArduinoGen.forBlock['ab_analog_read_var'] = function(block, gen) {
                var pin = gen.valueToCode(block, 'PIN', gen.ORDER_NONE) || '0';
                return ['analogRead(' + pin + ')', gen.ORDER_ATOMIC];
            };
        }
        if (!ArduinoGen.forBlock['ab_is_pwm_pin']) {
            ArduinoGen.forBlock['ab_is_pwm_pin'] = function(block, gen) {
                var pin = gen.valueToCode(block, 'PIN', gen.ORDER_NONE) || '0';
                return ['isPwmPin(' + pin + ')', gen.ORDER_ATOMIC];
            };
        }
        if (!ArduinoGen.forBlock['ab_pin_to_string']) {
            ArduinoGen.forBlock['ab_pin_to_string'] = function(block, gen) {
                var pin = gen.valueToCode(block, 'PIN', gen.ORDER_NONE) || '0';
                return ['pinToString(' + pin + ')', gen.ORDER_ATOMIC];
            };
        }

        console.log('[Advanced Pins] Code generators registered!');
    }

    init();
})();