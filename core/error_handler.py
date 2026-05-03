"""Enhanced error handling with user-friendly messages."""
import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class ArduinoError:
    """Represents a parsed Arduino compilation error."""
    message: str
    line: int = 0
    column: int = 0
    error_type: str = "compilation"
    suggestion: str = ""
    related_blocks: List[str] = field(default_factory=list)
    severity: str = "error"  # error, warning, info


class ErrorHandler:
    """Parse and enhance Arduino error messages."""
    
    # Common error patterns with friendly messages
    ERROR_PATTERNS = [
        {
            'pattern': r"'(\w+)' was not declared in this scope",
            'message': "Variable or function '{match1}' is not defined",
            'suggestion': "Add a 'Create variable' block for '{match1}' before using it",
            'block_type': 'variable'
        },
        {
            'pattern': r"expected ';' before",
            'message': "Missing semicolon in generated code",
            'suggestion': "Check your blocks - some block might be incomplete",
            'block_type': 'syntax'
        },
        {
            'pattern': r"pinMode.*not declared",
            'message': "pinMode function not available for this board",
            'suggestion': "This board might need different pin configuration",
            'block_type': 'pin'
        },
        {
            'pattern': r"undefined reference to",
            'message': "Missing function definition",
            'suggestion': "Create a function block for this call",
            'block_type': 'function'
        },
        {
            'pattern': r"stk500.*not in sync",
            'message': "Upload failed - Board not responding",
            'suggestion': "1. Check USB connection\n2. Select correct port\n3. Try pressing reset button before upload",
            'block_type': 'upload',
            'severity': 'error'
        },
        {
            'pattern': r"avrdude: ser_open\(\): can't open device",
            'message': "Serial port access denied",
            'suggestion': "Close other programs using the serial port (Arduino IDE, other monitors)",
            'block_type': 'upload'
        },
        {
            'pattern': r"Board.*not available",
            'message': "Board package not installed",
            'suggestion': "Install board support via Arduino CLI: arduino-cli core install {fqbn}",
            'block_type': 'board'
        },
        {
            'pattern': r"'Serial' was not declared",
            'message': "Serial communication not available",
            'suggestion': "Add 'Start Serial' block at the beginning",
            'block_type': 'serial'
        },
        {
            'pattern': r"OUT_OF_MEMORY",
            'message': "Not enough memory for this program",
            'suggestion': "Try:\n- Reduce number of blocks\n- Use smaller data types\n- Remove unnecessary Serial prints",
            'block_type': 'memory'
        },
        {
            'pattern': r"invalid conversion from",
            'message': "Type mismatch in block connection",
            'suggestion': "Check that connected blocks use compatible data types",
            'block_type': 'type'
        }
    ]
    
    @classmethod
    def parse_error(cls, error_output: str, fqbn: str = "") -> ArduinoError:
        """Parse Arduino error and return user-friendly version."""
        
        # Try to match known patterns
        for pattern_info in cls.ERROR_PATTERNS:
            match = re.search(pattern_info['pattern'], error_output, re.IGNORECASE)
            if match:
                # Build message with matched groups
                message = pattern_info['message']
                for i, group in enumerate(match.groups(), 1):
                    message = message.replace(f'{{match{i}}}', group)
                
                suggestion = pattern_info['suggestion']
                if '{fqbn}' in suggestion and fqbn:
                    suggestion = suggestion.replace('{fqbn}', fqbn)
                
                return ArduinoError(
                    message=message,
                    error_type=pattern_info.get('block_type', 'general'),
                    suggestion=suggestion,
                    severity=pattern_info.get('severity', 'error'),
                    line=cls._extract_line_number(error_output)
                )
        
        # Generic error - try to extract meaningful parts
        lines = error_output.strip().split('\n')
        error_lines = [l for l in lines if 'error:' in l.lower()]
        
        if error_lines:
            return ArduinoError(
                message=error_lines[0][:200],  # Limit length
                error_type='unknown',
                suggestion="Check your blocks or try a simpler program",
                line=cls._extract_line_number(error_output)
            )
        
        return ArduinoError(
            message="Unknown compilation error",
            error_type='unknown',
            suggestion="Verify all blocks are properly connected",
            line=0
        )
    
    @classmethod
    def _extract_line_number(cls, output: str) -> int:
        """Extract line number from error output."""
        match = re.search(r':(\d+):', output)
        if match:
            return int(match.group(1))
        
        match = re.search(r'line (\d+)', output, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return 0
    
    @classmethod
    def get_friendly_message(cls, error: ArduinoError) -> str:
        """Get user-friendly error message with formatting."""
        severity_icon = {
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }.get(error.severity, '❗')
        
        lines = [
            f"{severity_icon} {error.message}",
            ""
        ]
        
        if error.suggestion:
            lines.append(f"💡 Suggestion: {error.suggestion}")
        
        if error.line > 0:
            lines.append(f"📍 Location: ~ line {error.line}")
        
        if error.related_blocks:
            blocks_str = ', '.join(error.related_blocks[:3])
            lines.append(f"🧩 Related blocks: {blocks_str}")
        
        return '\n'.join(lines)
    
    @classmethod
    def analyze_blocks_for_errors(cls, workspace_xml: str) -> List[ArduinoError]:
        """Analyze blocks for potential errors before compilation."""
        potential_errors = []
        
        # Simple checks without full parsing
        if 'ab_pin_mode' in workspace_xml:
            # Check if pin number is valid
            import re
            pins = re.findall(r'<field name="PIN">(\d+)</field>', workspace_xml)
            for pin in pins:
                pin_num = int(pin)
                if pin_num > 13 and pin_num not in [0, 1]:  # Pin 0/1 are special
                    potential_errors.append(ArduinoError(
                        message=f"Pin {pin_num} may not be available on all boards",
                        severity="warning",
                        suggestion="Consider using pins 0-13 for better compatibility"
                    ))
        
        # Check for missing setup
        if 'ab_program' in workspace_xml and 'ab_pin_mode' not in workspace_xml:
            # Check if there are digital writes without pin setup
            if 'ab_digital_write' in workspace_xml:
                potential_errors.append(ArduinoError(
                    message="Digital write used without pin setup",
                    suggestion="Add a 'pinMode' block in the Setup section",
                    severity="warning"
                ))
        
        # Check for infinite loops (potentially)
        if 'ab_while' in workspace_xml and 'controls_if' not in workspace_xml:
            potential_errors.append(ArduinoError(
                message="While loop may run forever without exit condition",
                suggestion="Add an IF condition or break block inside the loop",
                severity="info"
            ))
        
        return potential_errors


class UploadErrorHandler:
    """Handle upload-specific errors with retry suggestions."""
    
    @staticmethod
    def handle_upload_error(error_msg: str, port: str) -> Dict:
        """Analyze upload error and provide recovery steps."""
        
        error_lower = error_msg.lower()
        
        if "access denied" in error_lower or "permission denied" in error_lower:
            return {
                "can_retry": True,
                "suggestions": [
                    "Close other programs using the serial port",
                    "Check if you have permission to access the port",
                    "Try running as administrator (Windows) or add to dialout group (Linux)"
                ],
                "auto_fix": None
            }
        
        if "not in sync" in error_lower or "stk500" in error_lower:
            return {
                "can_retry": True,
                "suggestions": [
                    "Press the reset button on your Arduino just before uploading",
                    "Check that you selected the correct board type",
                    "Try disconnecting and reconnecting the USB cable"
                ],
                "auto_fix": "reset_and_retry"
            }
        
        if "timeout" in error_lower:
            return {
                "can_retry": True,
                "suggestions": [
                    "Check USB connection",
                    "Try a different USB port",
                    "Restart your computer if the issue persists"
                ],
                "auto_fix": None
            }
        
        return {
            "can_retry": False,
            "suggestions": [
                "Verify board is connected and powered",
                "Check that the correct port is selected",
                "Try uploading from Arduino IDE to test the board"
            ],
            "auto_fix": None
        }