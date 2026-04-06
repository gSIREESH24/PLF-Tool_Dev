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
    # Add to_json method for serialization
    lines.append('    std::string to_json() const {')
    lines.append('        std::string json = "{";')
    for i, field in enumerate(cls_def.fields):
        if i > 0:
            lines.append('        json += ", ";')
        if field.type_hint == 'string':
            lines.append(f'        json += "\\"{field.name}\\": \\"" + {field.name} + "\\"";')
        else:
            lines.append(f'        json += "\\"{field.name}\\": " + std::to_string({field.name});')
    lines.append('        json += "}";')
    lines.append('        return json;')
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
    # Add toJson method for serialization
    lines.append('    public String toJson() {')
    lines.append('        StringBuilder json = new StringBuilder("{");')
    for i, field in enumerate(cls_def.fields):
        if i > 0:
            lines.append('        json.append(", ");')
        if field.type_hint == 'string':
            lines.append(f'        json.append("\\"{field.name}\\": \\\"" + this.{field.name} + "\\\"");')
        else:
            lines.append(f'        json.append("\\"{field.name}\\": " + this.{field.name});')
    lines.append('        json.append("}");')
    lines.append('        return json.toString();')
    lines.append('    }')
    lines.append('}')
    return '\n'.join(lines) + '\n'

def generate_c_struct(cls_def: ClassDefinition) -> str:
    lines = [f'typedef struct {{']
    for field in cls_def.fields:
        t = 'char*' if field.type_hint == 'string' else field.type_hint
        lines.append(f'    {t} {field.name};')
    lines.append(f'}} {cls_def.name};')
    # Add serialization helper function
    lines.append(f'\nchar* {cls_def.name}_to_json({cls_def.name} obj) {{')
    lines.append('    char* json = (char*)malloc(1024);')
    lines.append('    strcpy(json, "{");')
    for i, field in enumerate(cls_def.fields):
        if i > 0:
            lines.append('    strcat(json, ", ");')
        if field.type_hint == 'string':
            lines.append(f'    strcat(json, "\\"{field.name}\\": \\\"");')
            lines.append(f'    strcat(json, obj.{field.name});')
            lines.append('    strcat(json, "\\\"");')
        else:
            lines.append(f'    strcat(json, "\\"{field.name}\\": ");')
            lines.append(f'    char buf[32]; sprintf(buf, "%f", obj.{field.name}); strcat(json, buf);')
    lines.append('    strcat(json, "}");')
    lines.append('    return json;')
    lines.append('}')
    return '\n'.join(lines) + '\n'
