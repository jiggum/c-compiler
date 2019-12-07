def getVisitorFunc(visitor, node_class):
  node_name = node_class.__name__
  if (hasattr(visitor, node_name)):
    return getattr(visitor, node_name)
  for base_node in node_class.__bases__:
    if (base_node is not object):
      visitorFunc = getVisitorFunc(visitor, base_node)
      if (visitorFunc != None):
        return visitorFunc
  return None

def props(cls):
  return [i for i in cls.__dict__.keys() if i[:1] != '_']
