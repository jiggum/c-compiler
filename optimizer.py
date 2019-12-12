import re
import argparse
from parser import Parser
from write_visitor import WriteVisitor
from constant_folding_visitor import ConstantFoldingVisitor
from print_visitor import PrintVisitor

CLI_NEXT_REGEX = re.compile('^next(?:\s(.+))?$')
CLI_PRINT_REGEX = re.compile('^print(?:\s(.+))?$')
CLI_TRACE_REGEX = re.compile('^trace\s(\w+)$')
LINE_RGEX = re.compile('^\d+$')
VARIABLE_RGEX = re.compile('^[a-zA-Z_$][a-zA-Z_$0-9]*$')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='AST optimizer')
  parser.add_argument('input', type=str, metavar='Input File', help='Input .c file path')
  parser.add_argument('output', type=str, metavar='Output File', help='Output .c file path')
  parser.add_argument('--debug', action='store_true')
  args = parser.parse_args()

  src_path = args.input
  target_path = args.output
  parser = Parser(debug=args.debug)
  ast = parser.run(src_path)
  if args.debug:
    printVisitor = PrintVisitor()
    ast.accept(printVisitor)
    print(printVisitor)
  constantFoldingVisitor = ConstantFoldingVisitor(debug=args.debug, mark_used=True)
  ast.accept(constantFoldingVisitor)
  ast.accept(constantFoldingVisitor)
  writeVisitor = WriteVisitor(dead_code_elimination=True)
  s = ast.accept(writeVisitor)
  f = open(target_path, 'w')
  f.write(s)
  f.close()
