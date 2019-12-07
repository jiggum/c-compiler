import sys
import traceback
from symbol_table import SymbolTable
import ast
from function import globalFunctionTable, Function

class FlowVisitor:
  def __init__(self, debug=False, constant_folding=False):
    self.global_scope = SymbolTable(ast.EmptyNode(), globalFunctionTable)
    self.scopes = [self.global_scope]
    self.linenos = [1]
    self.line_num = 0
    self.debug = debug
    self.runtime_error = False
    self.constant_folding = constant_folding
    self.freeze_constant_folding = False

  def accept(self, node):
    try :
      if node.terminated:
        return node.terminated, node.result, None
      terminated, result, jum_stmt = node.accept(self)
      node.visited = True
      return terminated, result, jum_stmt
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

  def add_linenum(self, line_num):
    self.line_num += line_num

  def push_scope(self, scope, lineno):
    self.scopes.append(scope)
    self.linenos.append(lineno)

  def pop_scope(self):
    self.scopes.pop()
    self.linenos.pop()

  def get_scope(self):
    return self.scopes[-1]

  def get_lineno(self):
    return self.linenos[-1]

  def update_lineno(self, lineno):
    self.linenos[-1] = lineno

  def is_in_loop(self):
    for scope in reversed(self.scopes):
      if isinstance(scope.node, ast.LoopStatement):
        return True
    return False

  def is_in_conditional_section(self):
    for scope in reversed(self.scopes):
      if isinstance(scope.node, ast.LoopStatement) or isinstance(scope.node , ast.ConditionalStatement):
        return True
    return False

  def is_optimizer(self):
    return self.constant_folding

  # return to_return, terminated, result, jump_stmt
  def visit_with_linecount(self, node, lazy=False):
    if not node.visited:
      lineno = node.get_excutable_lineno()
      if lineno > self.get_lineno() + self.line_num - 1 and not self.is_optimizer():
        self.update_lineno(self.get_lineno() + self.line_num)
        self.line_num = 0
        return True, False, None, None
      else:
        self.line_num -= lineno - self.get_lineno()
        if lazy:
          self.line_num -= 1
        self.update_lineno(lineno)
    prev_terminated = node.terminated
    terminated, result, jump_stmt = self.accept(node)
    if not terminated:
      return True, False, None, None
    elif jump_stmt is not None:
      return True, node.terminated, node.result, jump_stmt
    if lazy and (not prev_terminated):
      self.update_lineno(self.get_lineno() + 1)
    return False, node.terminated, node.result, None

  # def ArrayNode(self): // all child node implemented by itself

  # def EmptyNode(self): // maybe not necessary

  # def TypeNode(self): // maybe not necessary

  def Const(self, node):
    node.terminated = True
    node.result = node.value
    return node.terminated, node.result, None

  def BaseSection(self, node):
    for child in node.childs:
      to_return, terminated, result, jump_stmt = self.visit_with_linecount(child, True)
      if to_return:
        node.terminated = terminated
        node.result = result
        return node.terminated, node.result, jump_stmt

    section_end_lineno = node.linespan[1]
    if section_end_lineno > self.get_lineno() + self.line_num - 1 and not self.is_optimizer():
      self.update_lineno(self.get_lineno() + self.line_num)
      self.line_num = 0
      return False, None, None
    else:
      self.line_num -= section_end_lineno - self.get_lineno()
      self.update_lineno(section_end_lineno)

    node.terminated = True
    return node.terminated, node.result, None

  def RootSection(self, node):
    for child in node.childs:
      terminated, result, jump_stmt = self.accept(child)
      if not terminated:
        return False, None, None
    print('End of program')
    node.terminated = True
    return node.terminated, node.result, None

  # def Section(self): // covered by BaseSection

  # def Declaration(self): // all child node implemented by itself

  def FnDeclaration(self, node):
    if not node.visited:
      scope = self.get_scope()
      scope.define(node.name, node.type, node.linespan[0], node)
      scope.set_constant(node.name, False)
    if node.name == 'main' or self.is_optimizer():
      func_scope = SymbolTable(node, self.global_scope)
      if not node.visited and node.name != 'main':
        self.push_scope(func_scope, node.body.linespan[0])
      if not node.parameterGroup.is_empty():
        for i, parameter in enumerate(node.parameterGroup.childs):
          func_scope.define(parameter.name, parameter.type, parameter.linespan[0])
          func_scope.set_constant(parameter.name, False)
      if not node.body.visited:
        self.update_lineno(node.body.linespan[0])
      terminated, result, jump_stmt = self.accept(node.body)
      if not terminated:
        return False, None, None
      if node.name != 'main':
        self.pop_scope()
    node.terminated = True
    return node.terminated, node.result, None

  def VaDeclarationList(self, node):
    for child in node.childs:
      self.accept(child)
    node.terminated = True
    return node.terminated, node.result, None

  # def Declarator(self): // all child node implemented by itself

  # def FnDeclarator(self): // covered by FnDeclaration

  def VaDeclarator(self, node):
    scope = self.get_scope()
    scope.define(node.name, node.type, node.linespan[0], None)
    return True, None, None

  def ArrayDeclarator(self, node):
    scope = self.get_scope()
    scope.define(node.name, node.type, node.linespan[0], [None] * node.size)
    return True, None, None

  # def ParameterGroup(self): // not necessary

  def ConditionalStatement(self, node):
    expr_terminated, expr_result, expr_jump_stmt = self.accept(node.expr)
    if not expr_terminated:
      return False, None, None
    if expr_result or (not node.else_section.is_empty()):
      section = node.then_section if expr_result else node.else_section
      if not section.visited:
        self.push_scope(SymbolTable(node, self.get_scope()), section.linespan[0])
        self.update_lineno(section.linespan[0])
      to_return, terminated, result, jump_stmt = self.visit_with_linecount(section)
      if to_return:
        if jump_stmt is not None:
          self.pop_scope()
        node.terminated = terminated
        node.result = result
        return node.terminated, node.result, jump_stmt
      self.pop_scope()
      self.line_num -= 1

    self.update_lineno(node.linespan[1])
    node.terminated = True
    return node.terminated, node.result, None

  def LoopStatement(self, node):
    iter_count = 0
    if self.is_optimizer():
      iter_count = 2
      self.freeze_constant_folding = True

    if not node.visited:
      node.save_origin()
      scope = self.get_scope()
      self.push_scope(SymbolTable(node, scope), node.get_excutable_lineno() + 1)

    if node.init_stmt is not None:
      init_stmt_terminated, init_stmt_result, init_stmt_jump_stmt = self.accept(node.init_stmt)
      if not init_stmt_terminated:
        return False, None, None

    while True:
      to_return, expr_terminated, expr_result, expr_jump_stmt = self.visit_with_linecount(node.expr)
      if to_return:
        node.terminated = expr_terminated
        node.result = expr_result
        return node.terminated, node.result, expr_jump_stmt

      if (not expr_result) and (not self.is_optimizer()):
        self.pop_scope()
        node.terminated = True
        self.update_lineno(node.linespan[1])
        self.line_num -= 1
        return node.terminated, node.result, None

      to_return, terminated, result, jump_stmt = self.visit_with_linecount(node.section)
      if to_return:
        if jump_stmt is not None:
          if isinstance(jump_stmt, ast.Return):
            self.pop_scope()
            self.update_lineno(node.linespan[1])
            node.terminated = terminated
            node.result = result
            return node.terminated, node.result, jump_stmt
          elif isinstance(jump_stmt, ast.Break):
            self.pop_scope()
            self.update_lineno(node.linespan[1])
            node.terminated = terminated
            return node.terminated, None, None
          elif isinstance(jump_stmt, ast.Continue):
            pass
          else:
            raise ValueError
        else:
          node.terminated = terminated
          return node.terminated, None, None

      if node.term_stmt is not None:
        term_stmt_terminated, term_stmt_result, term_stmt_jump_stmt = self.accept(node.term_stmt)
        if (not term_stmt_terminated):
          return False, None, None

      self.update_lineno(node.linespan[0])
      self.line_num -= 1

      if self.is_optimizer():
        iter_count -= 1
        self.freeze_constant_folding = False
        if iter_count <= 0:
          self.pop_scope()
          node.terminated = True
          return node.terminated, None, None

      node.load_origin()

  # def While(self): // covered by LoopStatement

  # def For(self): // covered by LoopStatement

  # def JumpStatement(self): // all child node implemented by itself

  def Return(self, node):
    if not node.expr.is_empty():
      terminated, result, jump_stmt = self.accept(node.expr)
      if (not terminated):
        return False, None, None
      node.result = result
    node.terminated = True
    return node.terminated, node.result, node

  def Break(self, node):
    if not self.is_in_loop():
      raise ValueError
    node.terminated = True
    return node.terminated, node.result, node

  def Continue(self, node):
    if not self.is_in_loop():
      raise ValueError
    node.terminated = True
    return node.terminated, node.result, node

  def ArgumentList(self, node):
    results = []
    for child in node.childs:
      terminated, result, jump_stmt = self.accept(child)
      if (not terminated):
        return False, None, None
      results.append(result)
    node.result = results
    node.terminated = True
    return node.terminated, node.result, None

  def BinaryOp(self, node):
    left_terminated, left_result, left_jump_stmt = self.accept(node.left)
    if not left_terminated:
      return False, None, None
    right_terminated, right_result, right_jump_stmt = self.accept(node.right)
    if not right_terminated:
      return False, None, None

    if self.is_optimizer() and ((left_result is None) or (right_result is None)):
      node.terminated = True
      node.result = None
      return node.terminated, node.result, None

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

    if node.op == '++' or node.op == '--':
      scope = self.get_scope()
      if node.left.__class__ is ast.VaExpression:
        scope.add(node.left.name, node.linespan[0], node.result)
        if scope.is_constant(node.left.name):
          is_constant = not self.is_in_conditional_section()
          scope.set_constant(node.left.name, is_constant)
      elif self.constant_folding and node.left.__class__ is ast.Const:
        node.replace(ast.Const(node.result, node.linespan))

    if self.constant_folding and not self.freeze_constant_folding:
      if node.left.__class__ is ast.Const and node.right.__class__ is ast.Const:
        linespan = (node.left.linespan[0], node.right.linespan[1])
        node.replace(ast.Const(node.result, linespan))
    node.terminated = True
    return node.terminated, node.result, None

  def AssignOp(self, node):
    right_terminated, right_result, right_jump_stmt = self.accept(node.right)
    if not right_terminated:
      return False, None, None

    scope = self.get_scope()
    if node.left.__class__ is ast.VaExpression:
      symbol = node.left.name
      scope.add(symbol, node.linespan[0], right_result)
      node.result = scope.get(symbol)
      is_constant = (node.right.__class__ is ast.Const) and (not self.is_in_conditional_section())
      scope.set_constant(symbol, is_constant)
    elif node.left.__class__ is ast.ArrayExpression:
      prev_freeze_constant_folding = self.freeze_constant_folding
      if self.constant_folding:
        self.freeze_constant_folding = True
      expr_terminated, expr_result, expr_jump_stmt = self.accept(node.left.expr)
      if self.constant_folding:
        self.freeze_constant_folding = prev_freeze_constant_folding
      if not expr_terminated:
        return False, None, None
      index_terminated, index_result, index_jump_stmt = self.accept(node.left.index)
      if not index_terminated:
        return False, None, None
      expr_result[index_result] = right_result
      node.result = expr_result
    else:
      raise ValueError

    node.terminated = True
    return node.terminated, node.result, None

  def UnaryOp(self, node):
    expr_terminated, expr_result, expr_jump_stmt = self.accept(node.expr)
    if not expr_terminated:
      return False, None, None

    if self.is_optimizer() and (expr_result is None):
      node.terminated = True
      node.result = None
      return node.terminated, node.result, None

    if node.op == '+':
      node.result = expr_result
    elif node.op == '-':
      node.result = -expr_result
    else:
      raise ValueError

    if self.constant_folding and not self.freeze_constant_folding:
      if node.expr.__class__ is ast.Const:
        node.replace(ast.Const(node.result, node.expr.linespan))
    node.terminated = True
    return node.terminated, node.result, None

  def FnExpression(self, node):
    expr_terminated, expr_result, expr_jump_stmt = self.accept(node.expr)
    if not expr_terminated:
      return False, None, None
    arguments_terminated, arguments_result, arguments_jump_stmt = self.accept(node.arguments)
    if not arguments_terminated:
      return False, None, None

    if expr_result.__class__ is Function:
      node.result = expr_result.run(*arguments_result)
    else:
      if not node.initialized:
        node.body = expr_result.body.clone()
        func_scope = SymbolTable(expr_result, self.global_scope)
        self.push_scope(func_scope, node.body.linespan[0])
        for i, parameter in enumerate(expr_result.parameterGroup.childs):
          func_scope.define(parameter.name, parameter.type, parameter.linespan[0], arguments_result[i])
        node.initialized = True

      body_terminated, body_result, body_jump_stmt = self.accept(node.body)
      if not body_terminated:
        return False, None, None
      self.pop_scope()
      node.result = body_result
    node.terminated = True
    return node.terminated, node.result, None

  def VaExpression(self, node):
    scope = self.get_scope()
    node.result = scope.get(node.name)
    if self.constant_folding and scope.is_constant(node.name) and (not self.freeze_constant_folding):
      node.replace(ast.Const(node.result, node.linespan))
    node.terminated = True
    return node.terminated, node.result, None

  def ArrayExpression(self, node):
    prev_freeze_constant_folding = self.freeze_constant_folding
    if self.constant_folding:
      self.freeze_constant_folding = True
    expr_terminated, expr_result, expr_jump_stmt = self.accept(node.expr)
    if self.constant_folding:
      self.freeze_constant_folding = prev_freeze_constant_folding
    if not expr_terminated:
      return False, None, None
    index_terminated, index_result, index_jump_stmt = self.accept(node.index)
    if not index_terminated:
      return False, None, None

    if self.is_optimizer() and (expr_result is None):
      node.terminated = True
      node.result = None
      return node.terminated, node.result, None

    node.result = expr_result[index_result]
    node.terminated = True
    return node.terminated, node.result, None
