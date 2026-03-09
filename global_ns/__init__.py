"""
Global Namespace Package
Contains shared functions and utilities available to all languages
"""

from global_ns.marshalling import Marshaller, TypeConverter, get_converter, convert
from global_ns.builtins import register_builtins

__all__ = [
    "Marshaller",
    "TypeConverter",
    "get_converter",
    "convert",
    "register_builtins"
]
