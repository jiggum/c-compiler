import symbol_table as st

class Node():
  def __init__(self, lineno=None):
    self.lineno = lineno
    self.parent = None
    self.callstack = None
    self.scope = None
    self.current_line = None
    self.section_lineno = None

  def is_empty(self):
    return False

  def get_scope(self):
    self.parent.get_scope()

  def get_callstack(self):
    return self.parent.get_callstack()

  def get_current_line(self):
    return self.parent.get_current_line()

  def update_current_line(self, line):
    self.parent.update_current_line(line)

  def get_section_lineno(self):
    return self.parent.get_section_lineno()

  def push_callstack(self, node):
    return self.parent.push_callstack(node)

  def pop_callstack(self):
    return self.parent.pop_callstack()

  def __str__(self, level=0, infos={}):
    ret = "\t"*level + str(self.lineno) + ':' + self.__class__.__name__ + infos.__str__() + '\n'
    return ret

class ArrayNode(Node):
  def __init__(self, child=None, lineno=None):
    super().__init__(lineno=lineno)
    self.childs = []
    if child != None:
      child.parent = self
      self.childs.append(child)

  def add(self, child):
    child.parent = self
    self.childs.append(child)


  def __str__(self, level=0, infos={}):
    ret = super().__str__(level, infos)
    for child in self.childs:
        ret += child.__str__(level+1)
    return ret


class EmptyNode(Node):
  def is_empty(self):
    return True

class TypeNode(Node):
  def __init__(self, type=None, lineno=None):
    super().__init__(lineno=lineno)
    self.types = []
    if (type is not None):
      self.add_type(type)

  def get_type(self):
    if (len(self.types) > 0):
      return self.types[0]
    return None

  def add_type(self, type):
    self.types.append(type)

  def __str__(self, level=0, infos={}):
    infos_ = {'types': self.types}
    infos_.update(infos)
    return super().__str__(level, infos_)

class Const(Node):
  def __init__(self, value, lineno=None):
    super().__init__(lineno=lineno)
    self.value = value

  def __str__(self, level=0, infos={}):
    infos_ = {'value': self.value}
    infos_.update(infos)
    return super().__str__(level, infos_)

class BaseSection(ArrayNode):
  def __init__(self, child=None, lineno=None):
    super().__init__(child=child, lineno=lineno)
    self.current_line = 1

  def get_current_line(self):
    return self.current_line

  def get_section_lineno(self):
    return self.lineno

  def update_current_line(self, line):
    self.current_line = line

  def pop_callstack(self):
    return self.callstack.pop()

class RootSection(BaseSection):
  def __init__(self, child=None, lineno=None):
    super().__init__(child=child, lineno=lineno)
    self.callstack = []

  def get_scope(self):
    return self.scope

  def get_callstack(self):
    return self.callstack

  def push_callstack(self, node):
    self.callstack.append(node)

class ScopelessSection(BaseSection):
  pass

class Section(BaseSection):
  def get_scope(self):
    return self.scope

class Declaration(Node):
  def __init__(self, declarator, lineno=None):
    super().__init__(lineno=lineno)
    self.type = declarator.type
    self.type.parent = self
    self.name = declarator.name

  def __str__(self, level=0, infos={}):
    infos_ = {'name': self.name}
    infos_.update(infos)
    ret = super().__str__(level, infos_)
    ret += self.type.__str__(level+1)
    return ret

class FnDeclaration(Declaration):
  def __init__(self, declarator, body, lineno=None):
    super().__init__(declarator, lineno=lineno)
    self.parameterGroup = declarator.parameterGroup
    self.parameterGroup.parent = self
    self.body = body
    self.body.parent = self


  def __str__(self, level=0, infos={}):
    ret = super().__str__(level, infos)
    ret += self.parameterGroup.__str__(level+1)
    ret += self.body.__str__(level+1)
    return ret

class VaDeclartion(Declaration):
  pass

class VaDeclationList(ArrayNode):
  pass

class Declarator(Node):
  def __init__(self, name, lineno=None):
    super().__init__(lineno=lineno)
    self.type = None
    self.name = name

  def add_type(self, typeNode):
    if self.type is None:
      self.type = typeNode
      self.type.parent = self
    else:
      self.type.add_type(typeNode.get_type())

  def __str__(self, level=0, infos={}):
    infos_ = {'name': self.name}
    infos_.update(infos)
    ret = super().__str__(level, infos_)
    ret += self.type.__str__(level+1)
    return ret

class FnDeclarator(Declarator):
  def __init__(self, name, parameterGroup=None, lineno=None):
    super().__init__(name, lineno=lineno)
    self.parameterGroup = parameterGroup
    self.parameterGroup.parent = self

  def __str__(self, level=0, infos={}):
    ret = super().__str__(level, infos)
    ret += self.parameterGroup.__str__(level+1)
    return ret

