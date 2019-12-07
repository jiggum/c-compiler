from helper import getVisitorFunc

class Node():
  def __init__(self, linespan=None):
    self.linespan = linespan
    self.visited = False
    self.terminated = False
    self.result = None

  def accept(self, visitor):
    return getVisitorFunc(visitor, self.__class__)(self)

  def is_empty(self):
    return False

  def update_linespan(self, linespan):
    self.linespan = linespan

  def clone(self):
    new_node = self.__class__(self.linespan)
    return new_node

  def get_excutable_lineno(self):
    return self.linespan[1]

class ArrayNode(Node):
  def __init__(self, child=None, linespan=None):
    super().__init__(linespan=linespan)
    self.childs = []
    if child != None:
      self.childs.append(child)

  def add(self, child):
    self.childs.append(child)

  def clone(self):
    new_node = self.__class__(linespan = self.linespan)
    for child in self.childs:
      new_node.add(child.clone())
    return new_node

class EmptyNode(Node):
  def is_empty(self):
    return True

  def clone(self):
    new_node = self.__class__()
    return new_node

class TypeNode(Node):
  def __init__(self, type=None, linespan=None):
    super().__init__(linespan=linespan)
    self.types = []
    if (type is not None):
      self.add_type(type)

  def get_type(self):
    if (len(self.types) > 0):
      return self.types[0]
    return None

  def add_type(self, type):
    self.types.append(type)

  def clone(self):
    new_node = self.__class__(linespan=self.linespan)
    for type in self.types:
      new_node.add_type(type)
    return new_node

class Const(Node):
  def __init__(self, value, linespan=None):
    super().__init__(linespan=linespan)
    self.value = value

  def clone(self):
    new_node = self.__class__(self.value, linespan=self.linespan)
    return new_node

class BaseSection(ArrayNode):
  def get_excutable_lineno(self):
    return self.linespan[0]

class RootSection(BaseSection):
  pass

class ScopelessSection(BaseSection):
  pass

class Section(BaseSection):
  pass

class Declaration(Node):
  def __init__(self, declarator, linespan=None):
    super().__init__(linespan=linespan)
    self.type = declarator.type
    self.name = declarator.name
    self.declarator = declarator

  def clone(self):
    new_node = self.__class__(self.declarator, linespan=self.linespan)
    new_node.type = self.type.clone()
    new_node.declarator = self.declarator.clone()
    return new_node

class FnDeclaration(Declaration):
  def __init__(self, declarator, body, linespan=None):
    super().__init__(declarator, linespan=linespan)
    self.parameterGroup = declarator.parameterGroup
    self.body = body

  def clone(self):
    new_node = self.__class__(self.declarator, self.body, linespan=self.linespan)
    new_node.type = self.type.clone()
    new_node.declarator = self.declarator.clone()
    new_node.parameterGroup = self.parameterGroup.clone()
    new_node.body = self.body.clone()
    return new_node

class VaDeclarationList(ArrayNode):
  pass

class Declarator(Node):
  def __init__(self, name, linespan=None):
    super().__init__(linespan=linespan)
    self.type = None
    self.name = name

  def add_type(self, typeNode):
    if self.type is None:
      self.type = typeNode
    else:
      self.type.add_type(typeNode.get_type())

  def clone(self):
    new_node = self.__class__(self.name, linespan=self.linespan)
    if (self.type != None):
      new_node.type = self.type.clone()
    return new_node

class FnDeclarator(Declarator):
  def __init__(self, name, parameterGroup=None, linespan=None):
    super().__init__(name, linespan=linespan)
    self.parameterGroup = parameterGroup

  def clone(self):
    new_node = self.__class__(self.name, self.parameterGroup, linespan=self.linespan)
    if (self.type != None):
      new_node.type = self.type.clone()
    new_node.parameterGroup = self.parameterGroup.clone()
    return new_node

class VaDeclarator(Declarator):
  pass

class ArrayDeclarator(Declarator):
  def __init__(self, name, size, linespan=None):
    super().__init__(name, linespan=linespan)
    self.size = int(size)

  def clone(self):
    new_node = self.__class__(self.name, self.size, linespan=self.linespan)
    if (self.type != None):
      new_node.type = self.type.clone()
    return new_node

class ParameterGroup(ArrayNode):
  pass

