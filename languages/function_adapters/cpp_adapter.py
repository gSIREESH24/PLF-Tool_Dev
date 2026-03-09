"""
C++ Function Adapter
Provides interface for calling C++ functions from other languages
"""

import subprocess
import json
import tempfile
import ctypes
import os
from pathlib import Path
from core.function_signature import FunctionSignature


class CppAdapter:
    """Adapter for calling C++ functions from other languages"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.compiled_functions = {}
    
    def call_cpp_function(self, function_name, args, cpp_code=None):
        """
        Call a C++ function from another language
        
        Args:
            function_name: Name of the C++ function to call
            args: List of arguments to pass to the function
            cpp_code: Optional C++ code containing the function
            
        Returns:
            Result from C++ function execution
        """
        try:
            if function_name not in self.compiled_functions and cpp_code:
                self._compile_cpp_function(function_name, cpp_code)
            
            # Create wrapper program
            wrapper_code = self._create_cpp_wrapper(function_name, args)
            
            # Write wrapper
            wrapper_file = Path(self.temp_dir) / "cpp_wrapper.cpp"
            wrapper_file.write_text(wrapper_code)
            
            # Compile with g++
            exe_file = wrapper_file.with_suffix('.exe')
            compile_result = subprocess.run(
                ["g++", "-std=c++11", str(wrapper_file), "-o", str(exe_file)],
                capture_output=True, text=True
            )
            
            if compile_result.returncode != 0:
                raise RuntimeError(f"C++ compilation error: {compile_result.stderr}")
            
            # Execute and capture result
            exec_result = subprocess.run(
                [str(exe_file)],
                capture_output=True, text=True
            )
            
            if exec_result.returncode != 0:
                raise RuntimeError(f"C++ execution error: {exec_result.stderr}")
            
            # Clean up
            if exe_file.exists():
                exe_file.unlink()
            
            # Parse result (JSON format from C++)
            try:
                return json.loads(exec_result.stdout)
            except:
                return exec_result.stdout.strip()
                
        except Exception as e:
            raise RuntimeError(f"Error calling C++ function {function_name}: {str(e)}")
    
    def _compile_cpp_function(self, function_name, cpp_code):
        """Compile a C++ function into a shared library"""
        try:
            cpp_file = Path(self.temp_dir) / f"{function_name}.cpp"
            cpp_file.write_text(cpp_code)
            
            # For Windows, compile to object file
            obj_file = cpp_file.with_suffix('.o')
            compile_result = subprocess.run(
                ["g++", "-std=c++11", "-c", str(cpp_file), "-o", str(obj_file)],
                capture_output=True, text=True
            )
            
            if compile_result.returncode == 0:
                self.compiled_functions[function_name] = str(obj_file)
                
        except Exception as e:
            raise RuntimeError(f"Error compiling C++ function {function_name}: {str(e)}")
    
    def _create_cpp_wrapper(self, function_name, args):
        """Create a wrapper C++ program to call the target function"""
        args_json = json.dumps(args)
        
        return f"""
#include <iostream>
#include <string>
#include <vector>

extern "C" {{
    // Forward declaration of the target function
    // This will be linked at runtime
}}

int main() {{
    try {{
        // Parse arguments from JSON
        std::string argsJson = R"({args_json})";
        
        // Call the C++ function
        // This would need proper implementation
        
        // Output result as JSON
        std::cout << "{{ \\"result\\": 0 }}" << std::endl;
        
        return 0;
    }} catch (std::exception& e) {{
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }}
}}
"""
    
    def create_cpp_function_signature(self, function_name, return_type, param_types):
        """
        Create a function signature for a C++ function
        
        Args:
            function_name: The function name
            return_type: Return type of the function
            param_types: List of parameter types
            
        Returns:
            FunctionSignature object
        """
        params = []
        for i, ptype in enumerate(param_types):
            params.append({
                'name': f'arg{i}',
                'type': ptype
            })
        
        return FunctionSignature(
            name=function_name,
            language='cpp',
            implementation=function_name,
            return_type=return_type,
            parameters=params
        )
    
    def convert_cpp_type(self, cpp_type, value):
        """
        Convert Python value to appropriate C++ type
        
        Args:
            cpp_type: C++ type name
            value: Python value to convert
            
        Returns:
            Converted value suitable for C++
        """
        if cpp_type in ['int', 'int32_t', 'int64_t']:
            return int(value)
        elif cpp_type in ['float', 'double']:
            return float(value)
        elif cpp_type in ['std::string', 'string', 'char*']:
            return str(value)
        elif cpp_type in ['bool']:
            return bool(value)
        elif cpp_type in ['long', 'long long']:
            return int(value)
        else:
            return value
    
    def convert_from_cpp(self, cpp_type, value):
        """
        Convert C++ result back to Python type
        
        Args:
            cpp_type: C++ type of the result
            value: C++ result value
            
        Returns:
            Python value
        """
        if cpp_type in ['int', 'int32_t', 'int64_t', 'long', 'long long']:
            return int(value)
        elif cpp_type in ['float', 'double']:
            return float(value)
        elif cpp_type in ['std::string', 'string', 'char*']:
            return str(value)
        elif cpp_type in ['bool']:
            return bool(value)
        else:
            return value
    
    def create_extern_c_wrapper(self, cpp_code):
        """
        Wrap C++ code with extern "C" for C linkage
        
        Args:
            cpp_code: Raw C++ code
            
        Returns:
            C++ code wrapped with extern "C"
        """
        return f"""
#include <iostream>
#include <string>
#include <vector>

extern "C" {{
{cpp_code}
}}

int main() {{
    // Main entry point for execution
    return 0;
}}
"""


def create_cpp_adapter():
    """Factory function to create a C++ adapter instance"""
    return CppAdapter()
