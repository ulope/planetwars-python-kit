from zlib import adler32
from logging import getLogger, Handler
from planetwars.compat import namedtuple
from functools import update_wrapper

log = getLogger(__name__)

Point = namedtuple("Point", "x y")

class ParsingException(Exception):
    pass

class TimeIsUp(Exception):
    pass

def _make_id(*args):
    return adler32("".join(map(str, args)))

#noinspection PyUnusedLocal
def timeout_handler(signal, frame):
    log.warning("Timeout reached!")
    raise TimeIsUp

class TypedSetMeta(type):
    methods = (
        '__ror__', 'difference_update', '__isub__', 'symmetric_difference',
        '__rsub__', '__and__', '__rand__', 'intersection', 'difference',
        '__iand__', 'union', '__ixor__', 'symmetric_difference_update',
        '__or__', 'copy', '__rxor__', 'intersection_update', '__xor__',
        '__ior__', '__sub__',
    )

    def __new__(cls, name, bases, attrs):
        new_cls = super(TypedSetMeta, cls).__new__(cls, name, bases, attrs)
        def wrapper(method_name):
            def inner(self, other):
                if isinstance(other, attrs.get('accepts', ())):
                    other = new_cls([other])
                return new_cls(getattr(super(new_cls, self), method_name)(other))
            return update_wrapper(inner, getattr(new_cls, method_name), assigned=("__name__", "__doc__"), updated=())
        for method_name in cls.methods:
            setattr(new_cls, method_name, wrapper(method_name))
        return new_cls

class TypedSetBase(set):
    __metaclass__ = TypedSetMeta

class NullHandler(Handler):
    def emit(self, record):
        pass
getLogger("planetwars").addHandler(NullHandler())

