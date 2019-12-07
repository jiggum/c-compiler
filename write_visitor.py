class WriteVisitor:
  def __init__(self):
    self.s = ''
    self._indent = 0

  def __str__(self):
    return self.s

  def indent(self):
    self._indent += 1

  def unindent(self):
    self._indent -= 1

  def get_indent_str(self):
    return '  ' * self._indent

  def Node(self, node):
    raise ValueError

  def ArrayNode(self, node):
    raise ValueError

  def EmptyNode(self, node):
    return ''

  def TypeNode(self, node):
    return node.types[-1]

  def Const(self, node):
    return str(node.value)

  def BaseSection(self, node):
    s = ''
    self.indent()
    for child in node.childs:
      s += '{}{}{}\n'.format(self.get_indent_str(), child.accept(self), ';' if child.need_semi() else '')
    self.unindent()
    return s

  def RootSection(self, node):
    s = ''
    for child in node.childs:
      s += '{}{}\n'.format(self.get_indent_str(), child.accept(self))
    return s

  def Declaration(self, node):
    raise ValueError

  def FnDeclaration(self, node):
    parameter_str = 'void' if node.parameterGroup.is_empty() else node.parameterGroup.accept(self)
    s = '{}{} {}({})\n'.format(self.get_indent_str(), node.type.accept(self), node.name, parameter_str)
    s += '{}{{\n'.format(self.get_indent_str())
    s += node.body.accept(self)
    s += '{}}}'.format(self.get_indent_str())
    return s

  def VaDeclarationList(self, node):
    variable_list = map(lambda n: n.accept(self), node.childs)
    variable_list_str = ', '.join(variable_list)
    s = '{} {}'.format(node.childs[0].type.accept(self), variable_list_str)
    return s

  def Declarator(self, node):
    return '{}{}'.format(''.join(node.type.types[:-1]), node.name)

  def FnDeclarator(self, node):
    raise ValueError

  # def VaDeclarator(self, node):

  def ArrayDeclarator(self, node):
    return '{}[{}]'.format(node.name, node.size)

  def ParameterGroup(self, node):
    paramemter_list = map(lambda n: '{} {}'.format(n.type.accept(self), n.accept(self)), node.childs)
    return ', '.join(paramemter_list)

  def ConditionalStatement(self, node):
    s = 'if ({})\n'.format(node.expr.accept(self))
    s += '{}{{\n'.format(self.get_indent_str())
    s += node.then_section.accept(self)
    s += '{}}}'.format(self.get_indent_str())

    if not node.else_section.is_empty():
      s += '\n{}else\n'.format(self.get_indent_str(), node.expr.accept(self))
      s += '{}{{\n'.format(self.get_indent_str())
      s += node.else_section.accept(self)
      s += '{}}}'.format(self.get_indent_str())

    return s

  def LoopStatement(self, node):
    raise ValueError

  def While(self, node):
    s = 'while({})\n'.format(node.expr.accept(self))
    s += '{}{{\n'.format(self.get_indent_str())
    s += node.section.accept(self)
    s += '{}}}'.format(self.get_indent_str())
    return s

  def For(self, node):
    s = 'for({}; {}; {})\n'.format(node.init_stmt.accept(self), node.expr.accept(self), node.term_stmt.accept(self))
    s += '{}{{\n'.format(self.get_indent_str())
    s += node.section.accept(self)
    s += '{}}}'.format(self.get_indent_str())
    return s

  def JumpStatement(self, node):
    raise ValueError

  def Return(self, node):
    if node.expr.is_empty():
      return 'return'
    return 'return {}'.format(node.expr.accept(self))

  def Break(self, node):
    return 'break'

  def Continue(self, node):
    return 'continue'

  def ArgumentList(self, node):
    argument_list = map(lambda n: n.accept(self), node.childs)
    return ', '.join(argument_list)

  def BinaryOp(self, node):
    if node.op == '++':
      return '{}++'.format(node.left.accept(self))
    elif node.op == '--':
      return '{}--'.format(node.left.accept(self))
    if node.use_paren:
      return '({} {} {})'.format(node.left.accept(self), node.op, node.right.accept(self))
    return '{} {} {}'.format(node.left.accept(self), node.op, node.right.accept(self))

  # def AssignOp(self, node):

  def UnaryOp(self, node):
    return '{}{}'.format(node.op, node.expr.accept(self))

  def FnExpression(self, node):
    return '{}({})'.format(node.expr.accept(self), node.arguments.accept(self))

  def VaExpression(self, node):
    if node.pointer is not None:
      return '*{}'.format(node.name)
    return node.name

  def ArrayExpression(self, node):
    return '{}[{}]'.format(node.expr.accept(self), node.index.accept(self))
