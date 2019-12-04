import sys
import os
import ply.yacc as yacc
from lexer import Lexer
import ast

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
    return yacc.parse(data)

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
    t[0] = ast.EmptyNode()

  def p_root_section_opt_2(self, t):
    '''root_section_opt : root_section'''
    t[0] = t[1]

  def p_root_section_1(self, t):
    '''root_section : root_sector'''
    t[0] = ast.RootSection(t[1], linespan=t[1].linespan)

  def p_root_section_2(self, t):
    '''root_section : root_section root_sector'''
    linespan = [t[1].linespan[0], t[2].linespan[1]]
    t[1].add(t[2])
    t[1].update_linespan(linespan)
    t[0] = t[1]

  def p_root_sector(self, t):
    '''root_sector : declaration
                   | expression_statement
                   | conditional_statement
                   | loop_statement'''
    t[0] = t[1]

  def p_section_wrapper(self, t):
    '''section_wrapper : BRACE_L section_opt BRACE_R'''
    linespan = [t.linespan(1)[0], t.linespan(3)[1]]
    t[2].update_linespan(linespan)
    t[0] = t[2]

  def p_section_opt_1(self, t):
    '''section_opt : empty'''
    pass

  def p_section_opt_2(self, t):
    '''section_opt : section'''
    t[0] = t[1]

  def p_section_1(self, t):
    '''section : sector'''
    t[0] = ast.Section(t[1], linespan=t[1].linespan)

  def p_section_2(self, t):
    '''section : section sector'''
    linespan = [t[1].linespan[0], t[2].linespan[1]]
    t[1].add(t[2])
    t[1].update_linespan(linespan)
    t[0] = t[1]

  def p_scopeless_section_wrapper(self, t):
    '''scopeless_section_wrapper : BRACE_L scopeless_section_opt BRACE_R'''
    linespan = [t.linespan(1)[0], t.linespan(3)[1]]
    t[2].update_linespan(linespan)
    t[0] = t[2]

  def p_scopeless_section_opt_1(self, t):
    '''scopeless_section_opt : empty'''
    pass

  def p_scopeless_section_opt_2(self, t):
    '''scopeless_section_opt : scopeless_section'''
    t[0] = t[1]

  def p_scopeless_section_1(self, t):
    '''scopeless_section : sector'''
    t[0] = ast.ScopelessSection(t[1], linespan=t[1].linespan)

  def p_scopeless_section_2(self, t):
    '''scopeless_section : scopeless_section sector'''
    linespan = [t.linespan(1)[0], t.linespan(2)[1]]
    t[1].add(t[2])
    t[1].update_linespan(linespan)
    t[0] = t[1]

  def p_sector(self, t):
    '''sector : declaration
              | statement'''
    t[0] = t[1]

  # Declaration

  def p_declaration(self, t):
    '''declaration : variable_declaration
                   | function_declaration'''
    t[0] = t[1]

  def p_function_declaration(self, t):
    '''function_declaration : type function_declarator section_wrapper'''
    t[2].add_type(t[1])
    linespan = [t[1].linespan[0], t[3].linespan[1]]
    t[0] = ast.FnDeclaration(t[2], t[3], linespan=linespan)

  def p_function_declarator_1(self, t):
    '''function_declarator : function_simple_declarator'''
    t[0] = t[1]

  def p_function_declarator_2(self, t):
    '''function_declarator : ASTERISK function_declarator'''
    linespan = [t.linespan(1)[0], t[2].linespan[1]]
    t[2].add_type(ast.TypeNode(t[1], linespan=linespan))
    t[0] = t[2]

  def p_function_simple_declarator_1(self, t):
    '''function_simple_declarator : ID PAREN_L parameter_group PAREN_R'''
    linespan = [t.linespan(1)[0], t.linespan(4)[1]]
    t[0] = ast.FnDeclarator(t[1], t[3], linespan=linespan)

  def p_function_simple_declarator_2(self, t):
    '''function_simple_declarator : ID PAREN_L PAREN_R
                                  | ID PAREN_L VOID PAREN_R'''
    linespan = [t.linespan(1)[0], t.linespan(len(t) - 1)[1]]
    t[0] = ast.FnDeclarator(t[1], ast.EmptyNode(), linespan=linespan)

  def p_variable_declaration(self, t):
    '''variable_declaration : type variable_declarator_group SEMICOLON'''
    linespan = [t[1].linespan[0], t.linespan(3)[1]]
    vdl = ast.VaDeclationList(linespan=linespan)
    for variable_declarator in t[2]:
      variable_declarator.add_type(t[1])
      vdl.add(variable_declarator)
    t[0] = vdl

  def p_variable_declarator_group_1(self, t):
    '''variable_declarator_group : variable_declarator'''
    t[0] = [t[1]]

  def p_variable_declarator_group_2(self, t):
    '''variable_declarator_group : variable_declarator_group COMMA variable_declarator'''
    t[1].append(t[3])
    t[0] = t[1]

  def p_variable_declarator_1(self, t):
    '''variable_declarator : variable_simple_declarator'''
    t[0] = t[1]

  def p_variable_declarator_2(self, t):
    '''variable_declarator : ASTERISK variable_declarator'''
    linespan = [t.linespan(1)[0], t[2].linespan[1]]
    t[2].add_type(ast.TypeNode(t[1], linespan=linespan))
    t[0] = t[2]

  def p_variable_simple_declarator_1(self, t):
    '''variable_simple_declarator : ID'''
    t[0] = ast.VaDeclarator(t[1], linespan=t.linespan(1))

  def p_variable_simple_declarator_2(self, t):
    '''variable_simple_declarator : ID BRACKET_L NUMBER_INT BRACKET_R'''
    linespan = [t.linespan(1)[0], t.linespan(4)[1]]
    t[0] = ast.ArrayDeclarator(t[1], t[3], linespan=linespan)

  def p_parameter_group_1(self, t):
    '''parameter_group : type variable_declarator'''
    t[2].add_type(t[1])
    linespan = [t[1].linespan[0], t[2].linespan[1]]
    t[0] = ast.ParameterGroup(t[2], linespan=linespan)

  def p_parameter_group_2(self, t):
    '''parameter_group : parameter_group COMMA type variable_declarator'''
    linespan = [t[1].linespan[0], t[4].linespan[1]]
    t[4].add_type(t[3])
    t[1].add(t[4])
    t[1].update_linespan(linespan)
    t[0] = t[1]

  # Statement

  def p_statement(self, t):
    '''statement : expression_statement
                 | conditional_statement
                 | loop_statement
                 | jump_statement'''
    t[0] = t[1]

  def p_expression_statement(self, t):
    '''expression_statement : expression SEMICOLON'''
    linespan = [t[1].linespan[0], t.linespan(2)[1]]
    t[1].update_linespan(linespan)
    t[0] = t[1]

  def p_conditional_statement_1(self, t):
    '''conditional_statement : IF PAREN_L expression PAREN_R section_wrapper %prec IFS'''
    linespan = [t.linespan(1)[0], t[5].linespan[1]]
    t[0] = ast.ConditionalStatement(t[3], t[5], ast.EmptyNode(), linespan=linespan)

  def p_conditional_statement_2(self, t):
    '''conditional_statement : IF PAREN_L expression PAREN_R section_wrapper ELSE section_wrapper'''
    linespan = [t.linespan(1)[0], t[7].linespan[1]]
    t[0] = ast.ConditionalStatement(t[3], t[5], t[7], linespan=linespan)

  def p_loop_statement_1(self, t):
    '''loop_statement : WHILE PAREN_L expression PAREN_R section_wrapper'''
    linespan = [t.linespan(1)[0], t[5].linespan[1]]
    t[0] = ast.While(t[3], t[5], linespan=linespan)

  def p_loop_statement_2(self, t):
    '''loop_statement : FOR PAREN_L expression_statement expression_statement expression PAREN_R scopeless_section_wrapper'''
    linespan = [t.linespan(1)[0], t[7].linespan[1]]
    t[0] = ast.For(t[3], t[4], t[5], t[7], linespan=linespan)

  def p_jump_statement_1(self, t):
    '''jump_statement : RETURN SEMICOLON'''
    linespan = [t.linespan(1)[0], t.linespan(2)[1]]
    t[0] = ast.Return(ast.EmptyNode(), linespan=linespan)

  def p_jump_statement_2(self, t):
    '''jump_statement : RETURN expression SEMICOLON'''
    linespan = [t.linespan(1)[0], t.linespan(3)[1]]
    t[0] = ast.Return(t[2], linespan=linespan)

  def p_jump_statement_3(self, t):
    '''jump_statement : BREAK SEMICOLON'''
    linespan = [t.linespan(1)[0], t.linespan(2)[1]]
    t[0] = ast.Break(linespan=linespan)

  def p_jump_statement_4(self, t):
    '''jump_statement : CONTINUE SEMICOLON'''
    linespan = [t.linespan(1)[0], t.linespan(2)[1]]
    t[0] = ast.Continue(linespan=linespan)

  # Expression

  def p_argument_expression_list_1(self, t):
    '''argument_expression_list : expression'''
    t[0] = ast.ArgumentList(t[1], linespan=t[1].linespan)

  def p_argument_expression_list_2(self, t):
    '''argument_expression_list : argument_expression_list COMMA expression'''
    linespan = [t[1].linespan[0], t[3].linespan[1]]
    t[1].add(t[3])
    t[1].update_linespan(linespan)
    t[0] = t[1]

  def p_expression(self, t):
    '''expression : additive_expression
                  | assign_expression'''
    t[0] = t[1]

  def p_assign_expression(self, t):
    '''assign_expression : variable_expression ASSIGN expression
                         | variable_expression ASSIGN_PLUS expression
                         | variable_expression ASSIGN_MINUS expression
                         | variable_expression ASSIGN_TIME expression
                         | variable_expression ASSIGN_DIVIDE expression
                         | variable_expression ASSIGN_MODULO expression'''
    linespan = [t[1].linespan[0], t[3].linespan[1]]
    t[0] = ast.AssignOp(t[2], t[1], t[3], linespan=linespan)

  def p_additive_expression_1(self, t):
    '''additive_expression : unary_expression'''
    t[0] = t[1]

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
    linespan = [t[1].linespan[0], t[3].linespan[1]]
    t[0] = ast.BinaryOp(t[2], t[1], t[3], linespan=linespan)

  def p_unary_expression_1(self, t):
    '''unary_expression : function_expression
                        | const_expression'''
    t[0] = t[1]

  def p_unary_expression_2(self, t):
    '''unary_expression : MINUS unary_expression
                        | PLUS unary_expression'''
    linespan = [t.linespan(1)[0], t[2].linespan[1]]
    t[0] = ast.UnaryOp(t[1], t[2], linespan=linespan)

  def p_unary_expression_3(self, t):
    '''unary_expression : function_expression DOUBLE_PLUS
                        | function_expression DOUBLE_MINUS'''
    linespan = [t[1].linespan[0], t.linespan(2)[1]]
    t[0] = ast.BinaryOp(t[2], t[1], ast.Const(1), linespan=linespan)

  def p_unary_expression_4(self, t):
    '''unary_expression : DOUBLE_PLUS function_expression
                        | DOUBLE_MINUS function_expression'''
    linespan = [t.linespan(1)[0], t[2].linespan[1]]
    t[0] = ast.BinaryOp(t[1], t[2], ast.Const(1), linespan=linespan)

  def p_function_expression_1(self, t):
    '''function_expression : variable_expression'''
    t[0] = t[1]

  def p_function_expression_2(self, t):
    '''function_expression : function_expression PAREN_L argument_expression_list PAREN_R'''
    linespan = [t[1].linespan[0], t.linespan(4)[1]]
    t[0] = ast.FnExpression(t[1], t[3], linespan=linespan)

  def p_function_expression_3(self, t):
    '''function_expression : function_expression PAREN_L PAREN_R'''
    linespan = [t[1].linespan[0], t.linespan(3)[1]]
    t[0] = ast.FnExpression(t[1], ast.EmptyNode, linespan=linespan)

  def p_variable_expression_1(self, t):
    '''variable_expression : variable_simpe_expression'''
    t[0] = t[1]

  def p_variable_expression_2(self, t):
    '''variable_expression : ASTERISK variable_simpe_expression
                           | AMPERSAND variable_simpe_expression'''
    linespan = [t.linespan(1)[0], t[2].linespan[1]]
    t[1].set_pointer(t[1])
    t[1].update_linespan(linespan)
    t[0] = t[1]

  def p_variable_simpe_expression_1(self, t):
    '''variable_simpe_expression : ID'''
    t[0] = ast.VaExpression(t[1], linespan=t.linespan(1))

  def p_variable_simpe_expression_2(self, t):
    '''variable_simpe_expression : variable_simpe_expression BRACKET_L expression BRACKET_R'''
    linespan = [t[1].linespan[0], t.linespan(4)[1]]
    t[0] = ast.ArrayExpression(t[1], t[3], linespan=linespan)

  def p_variable_simpe_expression_3(self, t):
    '''variable_simpe_expression : PAREN_L expression PAREN_R'''
    linespan = [t.linespan(1)[0], t.linespan(3)[1]]
    t[2].update_linespan(linespan)
    t[0] = t[2]

  def p_const_expression_1(self, t):
    '''const_expression : NUMBER_FLOAT'''
    t[0] = ast.Const(float(t[1]), linespan=t.linespan(1))

  def p_const_expression_2(self, t):
    '''const_expression : NUMBER_INT'''
    t[0] = ast.Const(int(t[1]), linespan=t.linespan(1))

  def p_const_expression_3(self, t):
    '''const_expression : CHARACTER'''
    t[0] = ast.Const(t[1], linespan=t.linespan(1))

  def p_const_expression_4(self, t):
    '''const_expression : STRING'''
    t[0] = ast.Const(t[1], linespan=t.linespan(1))

  # ETC

  def p_type(self, t):
    '''type : INT
            | FLOAT
            | VOID
            | CHAR'''
    t[0] = ast.TypeNode(t[1], linespan=t.linespan(1))

  def p_empty(self, t):
    'empty :'
    pass

  def p_error(self, t):
    print(t)
    print("Syntax Error at %d." % t.linespan)
    raise SyntaxError

if __name__ == '__main__':
    src_path = sys.argv[1]
    parser = Parser(debug=True)
    ast = parser.run(src_path)
    print(ast)