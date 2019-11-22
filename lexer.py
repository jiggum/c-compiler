import sys
import ply.lex as lex

class Lexer:
  def __init__(self, **kw):
    self.debug = kw.get('debug', 0)
    self.lexer = lex.lex(module=self, debug=self.debug)

  def run(self, source):
    f = open(source, 'r')
    lines = f.readlines()
    data = ''.join(lines)
    self.lexer.input(data)
    for token in self.lexer:
      print(token)

  tokens = (
    # Reserved
    'BREAK',
    'CHAR',
    'CONTINUE',
    'ELSE',
    'FLOAT',
    'FOR',
    'IF',
    'INT',
    'RETURN',
    'VOID',
    'WHILE',

    # Special characters
    'COMMA',
    'SEMICOLON',
    'PAREN_L',
    'PAREN_R',
    'BRACKET_L',
    'BRACKET_R',
    'BRACE_L',
    'BRACE_R',
    'ASSIGN',
    'ASSIGN_PLUS',
    'ASSIGN_MINUS',
    'ASSIGN_TIME',
    'ASSIGN_DIVIDE',
    'ASSIGN_MODULO',
    'PLUS',
    'MINUS',
    'DIVIDE',
    'MODULO',
    'DOUBLE_PLUS',
    'DOUBLE_MINUS',
    'DOUBLE_AMPERSAND',
    'DOUBLE_PIPE',
    'GREATER',
    'LESS',
    'EQ',
    'NOT_EQ',
    'GREATER_EQ',
    'LESS_EQ',
    'ASTERISK',
    'AMPERSAND',

    # Variable tokens
    'ID',
    'NUMBER',
    'STRING',
    'CHARACTER',
  )

  reserved = {
    'break': 'BREAK',
    'char': 'CHAR',
    'continue': 'CONTINUE',
    'else': 'ELSE',
    'float': 'FLOAT',
    'for': 'FOR',
    'if': 'IF',
    'int': 'INT',
    'return': 'RETURN',
    'void': 'VOID',
    'while': 'WHILE'
  }

  # Tokens

  t_COMMA = r','
  t_SEMICOLON = r';'
  t_PAREN_L = r'\('
  t_PAREN_R = r'\)'
  t_BRACKET_L = r'\['
  t_BRACKET_R = r'\]'
  t_BRACE_L = r'{'
  t_BRACE_R = r'}'
  t_ASSIGN = r'='
  t_ASSIGN_PLUS = r'\+='
  t_ASSIGN_MINUS = r'-='
  t_ASSIGN_TIME = r'\*='
  t_ASSIGN_DIVIDE = r'/='
  t_ASSIGN_MODULO = r'%='
  t_PLUS = r'\+'
  t_MINUS = r'-'
  t_DIVIDE = r'/(?!\*)'
  t_MODULO = r'%'
  t_DOUBLE_PLUS = r'\+\+'
  t_DOUBLE_MINUS = r'--'
  t_DOUBLE_AMPERSAND = r'&&'
  t_DOUBLE_PIPE = r'\|\|'
  t_GREATER = r'>'
  t_LESS = r'<'
  t_EQ = r'=='
  t_NOT_EQ = r'!='
  t_GREATER_EQ = r'>='
  t_LESS_EQ = r'<='
  t_ASTERISK = r'\*'
  t_AMPERSAND = r'&'

  def t_ID(self, t):
    r'[a-zA-Z_]\w*'
    t.type = self.reserved.get(t.value, 'ID')
    return t

  def t_NUMBER(self, t):
    r'(([1-9]\d*)|0(?!\d))(.\d*[1-9])?'
    return t

  def t_CHARACTER(self, t):
    r"'\w'"
    return t

  def t_STRING(self, t):
    r'".*(?<!\\)"'
    return t

  def t_whitespace(self, t):
    r'[ \t]+'
    pass

  def t_newline(self, t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

  def t_remark(self, t):
    r'/\*.*\*/|(//.*$)'
    t.lineno += t.value.count('\n')
    pass

  def t_error(self, t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# if __name__ == '__main__':
#     src_path = sys.argv[1]
#     lexer = Lexer(debug=True)
#     lexer.run(src_path)
