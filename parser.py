import sys
import os
import ply.yacc as yacc
from lexer import Lexer

class Parser(Lexer):
  def __init__(self, **kw):
    super().__init__(**kw)
    self.names = {}
    print(self.tokens)
    try:
      modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
    except:
      modname = "parser" + "_" + self.__class__.__name__
    self.debugfile = modname + ".dbg"
    self.tabmodule = modname + "_" + "parsetab"

    yacc.yacc(
      module=self,
      debug=self.debug,
      debugfile=self.debugfile,
      tabmodule=self.tabmodule
    )

  def run(self, source):
    f = open(source, 'r')
    lines = f.readlines()
    data = ''.join(lines)
    yacc.parse(data)

  precedence = (
    ('left', 'EQ', 'NOT_EQ'),
    ('left', 'LESS', 'GREATER', 'LESS_EQ', 'GREATER_EQ'),
    ('left', 'PLUS', 'MINUS', 'DOUBLE_AMPERSAND', 'DOUBLE_PIPE'),
    ('left', 'ASTERISK', 'DIVIDE', 'MODULO'),
    ('right', 'IFS'),
    ('right', 'ELSE'),
  )

  # Section

  def p_root_section_opt_1(self, t):
    '''root_section_opt : empty'''

  def p_root_section_opt_2(self, t):
    '''root_section_opt : root_section'''

  def p_root_section_1(self, t):
    '''root_section : root_sector'''

  def p_root_section_2(self, t):
    '''root_section : root_section root_sector'''

  def p_root_sector(self, t):
    '''root_sector : declaration
                   | expression_statement
                   | conditional_statement
                   | loop_statement'''

  def p_section_wrapper(self, t):
    '''section_wrapper : BRACE_L section_opt BRACE_R'''

  def p_section_opt_1(self, t):
    '''section_opt : empty'''

  def p_section_opt_2(self, t):
    '''section_opt : section'''

  def p_section_1(self, t):
    '''section : sector'''

  def p_section_2(self, t):
    '''section : section sector'''

  def p_sector(self, t):
    '''sector : declaration
              | statement'''

  # Declaration

  def p_declaration(self, t):
    '''declaration : variable_declaration
                   | function_declaration'''

  def p_function_declaration(self, t):
    '''function_declaration : type function_declarator section_wrapper'''

  def p_function_declarator_1(self, t):
    '''function_declarator : function_simple_declarator'''

  def p_function_declarator_2(self, t):
    '''function_declarator : ASTERISK function_declarator'''

  def p_function_simple_declarator_1(self, t):
    '''function_simple_declarator : ID PAREN_L parameter_group PAREN_R'''

  def p_function_simple_declarator_2(self, t):
    '''function_simple_declarator : ID PAREN_L PAREN_R
                                  | ID PAREN_L VOID PAREN_R'''

  def p_variable_declaration(self, t):
    '''variable_declaration : type variable_declarator_group SEMICOLON'''

  def p_variable_declarator_group_1(self, t):
    '''variable_declarator_group : variable_declarator'''

  def p_variable_declarator_group_2(self, t):
    '''variable_declarator_group : variable_declarator_group COMMA variable_declarator'''

  def p_variable_declarator_1(self, t):
    '''variable_declarator : variable_simple_declarator'''

  def p_variable_declarator_2(self, t):
    '''variable_declarator : ASTERISK variable_declarator'''

  def p_variable_simple_declarator_1(self, t):
    '''variable_simple_declarator : ID'''

  def p_variable_simple_declarator_2(self, t):
    '''variable_simple_declarator : ID BRACKET_L NUMBER BRACKET_R'''

  def p_parameter_group_1(self, t):
    '''parameter_group : type variable_declarator'''

  def p_parameter_group_2(self, t):
    '''parameter_group : parameter_group COMMA type variable_declarator'''

  # Statement

  def p_statement(self, t):
    '''statement : expression_statement
                 | conditional_statement
                 | loop_statement
                 | jump_statement'''

  def p_expression_statement(self, t):
    '''expression_statement : expression SEMICOLON'''

  def p_conditional_statement_1(self, t):
    '''conditional_statement : IF PAREN_L expression PAREN_R section_wrapper %prec IFS'''

  def p_conditional_statement_2(self, t):
    '''conditional_statement : IF PAREN_L expression PAREN_R section_wrapper ELSE section_wrapper'''

  def p_loop_statement_1(self, t):
    '''loop_statement : WHILE PAREN_L expression PAREN_R section_wrapper'''

  def p_loop_statement_2(self, t):
    '''loop_statement : FOR PAREN_L expression_statement expression_statement expression PAREN_R section_wrapper'''

  def p_jump_statement_1(self, t):
    '''jump_statement : RETURN SEMICOLON'''

  def p_jump_statement_2(self, t):
    '''jump_statement : RETURN expression SEMICOLON'''

  def p_jump_statement_3(self, t):
    '''jump_statement : BREAK SEMICOLON'''

  def p_jump_statement_4(self, t):
    '''jump_statement : CONTINUE SEMICOLON'''

  # Expression

  def p_argument_expression_list_1(self, t):
    '''argument_expression_list : expression'''

  def p_argument_expression_list_2(self, t):
    '''argument_expression_list : argument_expression_list COMMA expression'''

  def p_expression(self, t):
    '''expression : additive_expression
                  | assign_expression'''

  def p_assign_expression(self, t):
    '''assign_expression : variable_expression ASSIGN expression
                         | variable_expression ASSIGN_PLUS expression
                         | variable_expression ASSIGN_MINUS expression
                         | variable_expression ASSIGN_TIME expression
                         | variable_expression ASSIGN_DIVIDE expression
                         | variable_expression ASSIGN_MODULO expression'''

  def p_additive_expression_1(self, t):
    '''additive_expression : unary_expression'''

  def p_additive_expression_2(self, t):
    '''additive_expression : additive_expression EQ unary_expression
                           | additive_expression NOT_EQ unary_expression
                           | additive_expression LESS unary_expression
                           | additive_expression GREATER unary_expression
                           | additive_expression LESS_EQ unary_expression
                           | additive_expression GREATER_EQ unary_expression
                           | additive_expression PLUS unary_expression
                           | additive_expression MINUS unary_expression
                           | additive_expression DOUBLE_AMPERSAND unary_expression
                           | additive_expression DOUBLE_PIPE unary_expression
                           | additive_expression ASTERISK unary_expression
                           | additive_expression DIVIDE unary_expression
                           | additive_expression MODULO unary_expression'''

  def p_unary_expression_1(self, t):
    '''unary_expression : function_expression
                        | const_expression'''

  def p_unary_expression_2(self, t):
    '''unary_expression : MINUS unary_expression'''

  def p_unary_expression_3(self, t):
    '''unary_expression : PLUS unary_expression'''

  def p_unary_expression_4(self, t):
    '''unary_expression : function_expression DOUBLE_PLUS
                        | function_expression DOUBLE_MINUS'''

  def p_unary_expression_5(self, t):
    '''unary_expression : DOUBLE_PLUS function_expression
                        | DOUBLE_MINUS function_expression'''

  def p_function_expression_1(self, t):
    '''function_expression : variable_expression'''

  def p_function_expression_2(self, t):
    '''function_expression : function_expression PAREN_L argument_expression_list PAREN_R'''

  def p_function_expression_3(self, t):
    '''function_expression : function_expression PAREN_L PAREN_R'''

  def p_variable_expression_1(self, t):
    '''variable_expression : variable_simpe_expression'''

  def p_variable_expression_2(self, t):
    '''variable_expression : ASTERISK variable_simpe_expression
                           | AMPERSAND variable_simpe_expression'''

  def p_variable_simpe_expression_1(self, t):
    '''variable_simpe_expression : ID'''

  def p_variable_simpe_expression_2(self, t):
    '''variable_simpe_expression : variable_simpe_expression BRACKET_L expression BRACKET_R'''

  def p_variable_simpe_expression_3(self, t):
    '''variable_simpe_expression : PAREN_L expression PAREN_R'''

  def p_const_expression_1(self, t):
    '''const_expression : NUMBER'''

  def p_const_expression_2(self, t):
    '''const_expression : CHARACTER'''

  def p_const_expression_3(self, t):
    '''const_expression : STRING'''

  # ETC

  def p_type(self, t):
    '''type : INT
            | FLOAT
            | VOID
            | CHAR'''

  def p_empty(self, t):
    'empty :'
    pass

  def p_error(self, t):
    print(t)
    print("Syntax Error at %d." % t.lineno)
    raise SyntaxError

if __name__ == '__main__':
    src_path = sys.argv[1]
    parser = Parser(debug=True)
    parser.run(src_path)