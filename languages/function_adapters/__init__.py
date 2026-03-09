"""
Language Adapters Package
Provides adapters for calling functions across languages
Complete adapters for Python, JavaScript, C, Java, and C++
"""

# Import all language adapters
from .python_adapter import PythonAdapter, create_python_adapter
from .js_adapter import JavaScriptAdapter, create_js_adapter
from .c_adapter import CAdapter, create_c_adapter
from .java_adapter import JavaAdapter, create_java_adapter
from .cpp_adapter import CppAdapter, create_cpp_adapter

# Export all adapters and factory functions
__all__ = [
    # Adapter Classes
    "PythonAdapter",
    "JavaScriptAdapter",
    "CAdapter",
    "JavaAdapter",
    "CppAdapter",
    # Factory Functions
    "create_python_adapter",
    "create_js_adapter",
    "create_c_adapter",
    "create_java_adapter",
    "create_cpp_adapter",
]

# Convenience: Adapter registry for easy access
ADAPTER_REGISTRY = {
    'python': create_python_adapter,
    'javascript': create_js_adapter,
    'c': create_c_adapter,
    'java': create_java_adapter,
    'cpp': create_cpp_adapter,
}


def get_adapter(language):
    """
    Get an adapter instance for a specific language
    
    Args:
        language: Language name ('python', 'javascript', 'c', 'java', 'cpp')
        
    Returns:
        Adapter instance for the language
    """
    if language not in ADAPTER_REGISTRY:
        raise ValueError(f"Unsupported language: {language}. Supported: {list(ADAPTER_REGISTRY.keys())}")
    
    factory = ADAPTER_REGISTRY[language]
    return factory()

