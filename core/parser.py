import textwrap
from core.ast import BlockNode, ProgramNode

def parse(source_code):
    lines = source_code.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith('--') or stripped.startswith('#'):
            i += 1
            continue
        if stripped.endswith('{'):
            current_lang = stripped[:-1].strip().lower()
            if current_lang == 'global':
                i += 1
                global_content = []
                brace_depth = 1
                while i < len(lines) and brace_depth > 0:
                    line = lines[i]
                    stripped = line.strip()
                    brace_depth += stripped.count('{')
                    brace_depth -= stripped.count('}')
                    if brace_depth > 0:
                        global_content.append(line)
                    i += 1
                nested_blocks = parse_global_content(global_content)
                blocks.extend(nested_blocks)
            else:
                i += 1
                block_content = []
                brace_depth = 1
                while i < len(lines) and brace_depth > 0:
                    line = lines[i]
                    stripped = line.strip()
                    brace_depth += stripped.count('{')
                    brace_depth -= stripped.count('}')
                    if brace_depth > 0:
                        block_content.append(line)
                    i += 1
                cleaned = textwrap.dedent('\n'.join(block_content))
                blocks.append(BlockNode(current_lang, cleaned, is_global=False))
        else:
            i += 1
    return ProgramNode(blocks)

def parse_global_content(global_lines):
    from core.class_registry import ClassDefinition, ClassField, get_class_registry
    blocks = []
    current_lang = None
    current_code = []
    inside_lang_block = False
    brace_depth = 0
    global_vars = []
    i = 0
    while i < len(global_lines):
        line = global_lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith('--') or stripped.startswith('#'):
            i += 1
            continue
        if not inside_lang_block and stripped.startswith('class ') and stripped.endswith('{'):
            parts = stripped.split()
            class_name = parts[1]
            fields = []
            i += 1
            inner_depth = 1
            while i < len(global_lines) and inner_depth > 0:
                inner_line = global_lines[i].strip()
                if inner_line == '}':
                    inner_depth -= 1
                    break
                elif inner_line:
                    inner_line = inner_line.rstrip(';')
                    f_parts = inner_line.split()
                    if len(f_parts) == 2:
                        fields.append(ClassField(name=f_parts[1], type_hint=f_parts[0]))
                i += 1
            reg = get_class_registry()
            reg.register(ClassDefinition(name=class_name, fields=fields))
            i += 1
            continue
        if not inside_lang_block and stripped.endswith('{'):
            current_lang = stripped[:-1].strip().lower()
            current_code = []
            inside_lang_block = True
            brace_depth = 1
            i += 1
            continue
        if inside_lang_block:
            brace_depth += stripped.count('{')
            brace_depth -= stripped.count('}')
            if brace_depth == 0:
                cleaned = textwrap.dedent('\n'.join(current_code))
                blocks.append(BlockNode(current_lang, cleaned, is_global=True))
                inside_lang_block = False
            else:
                current_code.append(line)
        elif '=' in stripped and (not stripped.startswith(('--', '#', '//'))):
            global_vars.append(stripped)
        i += 1
    if global_vars:
        var_code = '\n'.join(global_vars)
        blocks.insert(0, BlockNode('python', var_code, is_global=True))
    return blocks
