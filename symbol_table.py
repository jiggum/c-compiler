class Log:
  def __init__(self, lineno, value=None):
    self.value = value
    self.lineno = lineno

  def __str__(self):
    value_str = 'N/A' if self.value is None else self.value
    return '{} at line {}'.format(value_str, self.lineno)

class History:
  def __init__(self, symbol):
    self.symbol = symbol
    self.history = []

  def add(self, lineno, value):
    self.history.append(Log(lineno, value))

  def get(self):
    return self.history[-1].value

  def trace(self):
    for log in self.history:
      print('{} = {}'.format(self.symbol, log.__str__()))

class SymbolTableEntry:
  def __init__(self, symbol, type):
    self.symbol = symbol
    self.type = type
    self.history = History(symbol)
    self.constant = False
    self.constant_section = None
    self.used = False

  def add_log(self, lineno, value):
    self.history.add(lineno, value)

  def trace(self):
    self.history.trace()

  def get(self):
    return self.history.get()

class SymbolTable:
  def __init__(self, node, inherit_symbol_table=None):
    self.node = node
    self.table = {}
    if (inherit_symbol_table):
      self.table.update(inherit_symbol_table.table)

  def define(self, symbol, type, lineno, value=None):
    self.table[symbol] = SymbolTableEntry(symbol, type)
    self.add(symbol, lineno, value)

  def add(self, symbol, lineno, value):
    self.table[symbol].add_log(lineno, value)

  def has(self, symbol):
    return symbol in self.table

  def get(self, symbol):
    return self.table[symbol].get()

  def trace(self, symbol):
    self.table[symbol].trace()

  def set_constant(self, symbol, constant, constant_section):
    self.table[symbol].constant = constant
    self.table[symbol].constant_section = constant_section

  def is_constant(self, symbol, current_loop_node, check_outer):
    constant = self.table[symbol].constant
    constant_section = self.table[symbol].constant_section
    if check_outer:
      return constant and (constant_section is not current_loop_node)
    return constant and (constant_section is current_loop_node)

  def set_used(self, symbol):
    self.table[symbol].used = True

  def is_used(self, symbol):
    return self.table[symbol].used
