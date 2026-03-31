class BlockNode:

    def __init__(self, language, code, is_global=False):
        self.language = language
        self.code = code
        self.is_global = is_global

class ProgramNode:

    def __init__(self, blocks):
        self.blocks = blocks
