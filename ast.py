import symbol_table as st
from helper import getVisitorFunc

class Node():
  def __init__(self, linespan=None):
    self.linespan = linespan
    self.parent = None
    self.scope = None
    self.current_line = None
    self.section_linespan = None

  def accept(self, visitor):
    getVisitorFunc(visitor, self.__class__)(self)

  def is_empty(self):
    return False

  def get_scope(self):
    return self.parent.get_scope()

  def get_current_line(self):
    return self.parent.get_current_line()

  def get_section_linespan(self):
    return self.parent.get_section_linespan()

  def update_current_line(self, line=1):
    self.parent.update_current_line(line)

  def update_linespan(self, linespan):
    self.linespan = linespan

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

class EmptyNode(Node):
  def is_empty(self):
    return True

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

class Const(Node):
  def __init__(self, value, linespan=None):
    super().__init__(linespan=linespan)
    self.value = value

class BaseSection(ArrayNode):
  def __init__(self, child=None, linespan=None):
    super().__init__(child=child, linespan=linespan)
    self.current_line = 1

  def get_current_line(self):
    return self.current_line

  def get_section_linespan(self):
    return self.linespan

  def update_current_line(self, line=1):
    self.current_line = line

class RootSection(BaseSection):
  def get_scope(self):
    return self.scope


class ScopelessSection(BaseSection):
  pass

class Section(BaseSection):
  def get_scope(self):
    return self.scope

class Declaration(Node):
  def __init__(self, declarator, linespan=None):
    super().__init__(linespan=linespan)
    self.type = declarator.type
    self.type.parent = self
    self.name = declarator.name

class FnDeclaration(Declaration):
  def __init__(self, declarator, body, linespan=None):
    super().__init__(declarator, linespan=linespan)
    self.parameterGroup = declarator.parameterGroup
    self.parameterGroup.parent = self
    self.body = body
    self.body.parent = self

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

class FnDeclarator(Declarator):
  def __init__(self, name, parameterGroup=None, linespan=None):
    super().__init__(name, linespan=linespan)
    self.parameterGroup = parameterGroup
    self.parameterGroup.parent = self

class VaDeclarator(Declarator):
  pass

class ArrayDeclarator(Declarator):
  def __init__(self, name, size, linespan=None):
    super().__init__(name, linespan=linespan)
    self.size = size

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

class LoopStatement(Node):
  def __init__(self, expr, section, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self
    self.section = section
    self.section.parent = self

class While(LoopStatement):
  pass

class For(LoopStatement):
  def __init__(self, init_stmt, expr, term_stmt, section, linespan=None):
    super().__init__(expr, section, linespan=linespan)
    self.init_stmt = init_stmt
    self.init_stmt.parent = self
    self.term_stmt = term_stmt
    self.term_stmt.parent = self

class JumpStatement(Node):
  pass

class Return(JumpStatement):
  def __init__(self, expr, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self

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

class AssignOp(BinaryOp):
  pass

class UnaryOp(Node):
  def __init__(self, op, expr, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self
    self.op = op

class FnExpression(Node):
  def __init__(self, expr, arguments, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self
    self.arguments = arguments
    self.arguments.parent = self

class VaExpression(Node):
  def __init__(self, name, linespan=None):
    super().__init__(linespan=linespan)
    self.name = name
    self.pointer = None

  def set_pointer(self, type):
    self.pointer = type

class ArrayExpression(Node):
  def __init__(self, expr, index, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self
    self.index = index
    self.index.parent = self
