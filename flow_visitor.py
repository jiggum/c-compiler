from symbol_table import SymbolTable

class FlowVisitor:
  def __init__(self, parent=None):
    self.parent = parent
    self.current_lineno = 1
    self.scopes = [SymbolTable()]
    self.line_num = 0

  def add_linenum(self, line_num):
    self.line_num += line_num

  def push_scope(self, scope):
    self.scopes.push(scope)

  def pop_scope(self):
    return self.scopes.pop()

  def get_scope(self):
    return self.scopes[-1]

  def RootSection(self, node):
    for child in node.childs:
      terminated, result, jump_stmt = child.accept(self)
      if not terminated:
        return terminated, result, None
    node.terminated = True
    return node.terminated, node.result, None

  def FnDeclaration(self, node):
    self.get_scope().add(node.name, node.body)
    if node.name == 'main':
      if not node.body.visited:
        self.current_lineno = node.body.linespan[0]
      terminated, result, jump_stmt = node.body.accept(self)
      if (not terminated):
        return terminated, None, None
    node.terminated = True
    return node.terminated, node.result, None

  def Section(self, node):
    if (not node.visited):
      self.push_scope(SymbolTable(self.get_scope()))
    for child in node.childs:
      if not child.visited:
        child_lineno_end = child.linespan[1]
        if child_lineno_end > self.current_lineno + self.line_num - 1:
          self.current_lineno += self.line_num
          self.line_num = 0
          return False, None, None
        else:
          self.line_num -= child_lineno_end + 1 - self.current_lineno
          self.current_lineno = child_lineno_end

      prev_terminated = child.terminated
      terminated, result, jump_stmt = child.accept(self)
      if (not terminated):
        return False, None, None
      elif jump_stmt is not None:
        print('jump_stmt2', jump_stmt)
      if not prev_terminated:
        self.current_lineno += 1
    self.pop_scope()
    node.terminated = True
    return node.terminated, node.result, None

  def VaDeclationList(self, node):
    for child in node.childs:
      child.accept(self)
    node.terminated = True
    return node.terminated, node.result, None

  def VaDeclarator(self, node):
    scope = self.get_scope()
    scope.add(node.name, node)
    scope.add_log(node.name, node.linespan[0], None)

  def ArrayDeclarator(self, node):
    scope = self.get_scope()
    scope.add(node.name, node)
    scope.add_log(node.name, node.linespan[0], [])

  def AssignOp(self, node):
    # left_result should be VaExpression
    left_terminated, left_result, left_jump_stmt = node.left.accept(self)
    if not left_terminated:
      return False, None, None
    right_terminated, right_result, right_jump_stmt = node.right.accept(self)
    if not right_terminated:
      return False, None, None
    scope = self.get_scope()
    symbol = left_result.name
    scope.add_log(symbol, node.linespan[0], right_result)
    node.terminated = True
    node.result = scope.get(symbol)
    return node.terminated, node.result, None

  def VaExpression(self, node):
    node.terminated = True
    node.result = node
    return node.terminated, node.result, None

  def Const(self, node):
    node.terminated = True
    node.result = node.value
    return node.terminated, node.result, None
