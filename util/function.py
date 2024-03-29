import sys
from model.ast import TypeNode, EmptyNode
from model.symbol_table import SymbolTable
import codecs

class Function:
  def __init__(self , function, name):
    self.function = function
    self.name = name

  def run(self, *args):
    return self.function(*args)

def printf(format, *args):
  format_ = codecs.escape_decode(format)[0].decode('unicode_escape')
  return sys.stdout.write(format_ % args)

globalFunctionTable = SymbolTable(EmptyNode())
globalFunctionTable.define('printf', TypeNode(), 0, Function(printf, 'printf'))
globalFunctionTable.set_pure_function('printf', False)
