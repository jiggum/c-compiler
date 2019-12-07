import sys
import re
from parser import Parser
from write_visitor import WriteVisitor

DEBUG=True

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
  printVisitor = WriteVisitor()
  s = ast.accept(printVisitor)
  f = open(target_path, 'w')
  f.write(s)
  f.close()
