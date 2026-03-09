"""
Type Marshalling System - Automatic type conversion between languages
Supports: Python, JavaScript, C, Java, C++
"""

from typing import Any, Dict, Callable
import json


class Marshaller:
    """
    Base class for language-specific marshalling.
    Handles conversion of values between Python, JavaScript, C, Java, and C++ types.
    """
    
    # Type mapping for all 5 languages
    TYPE_MAP = {
        # Python types
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "list": list,
        "dict": dict,
        # JavaScript/TypeScript types
        "number": float,
        "string": str,
        "boolean": bool,
        "array": list,
        "object": dict,
        # C types
        "integer": int,
        "double": float,
        "char*": str,
        "void": type(None),
        # Java types
        "Integer": int,
        "Double": float,
        "String": str,
        "Boolean": bool,
        "ArrayList": list,
        "HashMap": dict,
        "Long": int,
        "Float": float,
        "Short": int,
        "Byte": int,
        # C++ types
        "int32_t": int,
        "int64_t": int,
        "std::string": str,
        "std::vector": list,
        "std::map": dict,
        "std::unordered_map": dict,
        # Common types
        "null": type(None),
        "none": type(None),
    }
    
    @staticmethod
    def python_to_js(value: Any) -> Any:
        """Convert Python types to JavaScript-compatible types"""
        if value is None:
            return None
        elif isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            return value
        elif isinstance(value, (list, tuple)):
            return [Marshaller.python_to_js(v) for v in value]
        elif isinstance(value, dict):
            return {k: Marshaller.python_to_js(v) for k, v in value.items()}
        else:
            try:
                return str(value)
            except:
                return None
    
    @staticmethod
    def js_to_python(value: Any) -> Any:
        """Convert JavaScript types to Python-compatible types"""
        if value is None:
            return None
        else:
            return value
    
    @staticmethod
    def python_to_c(value: Any) -> Any:
        """Convert Python types to C-compatible types"""
        if value is None:
            return "NULL"
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, (list, tuple)):
            elements = [Marshaller.python_to_c(v) for v in value]
            return "{" + ", ".join(str(e) for e in elements) + "}"
        else:
            return str(value)
    
    @staticmethod
    def c_to_python(value: Any) -> Any:
        """Convert C types back to Python"""
        if isinstance(value, str):
            if value.lower() == "null":
                return None
            elif value.lower() in ("true", "false"):
                return value.lower() == "true"
            try:
                return int(value)
            except ValueError:
                try:
                    return float(value)
                except ValueError:
                    return value
        return value
    
    @staticmethod
    def python_to_java(value: Any) -> Any:
        """Convert Python types to Java-compatible types"""
        if value is None:
            return None
        elif isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return value
        elif isinstance(value, float):
            return float(value)
        elif isinstance(value, str):
            return value
        elif isinstance(value, (list, tuple)):
            return [Marshaller.python_to_java(v) for v in value]
        elif isinstance(value, dict):
            return {k: Marshaller.python_to_java(v) for k, v in value.items()}
        else:
            try:
                return str(value)
            except:
                return None
    
    @staticmethod
    def java_to_python(value: Any) -> Any:
        """Convert Java types back to Python"""
        if value is None:
            return None
        elif isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return int(value)
        elif isinstance(value, float):
            return float(value)
        elif isinstance(value, str):
            return value
        elif isinstance(value, (list, tuple)):
            return [Marshaller.java_to_python(v) for v in value]
        elif isinstance(value, dict):
            return {k: Marshaller.java_to_python(v) for k, v in value.items()}
        return value
    
    @staticmethod
    def python_to_cpp(value: Any) -> Any:
        """Convert Python types to C++-compatible types"""
        if value is None:
            return None
        elif isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            return value
        elif isinstance(value, (list, tuple)):
            return [Marshaller.python_to_cpp(v) for v in value]
        elif isinstance(value, dict):
            return {k: Marshaller.python_to_cpp(v) for k, v in value.items()}
        else:
            try:
                return str(value)
            except:
                return None
    
    @staticmethod
    def cpp_to_python(value: Any) -> Any:
        """Convert C++ types back to Python"""
        if value is None:
            return None
        elif isinstance(value, bool):
            return value
        elif isinstance(value, int):
            return int(value)
        elif isinstance(value, float):
            return float(value)
        elif isinstance(value, str):
            return value
        elif isinstance(value, (list, tuple)):
            return [Marshaller.cpp_to_python(v) for v in value]
        elif isinstance(value, dict):
            return {k: Marshaller.cpp_to_python(v) for k, v in value.items()}
        return value
    
    @staticmethod
    def validate_type(value: Any, type_hint: str) -> bool:
        """
        Check if a value matches the expected type hint.
        
        Args:
            value: The value to check
            type_hint: Type hint string (e.g., "int", "str", "list")
            
        Returns:
            True if value matches type_hint
        """
        if type_hint is None:
            return True
        
        type_hint_lower = type_hint.lower()
        
        if type_hint_lower in ("int", "integer"):
            return isinstance(value, int) and not isinstance(value, bool)
        elif type_hint_lower in ("float", "double"):
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        elif type_hint_lower in ("str", "string"):
            return isinstance(value, str)
        elif type_hint_lower in ("bool", "boolean"):
            return isinstance(value, bool)
        elif type_hint_lower in ("list", "array"):
            return isinstance(value, (list, tuple))
        elif type_hint_lower in ("dict", "object", "map"):
            return isinstance(value, dict)
        elif type_hint_lower in ("none", "null"):
            return value is None
        
        return True  # Unknown type, accept it
    
    @staticmethod
    def infer_type(value: Any) -> str:
        """
        Infer the type of a value.
        
        Args:
            value: The value to analyze
            
        Returns:
            Type hint string
        """
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "str"
        elif isinstance(value, (list, tuple)):
            return "list"
        elif isinstance(value, dict):
            return "dict"
        else:
            return "any"


