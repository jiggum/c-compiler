class PrintVisitor:
  def __init__(self):
    self.s = ''
    self._indent = 0

  def __str__(self):
    return self.s

  def indent(self):
    self._indent += 1

  def unindent(self):
    self._indent -= 1

  def save_s(self, node, infos={}):
    self.s += "    " * self._indent + str(node.linespan) + ':' + node.__class__.__name__ + infos.__str__() + str(node) + '[rechable:' + str(node.is_rechable()) + ', used:' + str(node.used) + ']\n'

  def Node(self, node):
    self.save_s(node)

  def ArrayNode(self, node):
    self.save_s(node)
    self.indent()
    for child in node.childs:
      child.accept(self)
    self.unindent()

  def TypeNode(self, node):
    self.save_s(node, {'types': node.types})

  def Const(self, node):
    self.save_s(node, {'value': node.value})

  def Declaration(self, node):
    self.save_s(node, {'name': node.name})
    self.indent()
    node.type.accept(self)
    self.unindent()

  def FnDeclaration(self, node):
    self.save_s(node, {'name': node.name})
    self.indent()
    node.type.accept(self)
    node.parameterGroup.accept(self)
    node.body.accept(self)
    self.unindent()

  def Declarator(self, node):
    self.save_s(node, {'name': node.name})
    self.indent()
    node.type.accept(self)
    self.unindent()

  def FnDeclarator(self, node):
    self.save_s(node, {'name': node.name})
    self.indent()
    node.type.accept(self)
    node.parameterGroup.accept(self)
    self.unindent()

  def ArrayDeclarator(self, node):
    self.save_s(node, {'name': node.name, 'size': node.size})
    self.indent()
    node.type.accept(self)
    self.unindent()

  def ConditionalStatement(self, node):
    self.save_s(node)
    self.indent()
    node.expr.accept(self)
    node.then_section.accept(self)
    node.else_section.accept(self)
    self.unindent()

  def LoopStatement(self, node):
    self.save_s(node)
    self.indent()
    node.expr.accept(self)
    node.section.accept(self)
    self.unindent()

  def For(self, node):
    self.save_s(node)
    self.indent()
    node.init_stmt.accept(self)
    node.expr.accept(self)
    node.term_stmt.accept(self)
    node.section.accept(self)
    self.unindent()

  def Return(self, node):
    self.save_s(node)
    self.indent()
    node.expr.accept(self)
    self.unindent()

  def BinaryOp(self, node):
    self.save_s(node, {'op': node.op})
    self.indent()
    node.left.accept(self)
    node.right.accept(self)
    self.unindent()

  def UnaryOp(self, node):
    self.save_s(node, {'op': node.op})
    self.indent()
    node.expr.accept(self)
    self.unindent()

  def FnExpression(self, node):
    self.save_s(node)
    self.indent()
    node.arguments.accept(self)
    node.expr.accept(self)
    self.unindent()

  def VaExpression(self, node):
    self.save_s(node, {'name': node.name, 'pointer': node.pointer})

  def ArrayExpression(self, node):
    self.save_s(node)
    self.indent()
    node.index.accept(self)
    node.expr.accept(self)
    self.unindent()
