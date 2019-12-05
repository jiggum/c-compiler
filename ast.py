from helper import getVisitorFunc

class Node():
  def __init__(self, linespan=None):
    self.linespan = linespan
    self.parent = None
    self.visited = False
    self.terminated = False
    self.result = None

  def accept(self, visitor):
    if (self.terminated):
      return self.terminated, self.result, None
    self.visited = True
    return getVisitorFunc(visitor, self.__class__)(self)

  def is_empty(self):
    return False

  def update_linespan(self, linespan):
    self.linespan = linespan

  def clone(self, parent):
    new_node = self.__class__(self.linespan)
    new_node.parent = parent
    return new_node

class ArrayNode(Node):
  def __init__(self, child=None, linespan=None):
    super().__init__(linespan=linespan)
    self.childs = []
    if child != None:
      child.parent = self
      self.childs.append(child)

  def add(self, child):
    child.parent = self
    self.childs.append(child)

  def clone(self, parent):
    new_node = self.__class__(linespan = self.linespan)
    new_node.parent = parent
    for child in self.childs:
      new_node.add(child.clone(new_node))
    return new_node

class EmptyNode(Node):
  def is_empty(self):
    return True

  def clone(self, parent):
    new_node = self.__class__()
    new_node.parent = parent
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

  def clone(self, parent):
    new_node = self.__class__(linespan=self.linespan)
    new_node.parent = parent
    for type in self.types:
      new_node.add_type(type)
    return new_node

class Const(Node):
  def __init__(self, value, linespan=None):
    super().__init__(linespan=linespan)
    self.value = value

  def clone(self, parent):
    new_node = self.__class__(self.value, linespan=self.linespan)
    new_node.parent = parent
    return new_node

class BaseSection(ArrayNode):
  pass

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
    self.type.parent = self
    self.name = declarator.name
    self.declarator = declarator

  def clone(self, parent):
    new_node = self.__class__(self.declarator, linespan=self.linespan)
    new_node.type = self.type.clone(new_node)
    new_node.declarator = self.declarator.clone(new_node)
    new_node.parent = parent
    return new_node

class FnDeclaration(Declaration):
  def __init__(self, declarator, body, linespan=None):
    super().__init__(declarator, linespan=linespan)
    self.parameterGroup = declarator.parameterGroup
    self.parameterGroup.parent = self
    self.body = body
    self.body.parent = self

  def clone(self, parent):
    new_node = self.__class__(self.declarator, self.body, linespan=self.linespan)
    new_node.type = self.type.clone(new_node)
    new_node.declarator = self.declarator.clone(new_node)
    new_node.parameterGroup = self.parameterGroup.clone(new_node)
    new_node.body = self.body.clone(new_node)
    new_node.parent = parent
    return new_node

class VaDeclartion(Declaration):
  pass

class VaDeclationList(ArrayNode):
  pass

class Declarator(Node):
  def __init__(self, name, linespan=None):
    super().__init__(linespan=linespan)
    self.type = None
    self.name = name

  def add_type(self, typeNode):
    if self.type is None:
      self.type = typeNode
      self.type.parent = self
    else:
      self.type.add_type(typeNode.get_type())

  def clone(self, parent):
    new_node = self.__class__(self.name, linespan=self.linespan)
    if (self.type != None):
      new_node.type = self.type.clone(new_node)
    new_node.parent = parent
    return new_node

class FnDeclarator(Declarator):
  def __init__(self, name, parameterGroup=None, linespan=None):
    super().__init__(name, linespan=linespan)
    self.parameterGroup = parameterGroup
    self.parameterGroup.parent = self

  def clone(self, parent):
    new_node = self.__class__(self.name, self.parameterGroup, linespan=self.linespan)
    if (self.type != None):
      new_node.type = self.type.clone(new_node)
    new_node.parameterGroup = self.parameterGroup.clone(new_node)
    new_node.parent = parent
    return new_node

class VaDeclarator(Declarator):
  pass

