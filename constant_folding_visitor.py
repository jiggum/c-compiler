import sys
import traceback
from symbol_table import SymbolTable
import ast
from type import type_cast
from function import globalFunctionTable, Function

class ConstantFoldingVisitor:
  def __init__(self, debug=False):
    self.global_scope = SymbolTable(ast.EmptyNode(), globalFunctionTable)
    self.scopes = [self.global_scope]
    self.debug = debug
    self.runtime_error = False
    self.freeze_constant_folding = False
    self.freeze_set_constant = False
    self.check_constant_outer = False
    self.check_constant_self = False

  def accept(self, node):
    try :
      result, jum_stmt = node.accept(self)
      return result, jum_stmt
    except:
      if not self.runtime_error:
        if self.debug:
          exc_info = sys.exc_info()
          traceback.print_exception(*exc_info)
          del exc_info
        print('Run-time error : line %d' % node.linespan[0])
        self.runtime_error = True

  def print(self, symbol):
    scope = self.get_scope()
    if not scope.has(symbol):
      print('Invisible variable')
    else:
      target = scope.get(symbol)
      print('N/A' if target is None else target)

  def trace(self, symbol):
    scope = self.get_scope()
    if not scope.has(symbol):
      print('Invisible variable')
    else:
      scope.trace(symbol)

  def push_scope(self, scope):
    self.scopes.append(scope)

  def pop_scope(self):
    self.scopes.pop()

  def get_scope(self):
    return self.scopes[-1]

  def is_in_loop(self):
    for scope in reversed(self.scopes):
      if isinstance(scope.node, ast.LoopStatement):
        return True
    return False

  def is_parent_scope_node(self, node):
    if node is None:
      return True
    for scope in reversed(self.scopes):
      if scope.node is node:
        return True
    return False

  def is_constant(self, symbol):
    scope = self.get_scope()
    constant_section = scope.get_constant_section(symbol)
    constant = scope.is_constant(symbol)
    if self.check_constant_outer:
      return constant and self.is_parent_scope_node(constant_section) and (self.get_conditional_section() is not constant_section)
    if self.check_constant_self:
      return constant and self.get_conditional_section() is constant_section
    return constant and self.is_parent_scope_node(constant_section)

  def set_constant(self, symbol, constant):
    if self.freeze_set_constant:
      return
    self.get_scope().set_constant(symbol, constant, self.get_conditional_section())

  def get_conditional_section(self):
    for scope in reversed(self.scopes):
      if isinstance(scope.node, ast.LoopStatement) or isinstance(scope.node , ast.ConditionalStatement):
        return scope.node
    return None

  def replace(self, base_node, target_node):
    if not self.freeze_constant_folding:
        base_node.replace(target_node)

  # def ArrayNode(self): // all child node implemented by itself

  # def EmptyNode(self): // maybe not necessary

  # def TypeNode(self): // maybe not necessary

  def Const(self, node):
    node.result = node.value
    return node.result, None

  def BaseSection(self, node):
    for child in node.childs:
      result, jump_stmt = self.accept(child)
      if jump_stmt is not None:
        node.result = result
        return node.result, jump_stmt

    return node.result, None

  def RootSection(self, node):
    for child in node.childs:
      self.accept(child)
    print('End of program')
    return node.result, None

  # def Section(self): // covered by BaseSection

  # def Declaration(self): // all child node implemented by itself

  def FnDeclaration(self, node):
    scope = self.get_scope()
    scope.define(node.name, node.type, node.linespan[0], node)

    func_scope = SymbolTable(node, self.global_scope)
    if node.name != 'main':
      self.push_scope(func_scope)
    if not node.parameterGroup.is_empty():
      for i, parameter in enumerate(node.parameterGroup.childs):
        func_scope.define(parameter.name, parameter.type, parameter.linespan[0])
    self.accept(node.body)
    if node.name != 'main':
      self.pop_scope()
    return node.result, None

  def VaDeclarationList(self, node):
    for child in node.childs:
      self.accept(child)
    return node.result, None

  # def Declarator(self): // all child node implemented by itself

  # def FnDeclarator(self): // covered by FnDeclaration

  def VaDeclarator(self, node):
    scope = self.get_scope()
    scope.define(node.name, node.type, node.linespan[0], None)
    return None, None

  def ArrayDeclarator(self, node):
    scope = self.get_scope()
    scope.define(node.name, node.type, node.linespan[0], [None] * node.size)
    return None, None

  # def ParameterGroup(self): // not necessary

  def ConditionalStatement(self, node):
    expr_result, expr_jump_stmt = self.accept(node.expr)
    if expr_result or (not node.else_section.is_empty()):
      self.push_scope(SymbolTable(node, self.get_scope()))
      self.accept(node.then_section)
      self.pop_scope()
      if not node.else_section.is_empty():
        self.push_scope(SymbolTable(node, self.get_scope()))
        self.accept(node.else_section)
        self.pop_scope()

    return node.result, None

  def LoopStatement(self, node):
    prev_check_constant_outer = self.check_constant_outer
    prev_check_constant_self = self.check_constant_self
    self.check_constant_outer = False
    self.check_constant_self = True

    node.save_origin()
    scope = self.get_scope()
    self.push_scope(SymbolTable(node, scope))

    if node.init_stmt is not None:
      prev_freeze_set_constant = self.freeze_set_constant
      self.freeze_set_constant = True
      self.accept(node.init_stmt)
      self.freeze_set_constant = prev_freeze_set_constant

    for iter in range(2):
      expr_result, expr_jump_stmt = self.accept(node.expr)
      if expr_jump_stmt is not None:
        node.result = expr_result
        return node.result, expr_jump_stmt

      result, jump_stmt = self.accept(node.section)
      if jump_stmt is not None:
        if isinstance(jump_stmt, ast.Return):
          self.pop_scope()
          node.result = result
          return node.result, jump_stmt
        elif isinstance(jump_stmt, ast.Break):
          self.pop_scope()
          return None, None
        elif isinstance(jump_stmt, ast.Continue):
          pass
        else:
          raise ValueError

      if node.term_stmt is not None:
        self.accept(node.term_stmt)

      self.check_constant_self = prev_check_constant_self
      self.check_constant_outer = True
      node.save_origin()
      node.load_origin()

    self.check_constant_outer = prev_check_constant_outer
    self.pop_scope()
    return None, None

  # def While(self): // covered by LoopStatement

  # def For(self): // covered by LoopStatement

  # def JumpStatement(self): // all child node implemented by itself

  def Return(self, node):
    if not node.expr.is_empty():
      result, jump_stmt = self.accept(node.expr)
      node.result = result
    return node.result, node

  def Break(self, node):
    if not self.is_in_loop():
      raise ValueError
    return node.result, node

  def Continue(self, node):
    if not self.is_in_loop():
      raise ValueError
    return node.result, node

  def ArgumentList(self, node):
    results = []
    for child in node.childs:
      result, jump_stmt = self.accept(child)
      results.append(result)
    node.result = results
    return node.result, None

  def BinaryOp(self, node):
    prev_freeze_constant_folding = self.freeze_constant_folding
    if node.op == '++' or node.op == '--':
      self.freeze_constant_folding = True
    left_result, left_jump_stmt = self.accept(node.left)
    if node.op == '++' or node.op == '--':
      self.freeze_constant_folding = prev_freeze_constant_folding
    right_result, right_jump_stmt = self.accept(node.right)

    if (left_result is None) or (right_result is None):
      node.result = None
      return node.result, None

    if node.op == '==':
      node.result = left_result == right_result
    elif node.op == '!=':
      node.result = left_result != right_result
    elif node.op == '<':
      node.result = left_result < right_result
    elif node.op == '>':
      node.result = left_result > right_result
    elif node.op == '<=':
      node.result = left_result <= right_result
    elif node.op == '>=':
      node.result = left_result >= right_result
    elif node.op == '+':
      node.result = left_result + right_result
    elif node.op == '-':
      node.result = left_result - right_result
    elif node.op == '&&':
      node.result = left_result and right_result
    elif node.op == '||':
      node.result = left_result or right_result
    elif node.op == '*':
      node.result = left_result * right_result
    elif node.op == '/':
      node.result = left_result / right_result
    elif node.op == '%':
      node.result = left_result % right_result
    elif node.op == '++':
      node.result = left_result + right_result
    elif node.op == '--':
      node.result = left_result - right_result
    else:
      raise ValueError

    if node.result is True:
      node.result = 1
    elif node.result is False:
      node.result = 0

    if node.op == '++' or node.op == '--':
      scope = self.get_scope()
      if node.left.__class__ is ast.VaExpression:
        scope.add(node.left.name, node.linespan[0], node.result)
        self.set_constant(node.left.name, self.is_constant(node.left.name))
      elif (node.left.__class__ is ast.Const):
        self.replace(node, ast.Const(node.result, node.linespan))
    elif node.left.__class__ is ast.Const and node.right.__class__ is ast.Const:
      linespan = (node.left.linespan[0], node.right.linespan[1])
      self.replace(node, ast.Const(node.result, linespan))
    return node.result, None

  def AssignOp(self, node):
    right_result, right_jump_stmt = self.accept(node.right)

    scope = self.get_scope()
    if node.left.__class__ is ast.VaExpression:
      symbol = node.left.name
      if right_result is not None:
        right_result = type_cast(scope.get_type(symbol), right_result)
      scope.add(symbol, node.linespan[0], right_result)
      node.result = scope.get(symbol)
      self.set_constant(symbol, node.right.__class__ is ast.Const)
    elif node.left.__class__ is ast.ArrayExpression:
      prev_freeze_constant_folding = self.freeze_constant_folding
      self.freeze_constant_folding = True
      expr_result, expr_jump_stmt = self.accept(node.left.expr)
      self.freeze_constant_folding = prev_freeze_constant_folding
      index_result, index_jump_stmt = self.accept(node.left.index)
      expr_result[index_result] = right_result
      node.result = expr_result
    else:
      raise ValueError

    return node.result, None

  def UnaryOp(self, node):
    expr_result, expr_jump_stmt = self.accept(node.expr)

    if expr_result is None:
      node.result = None
      return node.result, None

    if node.op == '+':
      node.result = expr_result
    elif node.op == '-':
      node.result = -expr_result
    else:
      raise ValueError

    if node.expr.__class__ is ast.Const:
      self.replace(node, ast.Const(node.result, node.expr.linespan))
    return node.result, None

  def FnExpression(self, node):
    expr_result, expr_jump_stmt = self.accept(node.expr)
    arguments_result, arguments_jump_stmt = self.accept(node.arguments)
    if all(argument.__class__ is ast.Const for argument in node.arguments.childs):
      if expr_result.__class__ is Function:
        node.result = expr_result.run(*arguments_result)
      else:
        if not node.initialized:
          node.body = expr_result.body.clone()
          func_scope = SymbolTable(expr_result, self.global_scope)
          self.push_scope(func_scope)
          for i, parameter in enumerate(expr_result.parameterGroup.childs):
            func_scope.define(parameter.name, parameter.type, parameter.linespan[0], arguments_result[i])
          node.initialized = True

        body_result, body_jump_stmt = self.accept(node.body)
        self.pop_scope()
        node.result = body_result
      if self.get_scope().is_pure_function(expr_result.name):
        self.replace(node, ast.Const(node.result, node.linespan))
      return node.result, None
    else:
      return None, None

  def VaExpression(self, node):
    scope = self.get_scope()
    node.result = scope.get(node.name)
    if self.is_constant(node.name):
      self.replace(node, ast.Const(node.result, node.linespan))
    return node.result, None

  def ArrayExpression(self, node):
    prev_freeze_constant_folding = self.freeze_constant_folding
    self.freeze_constant_folding = True
    expr_result, expr_jump_stmt = self.accept(node.expr)
    self.freeze_constant_folding = prev_freeze_constant_folding
    index_result, index_jump_stmt = self.accept(node.index)

    if expr_result is None:
      node.result = None
      return node.result, None

    node.result = expr_result[index_result]
    return node.result, None
