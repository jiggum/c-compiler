import sys
import re
import traceback
import argparse
from generator.parser import Parser
from visitor.interpreter_visitor import InterpreterVisitor
from visitor.print_visitor import PrintVisitor

CLI_NEXT_REGEX = re.compile('^next(?:\s(.+))?$')
CLI_PRINT_REGEX = re.compile('^print(?:\s(.+))?$')
CLI_TRACE_REGEX = re.compile('^trace(?:\s(\w+))?$')
CLI_EXIT_REGEX = re.compile('^exit$')
LINE_RGEX = re.compile('^\d+$')
VARIABLE_RGEX = re.compile('^[a-zA-Z_$][a-zA-Z_$0-9]*$')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='AST optimizer')
  parser.add_argument('input', type=str, metavar='Input_File', help='Input .c file path')
  parser.add_argument('--debug', action='store_true')
  args = parser.parse_args()

  sys.setrecursionlimit(2**16)
  try:
    parser = Parser(debug=args.debug)
    ast = parser.run(args.input)
    if args.debug:
      printVisitor = PrintVisitor()
      ast.accept(printVisitor)
      print(printVisitor)
    flowVisitor = InterpreterVisitor(debug=args.debug)
    ast.accept(flowVisitor)
    while True:
      input_str = input(str(flowVisitor.linenos) + '>>' if args.debug else '>>')
      if CLI_NEXT_REGEX.search(input_str):
        m = CLI_NEXT_REGEX.match(input_str)
        lines_str = m.groups()[0]
        if lines_str is not None and LINE_RGEX.search(lines_str) is None:
          print('Incorrect command usage : try ‘next [lines]')
          continue
        lines = 1 if lines_str is None else int(m.groups()[0])
        flowVisitor.add_linenum(lines)
        ast.accept(flowVisitor)
      elif CLI_PRINT_REGEX.search(input_str):
        m = CLI_PRINT_REGEX.match(input_str)
        symbol = m.groups()[0]
        if symbol is None or VARIABLE_RGEX.search(symbol) is None:
          print('Invalid typing of the variable name')
          continue
        flowVisitor.print(symbol)
      elif CLI_TRACE_REGEX.search(input_str):
        m = CLI_TRACE_REGEX.match(input_str)
        symbol = m.groups()[0]
        if symbol is None or VARIABLE_RGEX.search(symbol) is None:
          print('Invalid typing of the variable name')
          continue
        flowVisitor.trace(symbol)
      elif CLI_EXIT_REGEX.search(input_str):
        break
      else:
        print('Invalid command. use : next / next [number] / trace [symbol] / print [symbol] / exit')
  except:
    if args.debug:
      exc_info = sys.exc_info()
      traceback.print_exception(*exc_info)
      del exc_info
