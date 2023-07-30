from functools import reduce

get_class = lambda qualified_name: reduce(getattr, qualified_name.split('.')[1:],
                                          __import__(qualified_name.partition('.')[0]))
"""
get class from fully qualified name that can be instantiated. Example:


cls = get_class('my.class')

a = cls() #instantiate a new instance of the class    
b = cls( arg1, arg2 ) # pass arguments to the constructor

dt = get_class('datetime.datetime')
dt_obj = dt()
dt_obj.now()
"""


def get_func_declaring_class(func: callable) -> str:
    """
        retrieve fully qualified name of the declaring class.
        Returns None if not declared in class
    """
    module = func.__module__
    cls = func.__qualname__.rsplit('.', 1)[0]
    if cls == func.__name__: return None  # not declared in class
    if module == 'builtins': module = ''
    return '.'.join([module, cls]).strip('.') if module else None

