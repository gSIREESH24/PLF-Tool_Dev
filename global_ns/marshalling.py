from typing import Any, Dict, Callable
import json

class Marshaller:
    TYPE_MAP = {'int': int, 'float': float, 'str': str, 'bool': bool, 'list': list, 'dict': dict, 'number': float, 'string': str, 'boolean': bool, 'array': list, 'object': dict, 'integer': int, 'double': float, 'char*': str, 'void': type(None), 'Integer': int, 'Double': float, 'String': str, 'Boolean': bool, 'ArrayList': list, 'HashMap': dict, 'Long': int, 'Float': float, 'Short': int, 'Byte': int, 'int32_t': int, 'int64_t': int, 'std::string': str, 'std::vector': list, 'std::map': dict, 'std::unordered_map': dict, 'null': type(None), 'none': type(None)}

    @staticmethod
    def python_to_js(value: Any) -> Any:
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
        if value is None:
            return None
        else:
            return value

    @staticmethod
    def python_to_c(value: Any) -> Any:
        if value is None:
            return 'NULL'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, (list, tuple)):
            elements = [Marshaller.python_to_c(v) for v in value]
            return '{' + ', '.join((str(e) for e in elements)) + '}'
        else:
            return str(value)

    @staticmethod
    def c_to_python(value: Any) -> Any:
        if isinstance(value, str):
            if value.lower() == 'null':
                return None
            elif value.lower() in ('true', 'false'):
                return value.lower() == 'true'
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
        if type_hint is None:
            return True
        type_hint_lower = type_hint.lower()
        if type_hint_lower in ('int', 'integer'):
            return isinstance(value, int) and (not isinstance(value, bool))
        elif type_hint_lower in ('float', 'double'):
            return isinstance(value, (int, float)) and (not isinstance(value, bool))
        elif type_hint_lower in ('str', 'string'):
            return isinstance(value, str)
        elif type_hint_lower in ('bool', 'boolean'):
            return isinstance(value, bool)
        elif type_hint_lower in ('list', 'array'):
            return isinstance(value, (list, tuple))
        elif type_hint_lower in ('dict', 'object', 'map'):
            return isinstance(value, dict)
        elif type_hint_lower in ('none', 'null'):
            return value is None
        return True

    @staticmethod
    def infer_type(value: Any) -> str:
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'str'
        elif isinstance(value, (list, tuple)):
            return 'list'
        elif isinstance(value, dict):
            return 'dict'
        else:
            return 'any'

class TypeConverter:

    def __init__(self):
        self.converters: Dict[tuple, Callable] = {('python', 'javascript'): Marshaller.python_to_js, ('javascript', 'python'): Marshaller.js_to_python, ('python', 'c'): Marshaller.python_to_c, ('c', 'python'): Marshaller.c_to_python, ('python', 'java'): Marshaller.python_to_java, ('java', 'python'): Marshaller.java_to_python, ('python', 'cpp'): Marshaller.python_to_cpp, ('c++', 'python'): Marshaller.cpp_to_python, ('python', 'c++'): Marshaller.python_to_cpp, ('cpp', 'python'): Marshaller.cpp_to_python}

    def convert(self, value: Any, from_lang: str, to_lang: str) -> Any:
        if from_lang == to_lang:
            return value
        from_lang_norm = self._normalize_lang(from_lang)
        to_lang_norm = self._normalize_lang(to_lang)
        if from_lang_norm == to_lang_norm:
            return value
        key = (from_lang_norm, to_lang_norm)
        if key in self.converters:
            return self.converters[key](value)
        if from_lang_norm != 'python':
            value = self.convert(value, from_lang_norm, 'python')
        if to_lang_norm != 'python':
            value = self.convert(value, 'python', to_lang_norm)
        return value

    @staticmethod
    def _normalize_lang(lang: str) -> str:
        lang_lower = lang.lower().strip()
        if lang_lower in ('c++', 'cpp', 'cplusplus'):
            return 'cpp'
        elif lang_lower in ('js', 'javascript', 'ts', 'typescript'):
            return 'javascript'
        elif lang_lower in ('c', 'c#', 'csharp'):
            return 'c'
        elif lang_lower in ('java', 'jvm'):
            return 'java'
        elif lang_lower == 'python':
            return 'python'
        return lang_lower

    def register_converter(self, from_lang: str, to_lang: str, converter: Callable[[Any], Any]) -> None:
        from_norm = self._normalize_lang(from_lang)
        to_norm = self._normalize_lang(to_lang)
        self.converters[from_norm, to_norm] = converter

    def get_supported_conversions(self) -> Dict[tuple, str]:
        return {key: f'{key[0]} → {key[1]}' for key in self.converters.keys()}

    def is_conversion_supported(self, from_lang: str, to_lang: str) -> bool:
        from_norm = self._normalize_lang(from_lang)
        to_norm = self._normalize_lang(to_lang)
        if from_norm == to_norm:
            return True
        return (from_norm, to_norm) in self.converters
_converter: TypeConverter = None

def get_converter() -> TypeConverter:
    global _converter
    if _converter is None:
        _converter = TypeConverter()
    return _converter

def convert(value: Any, from_lang: str, to_lang: str) -> Any:
    return get_converter().convert(value, from_lang, to_lang)
