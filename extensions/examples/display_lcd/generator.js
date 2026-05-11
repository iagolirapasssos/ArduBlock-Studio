// LCD Display Extension - Code Generator

// Registra geradores para os blocos da extensão LCD
(function() {
    // Gerador para ab_lcd_begin
    ArduinoGen.forBlock['ab_lcd_begin'] = function(block, generator) {
        var rs = block.getFieldValue('RS');
        var en = block.getFieldValue('EN');
        var d4 = block.getFieldValue('D4');
        var d5 = block.getFieldValue('D5');
        var d6 = block.getFieldValue('D6');
        var d7 = block.getFieldValue('D7');
        
        // Adiciona include da biblioteca LiquidCrystal
        ArduinoGen._includes['LiquidCrystal'] = '#include <LiquidCrystal.h>';
        
        // Declara objeto global do LCD
        ArduinoGen._globals['lcd'] = `LiquidCrystal lcd(${rs}, ${en}, ${d4}, ${d5}, ${d6}, ${d7});`;
        
        // Código de inicialização
        return 'lcd.begin(16, 2);\n';
    };
    
    // Gerador para ab_lcd_print
    ArduinoGen.forBlock['ab_lcd_print'] = function(block, generator) {
        var col = generator.valueToCode(block, 'COL', generator.ORDER_NONE) || '0';
        var row = generator.valueToCode(block, 'ROW', generator.ORDER_NONE) || '0';
        var text = generator.valueToCode(block, 'TEXT', generator.ORDER_NONE) || '""';
        
        return `lcd.setCursor(${col}, ${row});\n` +
               `lcd.print(${text});\n`;
    };
    
    // Gerador para ab_lcd_clear
    ArduinoGen.forBlock['ab_lcd_clear'] = function(block, generator) {
        return 'lcd.clear();\n';
    };
    
    // Gerador para ab_lcd_create_char
    ArduinoGen.forBlock['ab_lcd_create_char'] = function(block, generator) {
        var num = generator.valueToCode(block, 'NUMBER', generator.ORDER_NONE) || '0';
        var data = generator.valueToCode(block, 'DATA', generator.ORDER_NONE) || '{}';
        
        return `lcd.createChar(${num}, ${data});\n`;
    };
})();