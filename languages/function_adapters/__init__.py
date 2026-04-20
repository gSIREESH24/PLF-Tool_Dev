from .python_adapter import PythonAdapter, create_python_adapter
from .js_adapter import JavaScriptAdapter, create_js_adapter
from .c_adapter import CAdapter, create_c_adapter
from .java_adapter import JavaAdapter, create_java_adapter
from .cpp_adapter import CppAdapter, create_cpp_adapter
__all__ = ['PythonAdapter', 'JavaScriptAdapter', 'CAdapter', 'JavaAdapter', 'CppAdapter', 'create_python_adapter', 'create_js_adapter', 'create_c_adapter', 'create_java_adapter', 'create_cpp_adapter']
ADAPTER_REGISTRY = {'python': create_python_adapter, 'javascript': create_js_adapter, 'c': create_c_adapter, 'java': create_java_adapter, 'cpp': create_cpp_adapter}

def get_adapter(language):
    if language not in ADAPTER_REGISTRY:
        raise ValueError(f'Unsupported language: {language}. Supported: {list(ADAPTER_REGISTRY.keys())}')
    factory = ADAPTER_REGISTRY[language]
    return factory()
