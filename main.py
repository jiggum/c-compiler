import sys
import re
from parser import Parser
from flow_visitor import FlowVisitor
import traceback
from print_visitor import PrintVisitor

DEBUG=True

CLI_NEXT_REGEX = re.compile('^next(?:\s(.+))?$')
CLI_PRINT_REGEX = re.compile('^print(?:\s(.+))?$')
CLI_TRACE_REGEX = re.compile('^trace\s(\w+)$')
LINE_RGEX = re.compile('^\d+$')
VARIABLE_RGEX = re.compile('^[a-zA-Z_$][a-zA-Z_$0-9]*$')

if __name__ == '__main__':
  src_path = sys.argv[1]
  try:
    parser = Parser(debug=DEBUG)
    ast = parser.run(src_path)
    if DEBUG:
      printVisitor = PrintVisitor()
      ast.accept(printVisitor)
      print(printVisitor)
    flowVisitor = FlowVisitor(debug=DEBUG)
    ast.accept(flowVisitor)
    while True:
      input_str = input(str(flowVisitor.linenos) + '>>' if DEBUG else '>>')
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
      else:
        print('Invalid command. use : next / trace / print')
  except:
    if DEBUG:
      exc_info = sys.exc_info()
      traceback.print_exception(*exc_info)
      del exc_info
