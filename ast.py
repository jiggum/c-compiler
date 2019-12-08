from helper import getVisitorFunc, props

class Node():
  def __init__(self, linespan=None):
    self.linespan = linespan
    self.visited = False
    self.terminated = False
    self.result = None
    self.use_paren = False
    self.parent = None
    self.used = True
    self.default_reachable = False

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

  def need_semi(self):
    return True

  def replace(self, node):
    for prop in props(self.parent):
      if getattr(self.parent, prop) == self:
        setattr(self.parent, prop, node)
        node.parent = self.parent
        break

    if hasattr(self.parent, 'childs'):
      for i, child in enumerate(self.parent.childs):
        if child == self:
          self.parent.childs[i] = node
          node.parent = self.parent
          break

  def is_rechable(self):
    return self.default_reachable or self.visited or self.used

class ArrayNode(Node):
  def __init__(self, child=None, linespan=None):
    super().__init__(linespan=linespan)
    self.childs = []
    if child != None:
      self.add(child)

  def add(self, child):
    self.childs.append(child)
    child.parent = self

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
    self.default_reachable = True

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
    return self.__class__(self.value, linespan=self.linespan)

class BaseSection(ArrayNode):
  def get_excutable_lineno(self):
    return self.linespan[0]

class RootSection(BaseSection):
  def __init__(self, child=None, linespan=None):
    super().__init__(child=child, linespan=linespan)
    self.default_reachable = True

class Section(BaseSection):
  pass

class Declaration(Node):
  def __init__(self, declarator, linespan=None):
    super().__init__(linespan=linespan)
    self.type = declarator.type
    self.type.parent = self
    self.name = declarator.name
    self.declarator = declarator
    self.declarator.parent = self
    self.default_reachable = True

  def clone(self):
    return self.__class__(self.declarator.clone(), linespan=self.linespan)

class FnDeclaration(Declaration):
  def __init__(self, declarator, body, linespan=None):
    super().__init__(declarator, linespan=linespan)
    self.parameterGroup = declarator.parameterGroup
    self.parameterGroup.parent = self
    self.body = body
    self.body.parent = self

  def need_semi(self):
    return False

  def clone(self):
    return self.__class__(self.declarator.clone(), self.body.clone(), linespan=self.linespan)

class VaDeclarationList(ArrayNode):
  pass

class Declarator(Node):
  def __init__(self, name, linespan=None):
    super().__init__(linespan=linespan)
    self.type = None
    self.name = name
    self.default_reachable = True

  def add_type(self, typeNode):
    if self.type is None:
      self.type = typeNode
      self.type.parent = self
    else:
      self.type.add_type(typeNode.get_type())

  def clone(self):
    new_node = self.__class__(self.name, linespan=self.linespan)
    if (self.type != None):
      new_node.add_type(self.type.clone())
    return new_node

class FnDeclarator(Declarator):
  def __init__(self, name, parameterGroup=None, linespan=None):
    super().__init__(name, linespan=linespan)
    self.parameterGroup = parameterGroup
    self.parameterGroup.parent = self

  def clone(self):
    new_node = self.__class__(self.name, self.parameterGroup.clone(), linespan=self.linespan)
    if (self.type != None):
      new_node.add_type(self.type.clone())
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
      new_node.add_type(self.type.clone())
    return new_node

class ParameterGroup(ArrayNode):
  def __init__(self, child=None, linespan=None):
    super().__init__(child=child, linespan=linespan)
    self.default_reachable = True

class ConditionalStatement(Node):
  def __init__(self, expr, then_section, else_section, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self
    self.then_section = then_section
    self.then_section.parent = self
    self.else_section = else_section
    self.else_section.parent = self

  def get_excutable_lineno(self):
    return self.expr.linespan[1]

  def need_semi(self):
    return False

  def clone(self):
    return self.__class__(self.expr.clone(), self.then_section.clone(), self.else_section.clone(), linespan=self.linespan)

class LoopStatement(Node):
  def __init__(self, expr, section, linespan=None):
    super().__init__(linespan=linespan)
    self.init_stmt = None
    self.expr = expr
    self.expr.parent = self
    self.term_stmt = None
    self.section = section
    self.section.parent = self

  def get_excutable_lineno(self):
    return self.expr.linespan[1]

  def need_semi(self):
    return False

  def clone(self):
    return self.__class__(self.expr.clone(), self.section.clone(), linespan=self.linespan)

class While(LoopStatement):
  def save_origin(self):
    self.origin_expr = self.expr.clone()
    self.origin_expr.parent = self
    self.origin_section = self.section.clone()
    self.origin_section.parent = self

  def load_origin(self):
    self.expr = self.origin_expr.clone()
    self.expr.parent = self
    self.section = self.origin_section.clone()
    self.section.parent = self

class For(LoopStatement):
  def __init__(self, init_stmt, expr, term_stmt, section, linespan=None):
    super().__init__(expr, section, linespan=linespan)
    self.init_stmt = init_stmt
    self.init_stmt.parent = self
    self.term_stmt = term_stmt
    self.term_stmt.parent = self
    self.origin_expr = None
    self.origin_section = None
    self.origin_term_stmt = None

  def get_excutable_lineno(self):
    return self.term_stmt.linespan[1]

  def save_origin(self):
    self.origin_expr = self.expr.clone()
    self.origin_expr.parent = self
    self.origin_section = self.section.clone()
    self.origin_section.parent = self
    self.origin_term_stmt = self.term_stmt.clone()
    self.origin_term_stmt.parent = self

  def load_origin(self):
    self.expr = self.origin_expr.clone()
    self.expr.parent = self
    self.section = self.origin_section.clone()
    self.section.parent = self
    self.term_stmt = self.origin_term_stmt.clone()
    self.term_stmt.parent = self

  def clone(self):
    return self.__class__(self.init_stmt.clone(), self.expr.clone(), self.term_stmt.clone(), self.section.clone(), linespan=self.linespan)

class JumpStatement(Node):
  pass

class Return(JumpStatement):
  def __init__(self, expr, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self

  def clone(self):
    return self.__class__(self.expr.clone(), linespan=self.linespan)

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

  def clone(self):
    return self.__class__(self.op, self.left.clone(), self.right.clone(), linespan=self.linespan)

class AssignOp(BinaryOp):
  def __init__(self, op, left, right, linespan=None):
    super().__init__(op, left, right, linespan=linespan)
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
    self.right.parent = self

class UnaryOp(Node):
  def __init__(self, op, expr, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self
    self.op = op

  def clone(self):
    return self.__class__(self.op, self.expr.clone(), linespan=self.linespan)

class FnExpression(Node):
  def __init__(self, expr, arguments, linespan=None):
    super().__init__(linespan=linespan)
    self.expr = expr
    self.expr.parent = self
    self.arguments = arguments
    self.arguments.parent = self
    self.body = None # body will be cloned on FlowVisitor
    self.initialized = False

  def clone(self):
    return self.__class__(self.expr.clone(), self.arguments.clone(), linespan=self.linespan)

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
    self.expr.parent = self
    self.index = index
    self.index.parent = self

  def clone(self):
    return self.__class__(self.expr.clone(), self.index.clone(), linespan=self.linespan)