class VaDeclarator(Declarator):
  pass

class ArrayDeclarator(Declarator):
  def __init__(self, name, size, lineno=None):
    super().__init__(name, lineno=lineno)
    self.size = size

  def __str__(self, level=0, infos={}):
    infos_ = {'size': self.size}
    infos_.update(infos)
    return super().__str__(level, infos_)

class ParameterGroup(ArrayNode):
  pass

class ConditionalStatement(Node):
  def __init__(self, expr, then_section, else_section, lineno=None):
    super().__init__(lineno=lineno)
    self.expr = expr
    self.expr.parent = self
    self.then_section = then_section
    self.then_section.parent = self
    self.else_section = else_section
    self.else_section.parent = self

  def __str__(self, level=0, infos={}):
    ret = super().__str__(level, infos)
    ret += self.expr.__str__(level+1)
    ret += self.then_section.__str__(level+1)
    ret += self.else_section.__str__(level+1)
    return ret

class LoopStatement(Node):
  def __init__(self, expr, section, lineno=None):
    super().__init__(lineno=lineno)
    self.expr = expr
    self.expr.parent = self
    self.section = section
    self.section.parent = self

  def __str__(self, level=0, infos={}):
    ret = super().__str__(level, infos)
    ret += self.expr.__str__(level+1)
    ret += self.section.__str__(level+1)
    return ret

class While(LoopStatement):
  pass

class For(LoopStatement):
  def __init__(self, init_stmt, expr, term_stmt, section, lineno=None):
    super().__init__(expr, section, lineno=lineno)
    self.init_stmt = init_stmt
    self.init_stmt.parent = self
    self.term_stmt = term_stmt
    self.term_stmt.parent = self

  def __str__(self, level=0, infos={}):
    ret = super().__str__(level, infos)
    ret += self.init_stmt.__str__(level+1)
    ret += self.term_stmt.__str__(level+1)
    return ret

class JumpStatement(Node):
  pass

class Return(JumpStatement):
  def __init__(self, expr, lineno=None):
    super().__init__(lineno=lineno)
    self.expr = expr
    self.expr.parent = self

  def __str__(self, level=0, infos={}):
    ret = super().__str__(level, infos)
    ret += self.expr.__str__(level+1)
    return ret

class Break(JumpStatement):
  pass

class Continue(JumpStatement):
  pass

class ArgumentList(ArrayNode):
  pass

class BinaryOp(Node):
  def __init__(self, op, left, right, lineno=None):
    super().__init__(lineno=lineno)
    self.left = left
    self.left.parent = self
    self.right = right
    self.right.parent = self
    self.op = op

  def __str__(self, level=0, infos={}):
    infos_ = {'op': self.op}
    infos_.update(infos)
    ret = super().__str__(level, infos_)
    ret += self.left.__str__(level+1)
    ret += self.right.__str__(level+1)
    return ret

class AssignOp(BinaryOp):
  pass

class UnaryOp(Node):
  def __init__(self, op, expr, lineno=None):
    super().__init__(lineno=lineno)
    self.expr = expr
    self.expr.parent = self
    self.op = op

  def __str__(self, level=0, infos={}):
    infos_ = {'op': self.op}
    infos_.update(infos)
    ret = super().__str__(level, infos_)
    ret += self.expr.__str__(level+1)
    return ret

class FnExpression(Node):
  def __init__(self, expr, arguments, lineno=None):
    super().__init__(lineno=lineno)
    self.expr = expr
    self.expr.parent = self
    self.arguments = arguments
    self.arguments.parent = self

  def __str__(self, level=0, infos={}):
    ret = super().__str__(level, infos)
    ret += self.arguments.__str__(level+1)
    ret += self.expr.__str__(level+1)
    return ret

class VaExpression(Node):
  def __init__(self, name, lineno=None):
    super().__init__(lineno=lineno)
    self.name = name
    self.pointer = None

  def set_pointer(self, type):
    self.pointer = type

  def __str__(self, level=0, infos={}):
    infos_ = {'name': self.name, 'pointer': self.pointer}
    infos_.update(infos)
    return super().__str__(level, infos_)

class ArrayExpression(Node):
  def __init__(self, expr, index, lineno=None):
    super().__init__(lineno=lineno)
    self.expr = expr
    self.expr.parent = self
    self.index = index
    self.index.parent = self

  def __str__(self, level=0, infos={}):
    ret = super().__str__(level, infos)
    ret += self.index.__str__(level+1)
    ret += self.expr.__str__(level+1)
    return ret

