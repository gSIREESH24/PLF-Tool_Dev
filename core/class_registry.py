from typing import Dict, List, Optional
import json

class ClassField:

    def __init__(self, name: str, type_hint: str):
        self.name = name
        self.type_hint = type_hint

class ClassDefinition:

    def __init__(self, name: str, fields: List[ClassField]):
        self.name = name
        self.fields = fields

class ClassRegistry:

    def __init__(self):
        self.classes: Dict[str, ClassDefinition] = {}

    def register(self, definition: ClassDefinition):
        self.classes[definition.name] = definition

    def get(self, name: str) -> Optional[ClassDefinition]:
        return self.classes.get(name)

    def get_all(self) -> List[ClassDefinition]:
        return list(self.classes.values())
_class_registry = None

def get_class_registry() -> ClassRegistry:
    global _class_registry
    if _class_registry is None:
        _class_registry = ClassRegistry()
    return _class_registry

def generate_python_class(cls_def: ClassDefinition) -> str:
    lines = [f'class {cls_def.name}:']
    args = ', '.join([f'{f.name}' for f in cls_def.fields])
    lines.append(f'    def __init__(self, {args}):')
    for field in cls_def.fields:
        lines.append(f'        self.{field.name} = {field.name}')
    lines.append('    def to_dict(self):')
    lines.append('        return {')
    for field in cls_def.fields:
        lines.append(f"            '{field.name}': self.{field.name},")
    lines.append('        }')
    return '\n'.join(lines) + '\n'

def generate_js_class(cls_def: ClassDefinition) -> str:
    lines = [f'class {cls_def.name} {{']
    args = ', '.join([f'{f.name}' for f in cls_def.fields])
    lines.append(f'    constructor({args}) {{')
    for field in cls_def.fields:
        lines.append(f'        this.{field.name} = {field.name};')
    lines.append('    }')
    lines.append('}')
    return '\n'.join(lines) + '\n'

def generate_cpp_class(cls_def: ClassDefinition) -> str:
    lines = [f'class {cls_def.name} {{', 'public:']
    for field in cls_def.fields:
        t = 'std::string' if field.type_hint == 'string' else field.type_hint
        lines.append(f'    {t} {field.name};')
    args = ', '.join([f"{('std::string' if f.type_hint == 'string' else f.type_hint)} {f.name}_val" for f in cls_def.fields])
    lines.append(f'    {cls_def.name}({args}) {{')
    for field in cls_def.fields:
        lines.append(f'        {field.name} = {field.name}_val;')
    lines.append('    }')
    lines.append('};')
    return '\n'.join(lines) + '\n'

def generate_java_class(cls_def: ClassDefinition) -> str:
    lines = [f'class {cls_def.name} {{']
    for field in cls_def.fields:
        t = 'String' if field.type_hint == 'string' else field.type_hint
        lines.append(f'    public {t} {field.name};')
    args = ', '.join([f"{('String' if f.type_hint == 'string' else f.type_hint)} {f.name}_val" for f in cls_def.fields])
    lines.append(f'    public {cls_def.name}({args}) {{')
    for field in cls_def.fields:
        lines.append(f'        this.{field.name} = {field.name}_val;')
    lines.append('    }')
    lines.append('}')
    return '\n'.join(lines) + '\n'

def generate_c_struct(cls_def: ClassDefinition) -> str:
    lines = [f'typedef struct {{']
    for field in cls_def.fields:
        t = 'char*' if field.type_hint == 'string' else field.type_hint
        lines.append(f'    {t} {field.name};')
    lines.append(f'}} {cls_def.name};')
    return '\n'.join(lines) + '\n'
