/**
 * Template para criar novos blocos
 * 
 * Como usar:
 * 1. Copie este arquivo para sua extensão
 * 2. Modifique o nome do bloco e os campos
 * 3. Adicione o gerador de código correspondente
 */

// Definição do bloco
Blockly.Blocks['custom_block_name'] = {
    init: function() {
        // Cor do bloco (use cores da paleta do ArduBlock)
        this.setColour('#9966ff');
        
        // Adicione entradas
        this.appendDummyInput()
            .appendField("My Custom Block");
        
        // Ou valor com dropdown
        this.appendDummyInput()
            .appendField("Option")
            .appendField(new Blockly.FieldDropdown([
                ['Option 1', 'opt1'],
                ['Option 2', 'opt2']
            ]), 'OPTION');
        
        // Ou valor numérico
        this.appendValueInput('VALUE')
            .setCheck('Number')
            .appendField("Value:");
        
        // Define tipo do bloco
        this.setPreviousStatement(true);  // Pode ser conectado acima
        this.setNextStatement(true);      // Pode ser conectado abaixo
        
        // OU para blocos de valor:
        // this.setOutput(true, 'Number');
        
        // Dica de uso
        this.setTooltip("Description of what this block does");
    }
};

// Gerador de código Arduino
ArduinoGen.forBlock['custom_block_name'] = function(block, generator) {
    // Obtém valores dos campos
    var option = block.getFieldValue('OPTION');
    var value = generator.valueToCode(block, 'VALUE', generator.ORDER_NONE) || '0';
    
    // Gera código
    var code = `// Generated code for option ${option} with value ${value}\n`;
    
    return code;
};