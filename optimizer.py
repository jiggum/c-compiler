import sys
import re
from parser import Parser
from write_visitor import WriteVisitor
from constant_folding_visitor import ConstantFoldingVisitor
# from print_visitor import PrintVisitor

DEBUG=False

CLI_NEXT_REGEX = re.compile('^next(?:\s(.+))?$')
CLI_PRINT_REGEX = re.compile('^print(?:\s(.+))?$')
CLI_TRACE_REGEX = re.compile('^trace\s(\w+)$')
LINE_RGEX = re.compile('^\d+$')
VARIABLE_RGEX = re.compile('^[a-zA-Z_$][a-zA-Z_$0-9]*$')

if __name__ == '__main__':
  src_path = sys.argv[1]
  target_path = sys.argv[2]
  parser = Parser(debug=DEBUG)
  ast = parser.run(src_path)
  constantFoldingVisitor = ConstantFoldingVisitor(debug=DEBUG, mark_used=True)
  ast.accept(constantFoldingVisitor)
  ast.accept(constantFoldingVisitor)
  # printVisitor = PrintVisitor()
  # ast.accept(printVisitor)
  # print(printVisitor)
  writeVisitor = WriteVisitor(dead_code_elimination=True)
  s = ast.accept(writeVisitor)
  f = open(target_path, 'w')
  f.write(s)
  f.close()