class ArrayDeclarator(Declarator):
  def __init__(self, name, size, linespan=None):
    super().__init__(name, linespan=linespan)
    self.size = size

  def clone(self, parent):
    new_node = self.__class__(self.name, self.size, linespan=self.linespan)
    if (self.type != None):
      new_node.type = self.type.clone(new_node)
    new_node.parent = parent
    return new_node

class ParameterGroup(ArrayNode):
  pass

class ConditionalStatement(Node):
  def __init__(self, expr, then_section, else_section, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self
    self.then_section = then_section
    self.then_section.parent = self
    self.else_section = else_section
    self.else_section.parent = self

  def clone(self, parent):
    new_node = self.__class__(self.expr, self.then_section, self.else_section, linespan=self.linespan)
    new_node.expr = self.expr.clone(new_node)
    new_node.then_section = self.then_section.clone(new_node)
    new_node.else_section = self.else_section.clone(new_node)
    new_node.parent = parent
    return new_node

class LoopStatement(Node):
  def __init__(self, expr, section, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self
    self.section = section
    self.section.parent = self

  def clone(self, parent):
    new_node = self.__class__(self.expr, self.section, linespan=self.linespan)
    new_node.expr = self.expr.clone(new_node)
    new_node.section = self.section.clone(new_node)
    new_node.parent = parent
    return new_node

class While(LoopStatement):
  pass

class For(LoopStatement):
  def __init__(self, init_stmt, expr, term_stmt, section, linespan=None):
    super().__init__(expr, section, linespan=linespan)
    self.init_stmt = init_stmt
    self.init_stmt.parent = self
    self.term_stmt = term_stmt
    self.term_stmt.parent = self

  def clone(self, parent):
    new_node = self.__class__(self.init_stmt, self.expr, self.term_stmt, self.section, linespan=self.linespan)
    new_node.expr = self.expr.clone(new_node)
    new_node.section = self.section.clone(new_node)
    new_node.init_stmt = self.init_stmt.clone(new_node)
    new_node.term_stmt = self.term_stmt.clone(new_node)
    new_node.parent = parent
    return new_node

class JumpStatement(Node):
  pass

class Return(JumpStatement):
  def __init__(self, expr, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self

  def clone(self, parent):
    new_node = self.__class__(self.expr, linespan=self.linespan)
    new_node.expr = self.expr.clone(new_node)
    new_node.parent = parent
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
    self.left.parent = self
    self.right = right
    self.right.parent = self
    self.op = op

  def clone(self, parent):
    new_node = self.__class__(self.op, self.left, self.right, linespan=self.linespan)
    new_node.left = self.left.clone(new_node)
    new_node.right = self.right.clone(new_node)
    new_node.parent = parent
    return new_node

class AssignOp(BinaryOp):
  pass

class UnaryOp(Node):
  def __init__(self, op, expr, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self
    self.op = op

  def clone(self, parent):
    new_node = self.__class__(self.op, self.expr, linespan=self.linespan)
    new_node.expr = self.expr.clone(new_node)
    new_node.parent = parent
    return new_node

class FnExpression(Node):
  def __init__(self, expr, arguments, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self
    self.arguments = arguments
    self.arguments.parent = self

  def clone(self, parent):
    new_node = self.__class__(self.expr, self.arguments, linespan=self.linespan)
    new_node.expr = self.expr.clone(new_node)
    new_node.arguments = self.arguments.clone(new_node)
    new_node.parent = parent
    return new_node

class VaExpression(Node):
  def __init__(self, name, linespan=None):
    super().__init__(linespan=linespan)
    self.name = name
    self.pointer = None

  def set_pointer(self, type):
    self.pointer = type

  def clone(self, parent):
    new_node = self.__class__(self.name, linespan=self.linespan)
    new_node.set_pointer(self.pointer)
    new_node.parent = parent
    return new_node

class ArrayExpression(Node):
  def __init__(self, expr, index, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self
    self.index = index
    self.index.parent = self

  def clone(self, parent):
    new_node = self.__class__(self.expr, self.index, linespan=self.linespan)
    new_node.expr = self.expr.clone(new_node)
    new_node.index = self.index.clone(new_node)
    new_node.parent = parent
    return new_node