class ConditionalStatement(Node):
  def __init__(self, expr, then_section, else_section, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.then_section = then_section
    self.else_section = else_section

  def get_excutable_lineno(self):
    return self.expr.linespan[1]

  def clone(self):
    new_node = self.__class__(self.expr, self.then_section, self.else_section, linespan=self.linespan)
    new_node.expr = self.expr.clone()
    new_node.then_section = self.then_section.clone()
    new_node.else_section = self.else_section.clone()
    return new_node

class LoopStatement(Node):
  def __init__(self, expr, section, linespan=None):
    super().__init__(linespan=linespan)
    self.init_stmt = None
    self.expr = expr
    self.term_stmt = None
    self.section = section

  def get_excutable_lineno(self):
    return self.expr.linespan[1]

  def clone(self):
    new_node = self.__class__(self.expr, self.section, linespan=self.linespan)
    new_node.expr = self.expr.clone()
    new_node.section = self.section.clone()
    return new_node

class While(LoopStatement):
  def save_origin(self):
    self.origin_expr = self.expr.clone()
    self.origin_section = self.section.clone()

  def load_origin(self):
    self.expr = self.origin_expr.clone()
    self.section = self.origin_section.clone()

class For(LoopStatement):
  def __init__(self, init_stmt, expr, term_stmt, section, linespan=None):
    super().__init__(expr, section, linespan=linespan)
    self.init_stmt = init_stmt
    self.term_stmt = term_stmt
    self.origin_expr = None
    self.origin_section = None
    self.origin_term_stmt = None

  def get_excutable_lineno(self):
    return self.term_stmt.linespan[1]

  def save_origin(self):
    self.origin_expr = self.expr.clone()
    self.origin_section = self.section.clone()
    self.origin_term_stmt = self.term_stmt.clone()

  def load_origin(self):
    self.expr = self.origin_expr.clone()
    self.section = self.origin_section.clone()
    self.term_stmt = self.origin_term_stmt.clone()

  def clone(self):
    new_node = self.__class__(self.init_stmt, self.expr, self.term_stmt, self.section, linespan=self.linespan)
    new_node.expr = self.expr.clone()
    new_node.section = self.section.clone()
    new_node.init_stmt = self.init_stmt.clone()
    new_node.term_stmt = self.term_stmt.clone()
    return new_node

class JumpStatement(Node):
  pass

class Return(JumpStatement):
  def __init__(self, expr, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr

  def clone(self):
    new_node = self.__class__(self.expr, linespan=self.linespan)
    new_node.expr = self.expr.clone()
    return new_node

class Break(JumpStatement):
  pass

class Continue(JumpStatement):
  pass

class ArgumentList(ArrayNode):
  pass

class BinaryOp(Node):
  def __init__(self, op, left, right, linespan=None):
    super().__init__(linespan=linespan)
    self.left = left
    self.right = right
    self.op = op

  def clone(self):
    new_node = self.__class__(self.op, self.left, self.right, linespan=self.linespan)
    new_node.left = self.left.clone()
    new_node.right = self.right.clone()
    return new_node

class AssignOp(BinaryOp):
  def __init__(self, op, left, right, linespan=None):
    super().__init__(op, left, right, linespan=linespan)
    self.left = left
    self.op = '='
    if op == '=':
      self.right = right
    elif op == '+=':
      self.right = BinaryOp('+', self.left.clone(), right)
    elif op == '-=':
      self.right = BinaryOp('-', self.left.clone(), right)
    elif op == '*=':
      self.right = BinaryOp('*', self.left.clone(), right)
    elif op == '/=':
      self.right = BinaryOp('/', self.left.clone(), right)
    elif op == '%=':
      self.right = BinaryOp('%', self.left.clone(), right)
    else:
      raise ValueError

class UnaryOp(Node):
  def __init__(self, op, expr, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.op = op

  def clone(self):
    new_node = self.__class__(self.op, self.expr, linespan=self.linespan)
    new_node.expr = self.expr.clone()
    return new_node

class FnExpression(Node):
  def __init__(self, expr, arguments, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.arguments = arguments
    self.body = None # body will be cloned on FlowVisitor
    self.initialized = False

  def clone(self):
    new_node = self.__class__(self.expr, self.arguments, linespan=self.linespan)
    new_node.expr = self.expr.clone()
    new_node.arguments = self.arguments.clone()
    return new_node

class VaExpression(Node):
  def __init__(self, name, linespan=None):
    super().__init__(linespan=linespan)
    self.name = name
    self.pointer = None

  def set_pointer(self, type):
    self.pointer = type

  def clone(self):
    new_node = self.__class__(self.name, linespan=self.linespan)
    new_node.set_pointer(self.pointer)
    return new_node

class ArrayExpression(Node):
  def __init__(self, expr, index, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.index = index

  def clone(self):
    new_node = self.__class__(self.expr, self.index, linespan=self.linespan)
    new_node.expr = self.expr.clone()
    new_node.index = self.index.clone()
    return new_node
