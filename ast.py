class Node():
  def __init__(self, child=None):
    self.childs = []
    if child != None:
      self.childs.append(child)

  def is_leaf(self):
      return len(self.childs) == 0

  def add(self, child):
    self.childs.append(child)

  def is_empty(self):
    return False

class EmptyNode(Node):
  def __init__(self):
    super().__init__()

  def is_empty(self):
    return True

class TypeNode(Node):
  def __init__(self, type=None):
    super().__init__()
    self.types = []
    if (type is not None):
      self.add_type(type)

  def get_type(self):
    if (len(self.types) > 0):
      return self.types[0]
    return None

  def add_type(self, type):
    self.types.append(type)

class Const(Node):
  def __init__(self, value):
    super().__init__()
    self.value = value

class RootSection(Node):
  pass

class Section(Node):
  pass

class Declaration(Node):
  def __init__(self, declarator):
    super().__init__()
    self.type = declarator.type
    self.name = declarator.name

class FnDeclaration(Declaration):
  def __init__(self, declarator, body):
    super().__init__(declarator)
    self.body = body

class VaDeclartion(Declaration):
  pass

class VaDeclationList(Node):
  pass

class Declarator(Node):
  def __init__(self, name):
    super().__init__()
    self.type = None
    self.name = name

  def add_type(self, typeNode):
    if self.type is None:
      self.type = typeNode
    else:
      self.type.add_type(typeNode.get_type())

class FnDeclarator(Declarator):
  def __init__(self, name, parameterGroup=None):
    super().__init__(name)
    self.parameterGroup = parameterGroup

class VaDeclarator(Declarator):
  pass

class ArrayDeclarator(Declarator):
  def __init__(self, name, size):
    super().__init__(name)
    self.size = size

class ParameterGroup(Node):
  pass

class ConditionalStatement(Node):
  def __init__(self, expr, then_section, else_section):
    super().__init__()
    self.expr = expr
    self.then_section = then_section
    self.else_section = else_section

class LoopStatement(Node):
  def __init__(self, expr, section):
    super().__init__()
    self.expr = expr
    self.section = section

class While(LoopStatement):
  pass

class For(LoopStatement):
  def __init__(self, init_stmt, expr, term_stmt, section):
    super().__init__(expr, section)
    self.init_stmt = init_stmt
    self.term_stmt = term_stmt

class JumpStatement(Node):
  pass

class Return(JumpStatement):
  def __init__(self, expr):
    super().__init__()
    self.expr = expr

class Break(JumpStatement):
  pass

class Continue(JumpStatement):
  pass

class ArgumentList(Node):
  pass

class BinaryOp(Node):
  def __init__(self, op, left, right):
    super().__init__()
    self.left = left
    self.right = right
    self.op = op

class AssignOp(BinaryOp):
  pass

class UnaryOp(Node):
  def __init__(self, op, expr):
    super().__init__()
    self.expr = expr
    self.op = op

class FnExpression(Node):
  def __init__(self, expr, arguments):
    super().__init__()
    self.expr = expr
    self.arguments = arguments

class VaExpression(Node):
  def __init__(self, name):
    super().__init__()
    self.name = name
    self.pointer = None

  def set_pointer(self, type):
    self.pointer = type

class ArrayExpression(Node):
  def __init__(self, expr, index):
    super().__init__()
    self.expr = expr
    self.index = index