class TypeConverter:
    """
    High-level type conversion between languages.
    Defines conversion paths and handles edge cases.
    Supports all 5 languages: Python, JavaScript, C, Java, C++
    
    Conversion Matrix (10 bidirectional pairs):
    - Python ↔ JavaScript
    - Python ↔ C
    - Python ↔ Java
    - Python ↔ C++
    - JavaScript ↔ Java
    - JavaScript ↔ C++
    - C ↔ Java
    - C ↔ C++
    """
    
    def __init__(self):
        """Initialize type converter with all language pairs"""
        self.converters: Dict[tuple, Callable] = {
            # Python conversions
            ("python", "javascript"): Marshaller.python_to_js,
            ("javascript", "python"): Marshaller.js_to_python,
            ("python", "c"): Marshaller.python_to_c,
            ("c", "python"): Marshaller.c_to_python,
            ("python", "java"): Marshaller.python_to_java,
            ("java", "python"): Marshaller.java_to_python,
            ("python", "cpp"): Marshaller.python_to_cpp,
            ("c++", "python"): Marshaller.cpp_to_python,
            ("python", "c++"): Marshaller.python_to_cpp,
            ("cpp", "python"): Marshaller.cpp_to_python,
        }
    
    def convert(self, value: Any, from_lang: str, to_lang: str) -> Any:
        """
        Convert a value from one language to another.
        Supports direct conversion between all language pairs.
        For non-direct pairs, uses indirect conversion through Python.
        
        Args:
            value: The value to convert
            from_lang: Source language (python, javascript, c, java, cpp, c++)
            to_lang: Target language (python, javascript, c, java, cpp, c++)
            
        Returns:
            Converted value
        """
        if from_lang == to_lang:
            return value
        
        # Normalize language names
        from_lang_norm = self._normalize_lang(from_lang)
        to_lang_norm = self._normalize_lang(to_lang)
        
        if from_lang_norm == to_lang_norm:
            return value
        
        # Check for direct converter
        key = (from_lang_norm, to_lang_norm)
        if key in self.converters:
            return self.converters[key](value)
        
        # Use indirect conversion through Python
        # Convert source → Python → target
        if from_lang_norm != "python":
            value = self.convert(value, from_lang_norm, "python")
        
        if to_lang_norm != "python":
            value = self.convert(value, "python", to_lang_norm)
        
        return value
    
    @staticmethod
    def _normalize_lang(lang: str) -> str:
        """
        Normalize language name to standard form.
        
        Args:
            lang: Language name (can be 'c++', 'cpp', 'javascript', 'js', etc.)
            
        Returns:
            Normalized language name
        """
        lang_lower = lang.lower().strip()
        
        # Aliases
        if lang_lower in ("c++", "cpp", "cplusplus"):
            return "cpp"
        elif lang_lower in ("js", "javascript", "ts", "typescript"):
            return "javascript"
        elif lang_lower in ("c", "c#", "csharp"):
            return "c"
        elif lang_lower in ("java", "jvm"):
            return "java"
        elif lang_lower == "python":
            return "python"
        
        return lang_lower
    
    def register_converter(self, from_lang: str, to_lang: str,
                          converter: Callable[[Any], Any]) -> None:
        """
        Register a custom type converter.
        
        Args:
            from_lang: Source language
            to_lang: Target language
            converter: Conversion function
        """
        from_norm = self._normalize_lang(from_lang)
        to_norm = self._normalize_lang(to_lang)
        self.converters[(from_norm, to_norm)] = converter
    
    def get_supported_conversions(self) -> Dict[tuple, str]:
        """
        Get all supported conversion pairs.
        
        Returns:
            Dictionary of supported conversions with descriptions
        """
        return {
            key: f"{key[0]} → {key[1]}"
            for key in self.converters.keys()
        }
    
    def is_conversion_supported(self, from_lang: str, to_lang: str) -> bool:
        """
        Check if a conversion is directly supported.
        
        Args:
            from_lang: Source language
            to_lang: Target language
            
        Returns:
            True if conversion is supported
        """
        from_norm = self._normalize_lang(from_lang)
        to_norm = self._normalize_lang(to_lang)
        
        if from_norm == to_norm:
            return True
        
        return (from_norm, to_norm) in self.converters


# Global type converter instance
_converter: TypeConverter = None


def get_converter() -> TypeConverter:
    """Get or create the global type converter"""
    global _converter
    if _converter is None:
        _converter = TypeConverter()
    return _converter


def convert(value: Any, from_lang: str, to_lang: str) -> Any:
    """
    Convenience function to convert a value between languages.
    
    Args:
        value: The value to convert
        from_lang: Source language
        to_lang: Target language
        
    Returns:
        Converted value
    """
    return get_converter().convert(value, from_lang, to_lang)
