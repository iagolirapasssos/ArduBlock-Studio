/**
 * Advanced Mathematics Extension - Arduino Code Generators
 */

(function() {
    function init() {
        if (typeof ArduinoGen === 'undefined') {
            setTimeout(init, 100);
            return;
        }
        
        console.log('[Advanced Math] Registering code generators...');
        
        // Define constante PI
        ArduinoGen._globals = ArduinoGen._globals || {};
        if (!ArduinoGen._globals['math_pi']) {
            ArduinoGen._globals['math_pi'] = '#define PI 3.14159265358979323846';
        }
        
        // Função para random - necessária no Arduino
        if (!ArduinoGen._globals['random_setup']) {
            ArduinoGen._globals['random_setup'] = 'randomSeed(analogRead(0));';
        }
        
        // ==================== NÚMEROS BÁSICOS ====================
        ArduinoGen.forBlock['ab_math_number'] = function(block, gen) {
            var num = block.getFieldValue('NUM');
            return [num, gen.ORDER_ATOMIC];
        };
        
        ArduinoGen.forBlock['ab_math_float'] = function(block, gen) {
            var num = block.getFieldValue('NUM');
            return [num, gen.ORDER_ATOMIC];
        };
        
        // ==================== TRIGONOMETRIA ====================
        ArduinoGen.forBlock['ab_math_sin'] = function(block, gen) {
            var a = gen.valueToCode(block, 'ANGLE', gen.ORDER_NONE) || '0';
            return ['sin(' + a + ' * PI / 180.0)', gen.ORDER_ATOMIC];
        };
        
        ArduinoGen.forBlock['ab_math_cos'] = function(block, gen) {
            var a = gen.valueToCode(block, 'ANGLE', gen.ORDER_NONE) || '0';
            return ['cos(' + a + ' * PI / 180.0)', gen.ORDER_ATOMIC];
        };
        
        ArduinoGen.forBlock['ab_math_tan'] = function(block, gen) {
            var a = gen.valueToCode(block, 'ANGLE', gen.ORDER_NONE) || '0';
            return ['tan(' + a + ' * PI / 180.0)', gen.ORDER_ATOMIC];
        };
        
        // ==================== RAÍZES E POTÊNCIAS ====================
        ArduinoGen.forBlock['ab_math_sqrt'] = function(block, gen) {
            var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
            return ['sqrt(' + v + ')', gen.ORDER_ATOMIC];
        };
        
        ArduinoGen.forBlock['ab_math_cbrt'] = function(block, gen) {
            var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
            return ['cbrt(' + v + ')', gen.ORDER_ATOMIC];
        };
        
        ArduinoGen.forBlock['ab_math_pow'] = function(block, gen) {
            var b = gen.valueToCode(block, 'BASE', gen.ORDER_ATOMIC) || '0';
            var e = gen.valueToCode(block, 'EXP', gen.ORDER_ATOMIC) || '0';
            return ['pow(' + b + ', ' + e + ')', gen.ORDER_ATOMIC];
        };
        
        // ==================== LOGARITMOS ====================
        ArduinoGen.forBlock['ab_math_log'] = function(block, gen) {
            var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
            return ['log(' + v + ')', gen.ORDER_ATOMIC];
        };
        
        ArduinoGen.forBlock['ab_math_log10'] = function(block, gen) {
            var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
            return ['log10(' + v + ')', gen.ORDER_ATOMIC];
        };
        
        // ==================== COMBINATÓRIA ====================
        ArduinoGen.forBlock['ab_math_factorial'] = function(block, gen) {
            var n = gen.valueToCode(block, 'N', gen.ORDER_NONE) || '0';
            return ['factorial(' + n + ')', gen.ORDER_ATOMIC];
        };
        
        // ==================== TEORIA DOS NÚMEROS ====================
        ArduinoGen.forBlock['ab_math_gcd'] = function(block, gen) {
            var a = gen.valueToCode(block, 'A', gen.ORDER_NONE) || '0';
            var b = gen.valueToCode(block, 'B', gen.ORDER_NONE) || '0';
            return ['gcd(' + a + ', ' + b + ')', gen.ORDER_ATOMIC];
        };
        
        ArduinoGen.forBlock['ab_math_lcm'] = function(block, gen) {
            var a = gen.valueToCode(block, 'A', gen.ORDER_NONE) || '0';
            var b = gen.valueToCode(block, 'B', gen.ORDER_NONE) || '0';
            return ['lcm(' + a + ', ' + b + ')', gen.ORDER_ATOMIC];
        };
        
        ArduinoGen.forBlock['ab_math_is_prime'] = function(block, gen) {
            var n = gen.valueToCode(block, 'N', gen.ORDER_NONE) || '0';
            return ['isPrime(' + n + ')', gen.ORDER_ATOMIC];
        };
        
        // ==================== NÚMEROS ALEATÓRIOS ====================
        ArduinoGen.forBlock['ab_math_random'] = function(block, gen) {
            var min = gen.valueToCode(block, 'MIN', gen.ORDER_NONE) || '0';
            var max = gen.valueToCode(block, 'MAX', gen.ORDER_NONE) || '100';
            return ['random(' + min + ', ' + max + ')', gen.ORDER_ATOMIC];
        };
        
        // ==================== ARREDONDAMENTO ====================
        ArduinoGen.forBlock['ab_math_round'] = function(block, gen) {
            var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
            return ['round(' + v + ')', gen.ORDER_ATOMIC];
        };
        
        ArduinoGen.forBlock['ab_math_ceil'] = function(block, gen) {
            var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
            return ['ceil(' + v + ')', gen.ORDER_ATOMIC];
        };
        
        ArduinoGen.forBlock['ab_math_floor'] = function(block, gen) {
            var v = gen.valueToCode(block, 'VALUE', gen.ORDER_NONE) || '0';
            return ['floor(' + v + ')', gen.ORDER_ATOMIC];
        };
        
        // ==================== CONVERSÃO DE ÂNGULOS ====================
        ArduinoGen.forBlock['ab_math_degrees_to_radians'] = function(block, gen) {
            var d = gen.valueToCode(block, 'DEGREES', gen.ORDER_NONE) || '0';
            return ['(' + d + ' * PI / 180.0)', gen.ORDER_ATOMIC];
        };
        
        ArduinoGen.forBlock['ab_math_radians_to_degrees'] = function(block, gen) {
            var r = gen.valueToCode(block, 'RADIANS', gen.ORDER_NONE) || '0';
            return ['(' + r + ' * 180.0 / PI)', gen.ORDER_ATOMIC];
        };
        
        console.log('[Advanced Math] Code generators registered successfully!');
    }
    
    init();
})();