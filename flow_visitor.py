from symbol_table import SymbolTable
import ast

class FlowVisitor:
  def __init__(self, parent=None):
    self.parent = parent
    self.scopes = [SymbolTable()]
    self.linenos = [1]
    self.line_num = 0

  def accept(self, node):
    if (node.terminated):
      return node.terminated, node.result, None
    terminated, result, jum_stmt = node.accept(self)
    node.visited = True
    return terminated, result, jum_stmt

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

  def RootSection(self, node):
    for child in node.childs:
      terminated, result, jump_stmt = self.accept(child)
      if not terminated:
        return terminated, result, None
    node.terminated = True
    return node.terminated, node.result, None

  def FnDeclaration(self, node):
    if not node.visited:
      scope = self.get_scope()
      scope.add(node.name, node.linespan[0], node)
    if node.name == 'main':
      if not node.body.visited:
        self.update_lineno(node.body.linespan[0])
      terminated, result, jump_stmt = self.accept(node.body)
      if (not terminated):
        return terminated, None, None
    node.terminated = True
    return node.terminated, node.result, None

  def BaseSection(self, node):
    for child in node.childs:
      if not child.visited:
        child_lineno = child.get_excutable_lineno()
        if child_lineno > self.get_lineno() + self.line_num - 1:
          self.update_lineno(self.get_lineno() + self.line_num)
          self.line_num = 0
          return False, None, None
        else:
          self.line_num -= child_lineno + 1 - self.get_lineno()
          self.update_lineno(child_lineno)
      print(child, self.get_lineno(), self.line_num)
      prev_terminated = child.terminated
      terminated, result, jump_stmt = self.accept(child)
      if (not terminated):
        return False, None, None
      elif jump_stmt is not None:
        node.terminated = True
        node.result = jump_stmt.result
        return node.terminated, node.result, jump_stmt
      if not prev_terminated:
        self.update_lineno(self.get_lineno() + 1)
    node.terminated = True
    return node.terminated, node.result, None

  def Section(self, node):
    if (not node.visited):
      self.push_scope(SymbolTable(self.get_scope()), node.linespan[0])
    terminated, result, jum_stmt = self.BaseSection(node)
    if (terminated):
      self.pop_scope()
    return terminated, result, jum_stmt

  def VaDeclationList(self, node):
    for child in node.childs:
      self.accept(child)
    node.terminated = True
    return node.terminated, node.result, None

  def VaDeclarator(self, node):
    scope = self.get_scope()
    scope.add(node.name, node.linespan[0], None)
    return True, None, None

  def ArrayDeclarator(self, node):
    scope = self.get_scope()
    scope.add(node.name, node.linespan[0], [])
    return True, None, None

  def AssignOp(self, node):
    symbol = None
    if (node.left.__class__ is ast.VaExpression):
      symbol = node.left.name
    right_terminated, right_result, right_jump_stmt = self.accept(node.right)
    if not right_terminated:
      return False, None, None
    scope = self.get_scope()
    scope.add(symbol, node.linespan[0], right_result)
    node.terminated = True
    node.result = scope.get(symbol)
    return node.terminated, node.result, None

  def VaExpression(self, node):
    node.result = self.get_scope().get(node.name)
    node.terminated = True
    return node.terminated, node.result, None

  def Const(self, node):
    node.terminated = True
    node.result = node.value
    return node.terminated, node.result, None

  def FnExpression(self, node):
    expr_terminated, expr_result, expr_jump_stmt = self.accept(node.expr)
    if not expr_terminated:
      return False, None, None
    arguments_terminated, arguments_result, arguments_jump_stmt = self.accept(node.arguments)
    if not arguments_terminated:
      return False, None, None

    if not node.initialized:
      scope = self.get_scope()
      symbol = expr_result.name
      func_node = scope.get(symbol)
      node.body = func_node.body.clone(node)
      func_scope = SymbolTable()
      self.push_scope(func_scope, node.body.linespan[0])
      for i, parameter in enumerate(func_node.parameterGroup.childs):
        func_scope.add(parameter.name, parameter.linespan[0], arguments_result[i])
      node.initialized = True

    body_terminated, body_result, body_jump_stmt = self.accept(node.body)
    if not body_terminated:
      return False, None, None
    self.pop_scope()
    node.terminated = True
    node.result = body_result
    return node.terminated, node.result, body_jump_stmt

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

  def Return(self, node):
    terminated, result, jump_stmt = self.accept(node.expr)
    if (not terminated):
      return False, None, None
    node.terminated = True
    node.result = result
    return node.terminated, node.result, node

  def BinaryOp(self, node):
    left_terminated, left_result, left_jump_stmt = self.accept(node.left)
    if not left_terminated:
      return False, None, None
    right_terminated, right_result, right_jump_stmt = self.accept(node.right)
    if not right_terminated:
      return False, None, None

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
      if node.left.__class__ is ast.VaExpression:
        self.get_scope().add(node.left.name, node.linespan[0], node.result)
    elif node.op == '--':
      node.result = left_result - right_result
      if node.left.__class__ is ast.VaExpression:
        self.get_scope().add(node.left.name, node.linespan[0], node.result)
    else:
      raise ValueError

    node.terminated = True
    return node.terminated, node.result, node

  def For(self, node):
    if not node.visited:
      node.save_origin()
      scope = self.get_scope()
      self.push_scope(scope, node.linespan[0])

    init_stmt_terminated, init_stmt_result, init_stmt_jump_stmt = self.accept(node.init_stmt)
    if not init_stmt_terminated:
      return False, None, None
    print('line_num', self.line_num)
    while True:
      expr_terminated, expr_result, expr_jump_stmt = self.accept(node.expr)
      if not expr_terminated:
        return False, None, None
      if not expr_result:
        self.pop_scope()
        self.get_scope().trace('i')
        self.get_scope().trace('sum')
        print('not expr_result')
        node.terminated = True
        self.update_lineno(node.linespan[1] + 1)
        return node.terminated, node.result, None

      if not node.section.visited:
        section_lineno = node.section.get_excutable_lineno()
        if section_lineno > self.get_lineno() + self.line_num - 1:
          self.update_lineno(self.get_lineno() + self.line_num)
          self.line_num = 0
          return False, None, None
        else:
          self.line_num -= section_lineno - self.get_lineno()
          self.update_lineno(section_lineno)
      terminated, result, jump_stmt = self.accept(node.section)
      if (not terminated):
        return False, None, None
      elif jump_stmt is not None:
        node.terminated = True
        node.result = jump_stmt.result
        return node.terminated, node.result, jump_stmt

      term_stmt_terminated, term_stmt_result, term_stmt_jump_stmt = self.accept(node.term_stmt)
      if (not term_stmt_terminated):
        return False, None, None

      node.load_origin()
      self.update_lineno(node.linespan[0])
