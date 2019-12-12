def type_cast(type, value):
  last_type = type.get_type()
  types = type.types
  if last_type == 'int':
    return int(value)
  elif last_type == 'float':
    return float(value)
  elif last_type == 'char':
    return str(value)
  elif last_type == '*':
    if len(types) > 2 and types[1] == 'char':
      return str(value)
    else:
      return value
  else:
    raise ValueError
