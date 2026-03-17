import textwrap
from core.ast import BlockNode, ProgramNode

def parse(source_code):
    lines = source_code.splitlines()
    blocks = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if not stripped or stripped.startswith("--") or stripped.startswith("#"):
            i += 1
            continue
        
        if stripped.endswith("{"):
            current_lang = stripped[:-1].strip().lower()
            
            if current_lang == "global":
                i += 1
                global_content = []
                brace_depth = 1
                
                while i < len(lines) and brace_depth > 0:
                    line = lines[i]
                    stripped = line.strip()
                    
                    brace_depth += stripped.count("{")
                    brace_depth -= stripped.count("}")
                    
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
                    
                    brace_depth += stripped.count("{")
                    brace_depth -= stripped.count("}")
                    
                    if brace_depth > 0:
                        block_content.append(line)
                    
                    i += 1
                
                cleaned = textwrap.dedent("\n".join(block_content))
                blocks.append(BlockNode(current_lang, cleaned, is_global=False))
        else:
            i += 1

    return ProgramNode(blocks)

def parse_global_content(global_lines):
    """Parse language blocks and variables within a global block"""
    blocks = []
    current_lang = None
    current_code = []
    inside_lang_block = False
    brace_depth = 0
    global_vars = []

    for line in global_lines:
        stripped = line.strip()
        
        # Skip comments
        if not stripped or stripped.startswith("--") or stripped.startswith("#"):
            continue

        if not inside_lang_block and stripped.endswith("{"):
            current_lang = stripped[:-1].strip().lower()
            current_code = []
            inside_lang_block = True
            brace_depth = 1
            continue

        if inside_lang_block:
            brace_depth += stripped.count("{")
            brace_depth -= stripped.count("}")

            if brace_depth == 0:
                cleaned = textwrap.dedent("\n".join(current_code))
                blocks.append(BlockNode(current_lang, cleaned, is_global=True))
                inside_lang_block = False
            else:
                current_code.append(line)
        else:
            if "=" in stripped and not stripped.startswith(("--", "#", "//")):
                global_vars.append(stripped)

    if global_vars:
        var_code = "\n".join(global_vars)
        blocks.insert(0, BlockNode("python", var_code, is_global=True))

    return blocks