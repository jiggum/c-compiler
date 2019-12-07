import os
import ply.yacc as yacc
from lexer import Lexer
import ast

class Parser(Lexer):
  def __init__(self, **kw):
    super().__init__(**kw)
    self.names = {}
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

  def p_root_section_opt_1(self, p):
    '''root_section_opt : empty'''
    p[0] = ast.EmptyNode()

  def p_root_section_opt_2(self, p):
    '''root_section_opt : root_section'''
    p[0] = p[1]

  def p_root_section_1(self, p):
    '''root_section : root_sector'''
    p[0] = ast.RootSection(p[1], linespan=p[1].linespan)

  def p_root_section_2(self, p):
    '''root_section : root_section root_sector'''
    linespan = (p[1].linespan[0], p[2].linespan[1])
    p[1].add(p[2])
    p[1].update_linespan(linespan)
    p[0] = p[1]

  def p_root_sector(self, p):
    '''root_sector : declaration
                   | expression_statement
                   | conditional_statement
                   | loop_statement'''
    p[0] = p[1]

  def p_section_wrapper(self, p):
    '''section_wrapper : BRACE_L section_opt BRACE_R'''
    linespan = (p.linespan(1)[0], p.linespan(3)[1])
    p[2].update_linespan(linespan)
    p[0] = p[2]

  def p_section_opt_1(self, p):
    '''section_opt : empty'''
    pass

  def p_section_opt_2(self, p):
    '''section_opt : section'''
    p[0] = p[1]

  def p_section_1(self, p):
    '''section : sector'''
    p[0] = ast.Section(p[1], linespan=p[1].linespan)

  def p_section_2(self, p):
    '''section : section sector'''
    linespan = (p[1].linespan[0], p[2].linespan[1])
    p[1].add(p[2])
    p[1].update_linespan(linespan)
    p[0] = p[1]

  def p_scopeless_section_wrapper(self, p):
    '''scopeless_section_wrapper : BRACE_L scopeless_section_opt BRACE_R'''
    linespan = (p.linespan(1)[0], p.linespan(3)[1])
    p[2].update_linespan(linespan)
    p[0] = p[2]

  def p_scopeless_section_opt_1(self, p):
    '''scopeless_section_opt : empty'''
    pass

  def p_scopeless_section_opt_2(self, p):
    '''scopeless_section_opt : scopeless_section'''
    p[0] = p[1]

  def p_scopeless_section_1(self, p):
    '''scopeless_section : sector'''
    p[0] = ast.ScopelessSection(p[1], linespan=p[1].linespan)

  def p_scopeless_section_2(self, p):
    '''scopeless_section : scopeless_section sector'''
    linespan = (p.linespan(1)[0], p.linespan(2)[1])
    p[1].add(p[2])
    p[1].update_linespan(linespan)
    p[0] = p[1]

  def p_sector(self, p):
    '''sector : declaration
              | statement'''
    p[0] = p[1]

  # Declaration

  def p_declaration(self, p):
    '''declaration : variable_declaration
                   | function_declaration'''
    p[0] = p[1]

  def p_function_declaration(self, p):
    '''function_declaration : type function_declarator scopeless_section_wrapper'''
    p[2].add_type(p[1])
    linespan = (p[1].linespan[0], p[3].linespan[1])
    p[0] = ast.FnDeclaration(p[2], p[3], linespan=linespan)

  def p_function_declarator_1(self, p):
    '''function_declarator : function_simple_declarator'''
    p[0] = p[1]

  def p_function_declarator_2(self, p):
    '''function_declarator : ASTERISK function_declarator'''
    linespan = (p.linespan(1)[0], p[2].linespan[1])
    p[2].add_type(ast.TypeNode(p[1], linespan=linespan))
    p[0] = p[2]

  def p_function_simple_declarator_1(self, p):
    '''function_simple_declarator : ID PAREN_L parameter_group PAREN_R'''
    linespan = (p.linespan(1)[0], p.linespan(4)[1])
    p[0] = ast.FnDeclarator(p[1], p[3], linespan=linespan)

  def p_function_simple_declarator_2(self, p):
    '''function_simple_declarator : ID PAREN_L PAREN_R
                                  | ID PAREN_L VOID PAREN_R'''
    linespan = (p.linespan(1)[0], p.linespan(len(p) - 1)[1])
    p[0] = ast.FnDeclarator(p[1], ast.EmptyNode(), linespan=linespan)

  def p_variable_declaration(self, p):
    '''variable_declaration : type variable_declarator_group SEMICOLON'''
    linespan = (p[1].linespan[0], p.linespan(3)[1])
    vdl = ast.VaDeclarationList(linespan=linespan)
    for variable_declarator in p[2]:
      variable_declarator.add_type(p[1])
      vdl.add(variable_declarator)
    p[0] = vdl

  def p_variable_declarator_group_1(self, p):
    '''variable_declarator_group : variable_declarator'''
    p[0] = [p[1]]

  def p_variable_declarator_group_2(self, p):
    '''variable_declarator_group : variable_declarator_group COMMA variable_declarator'''
    p[1].append(p[3])
    p[0] = p[1]

  def p_variable_declarator_1(self, p):
    '''variable_declarator : variable_simple_declarator'''
    p[0] = p[1]

  def p_variable_declarator_2(self, p):
    '''variable_declarator : ASTERISK variable_declarator'''
    linespan = (p.linespan(1)[0], p[2].linespan[1])
    p[2].add_type(ast.TypeNode(p[1], linespan=linespan))
    p[0] = p[2]

  def p_variable_simple_declarator_1(self, p):
    '''variable_simple_declarator : ID'''
    p[0] = ast.VaDeclarator(p[1], linespan=p.linespan(1))

  def p_variable_simple_declarator_2(self, p):
    '''variable_simple_declarator : ID BRACKET_L NUMBER_INT BRACKET_R'''
    linespan = (p.linespan(1)[0], p.linespan(4)[1])
    p[0] = ast.ArrayDeclarator(p[1], p[3], linespan=linespan)

  def p_parameter_group_1(self, p):
    '''parameter_group : type variable_declarator'''
    p[2].add_type(p[1])
    linespan = (p[1].linespan[0], p[2].linespan[1])
    p[0] = ast.ParameterGroup(p[2], linespan=linespan)

  def p_parameter_group_2(self, p):
    '''parameter_group : parameter_group COMMA type variable_declarator'''
    linespan = (p[1].linespan[0], p[4].linespan[1])
    p[4].add_type(p[3])
    p[1].add(p[4])
    p[1].update_linespan(linespan)
    p[0] = p[1]

  # Statement

  def p_statement(self, p):
    '''statement : expression_statement
                 | conditional_statement
                 | loop_statement
                 | jump_statement'''
    p[0] = p[1]

  def p_expression_statement(self, p):
    '''expression_statement : expression SEMICOLON'''
    linespan = (p[1].linespan[0], p.linespan(2)[1])
    p[1].update_linespan(linespan)
    p[0] = p[1]

  def p_conditional_statement_1(self, p):
    '''conditional_statement : IF PAREN_L expression PAREN_R section_wrapper %prec IFS'''
    linespan = (p.linespan(1)[0], p[5].linespan[1])
    p[0] = ast.ConditionalStatement(p[3], p[5], ast.EmptyNode(), linespan=linespan)

  def p_conditional_statement_2(self, p):
    '''conditional_statement : IF PAREN_L expression PAREN_R section_wrapper ELSE section_wrapper'''
    linespan = (p.linespan(1)[0], p[7].linespan[1])
    p[0] = ast.ConditionalStatement(p[3], p[5], p[7], linespan=linespan)

  def p_loop_statement_1(self, p):
    '''loop_statement : WHILE PAREN_L expression PAREN_R scopeless_section_wrapper'''
    linespan = (p.linespan(1)[0], p[5].linespan[1])
    p[0] = ast.While(p[3], p[5], linespan=linespan)

  def p_loop_statement_2(self, p):
    '''loop_statement : FOR PAREN_L expression_statement expression_statement expression PAREN_R scopeless_section_wrapper'''
    linespan = (p.linespan(1)[0], p[7].linespan[1])
    p[0] = ast.For(p[3], p[4], p[5], p[7], linespan=linespan)

  def p_jump_statement_1(self, p):
    '''jump_statement : RETURN SEMICOLON'''
    linespan = (p.linespan(1)[0], p.linespan(2)[1])
    p[0] = ast.Return(ast.EmptyNode(), linespan=linespan)

  def p_jump_statement_2(self, p):
    '''jump_statement : RETURN expression SEMICOLON'''
    linespan = (p.linespan(1)[0], p.linespan(3)[1])
    p[0] = ast.Return(p[2], linespan=linespan)

  def p_jump_statement_3(self, p):
    '''jump_statement : BREAK SEMICOLON'''
    linespan = (p.linespan(1)[0], p.linespan(2)[1])
    p[0] = ast.Break(linespan=linespan)

  def p_jump_statement_4(self, p):
    '''jump_statement : CONTINUE SEMICOLON'''
    linespan = (p.linespan(1)[0], p.linespan(2)[1])
    p[0] = ast.Continue(linespan=linespan)

  # Expression

  def p_argument_expression_list_1(self, p):
    '''argument_expression_list : expression'''
    p[0] = ast.ArgumentList(p[1], linespan=p[1].linespan)

  def p_argument_expression_list_2(self, p):
    '''argument_expression_list : argument_expression_list COMMA expression'''
    linespan = (p[1].linespan[0], p[3].linespan[1])
    p[1].add(p[3])
    p[1].update_linespan(linespan)
    p[0] = p[1]

  def p_expression(self, p):
    '''expression : additive_expression
                  | assign_expression'''
    p[0] = p[1]

  def p_assign_expression(self, p):
    '''assign_expression : variable_expression ASSIGN expression
                         | variable_expression ASSIGN_PLUS expression
                         | variable_expression ASSIGN_MINUS expression
                         | variable_expression ASSIGN_TIME expression
                         | variable_expression ASSIGN_DIVIDE expression
                         | variable_expression ASSIGN_MODULO expression'''
    linespan = (p[1].linespan[0], p[3].linespan[1])
    p[0] = ast.AssignOp(p[2], p[1], p[3], linespan=linespan)

  def p_additive_expression_1(self, p):
    '''additive_expression : unary_expression'''
    p[0] = p[1]

  def p_additive_expression_2(self, p):
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
    linespan = (p[1].linespan[0], p[3].linespan[1])
    p[0] = ast.BinaryOp(p[2], p[1], p[3], linespan=linespan)

  def p_unary_expression_1(self, p):
    '''unary_expression : function_expression
                        | const_expression'''
    p[0] = p[1]

  def p_unary_expression_2(self, p):
    '''unary_expression : MINUS unary_expression
                        | PLUS unary_expression'''
    linespan = (p.linespan(1)[0], p[2].linespan[1])
    p[0] = ast.UnaryOp(p[1], p[2], linespan=linespan)

  def p_unary_expression_3(self, p):
    '''unary_expression : function_expression DOUBLE_PLUS
                        | function_expression DOUBLE_MINUS'''
    linespan = (p[1].linespan[0], p.linespan(2)[1])
    p[0] = ast.BinaryOp(p[2], p[1], ast.Const(1), linespan=linespan)

  def p_unary_expression_4(self, p):
    '''unary_expression : DOUBLE_PLUS function_expression
                        | DOUBLE_MINUS function_expression'''
    linespan = (p.linespan(1)[0], p[2].linespan[1])
    p[0] = ast.BinaryOp(p[1], p[2], ast.Const(1), linespan=linespan)

  def p_function_expression_1(self, p):
    '''function_expression : variable_expression'''
    p[0] = p[1]

  def p_function_expression_2(self, p):
    '''function_expression : function_expression PAREN_L argument_expression_list PAREN_R'''
    linespan = (p[1].linespan[0], p.linespan(4)[1])
    p[0] = ast.FnExpression(p[1], p[3], linespan=linespan)

  def p_function_expression_3(self, p):
    '''function_expression : function_expression PAREN_L PAREN_R'''
    linespan = (p[1].linespan[0], p.linespan(3)[1])
    p[0] = ast.FnExpression(p[1], ast.EmptyNode, linespan=linespan)

  def p_variable_expression_1(self, p):
    '''variable_expression : variable_simpe_expression'''
    p[0] = p[1]

  def p_variable_expression_2(self, p):
    '''variable_expression : ASTERISK variable_simpe_expression
                           | AMPERSAND variable_simpe_expression'''
    linespan = (p.linespan(1)[0], p[2].linespan[1])
    p[1].set_pointer(p[1])
    p[1].update_linespan(linespan)
    p[0] = p[1]

  def p_variable_simpe_expression_1(self, p):
    '''variable_simpe_expression : ID'''
    p[0] = ast.VaExpression(p[1], linespan=p.linespan(1))

  def p_variable_simpe_expression_2(self, p):
    '''variable_simpe_expression : variable_simpe_expression BRACKET_L expression BRACKET_R'''
    linespan = (p[1].linespan[0], p.linespan(4)[1])
    p[0] = ast.ArrayExpression(p[1], p[3], linespan=linespan)

  def p_variable_simpe_expression_3(self, p):
    '''variable_simpe_expression : PAREN_L expression PAREN_R'''
    linespan = (p.linespan(1)[0], p.linespan(3)[1])
    p[2].update_linespan(linespan)
    p[2].use_paren = True
    p[0] = p[2]

  def p_const_expression_1(self, p):
    '''const_expression : NUMBER_FLOAT'''
    p[0] = ast.Const(float(p[1]), linespan=p.linespan(1))

  def p_const_expression_2(self, p):
    '''const_expression : NUMBER_INT'''
    p[0] = ast.Const(int(p[1]), linespan=p.linespan(1))

  def p_const_expression_3(self, p):
    '''const_expression : CHARACTER'''
    p[0] = ast.Const(p[1][1:-1], linespan=p.linespan(1))

  def p_const_expression_4(self, p):
    '''const_expression : STRING'''
    p[0] = ast.Const(p[1][1:-1], linespan=p.linespan(1))

  # ETC

  def p_type(self, p):
    '''type : INT
            | FLOAT
            | VOID
            | CHAR'''
    p[0] = ast.TypeNode(p[1], linespan=p.linespan(1))

  def p_empty(self, p):
    'empty :'
    pass

  def p_error(self, p):
    print("Syntax error : line %d" % p.lineno)
    raise SyntaxError
