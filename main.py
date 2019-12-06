import sys
import re
from parser import Parser
from flow_visitor import FlowVisitor
import traceback
from print_visitor import PrintVisitor

DEBUG=True

CLI_NEXT_REGEX = re.compile('^next(?: (\d+))?$')
CLI_PRINT_REGEX = re.compile('^print (\w+)$')
CLI_TRACE_REGEX = re.compile('^trace (\w+)$')

if __name__ == '__main__':
    src_path = sys.argv[1]
    try:
      parser = Parser(debug=DEBUG)
      ast = parser.run(src_path)
      # printVisitor = PrintVisitor()
      # ast.accept(printVisitor)
      # print(printVisitor)
      flowVisitor = FlowVisitor(debug=DEBUG)
      ast.accept(flowVisitor)
      while True:
        input_str = input('>>')
        if CLI_NEXT_REGEX.search(input_str):
          m = CLI_NEXT_REGEX.match(input_str)
          lines_str = m.groups()[0]
          lines = 1 if lines_str is None else int(m.groups()[0])
          flowVisitor.add_linenum(lines)
          ast.accept(flowVisitor)
        elif CLI_PRINT_REGEX.search(input_str):
          m = CLI_PRINT_REGEX.match(input_str)
          symbol = m.groups()[0]
          flowVisitor.print(symbol)
        elif CLI_TRACE_REGEX.search(input_str):
          m = CLI_TRACE_REGEX.match(input_str)
          symbol = m.groups()[0]
          flowVisitor.trace(symbol)
    except:
      if DEBUG:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        del exc_info
