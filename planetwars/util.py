from hashlib import sha256
from logging import getLogger, Handler
from planetwars.compat import namedtuple
from functools import update_wrapper
from collections import defaultdict

log = getLogger(__name__)

class Point(namedtuple("Point", "x y")):
    def __repr__(self):
        return "(%0.2fx%0.2f)" % (self.x, self.y)

class ParsingException(Exception):
    pass

class TimeIsUp(Exception):
    pass

def _make_id(*args):
    return filter(lambda y: y.isdigit(), sha256("".join(map(str, args))).hexdigest()[:16])

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

        old_init = getattr(new_cls, "__init__")
        def new_init(self, iterable_or_item=()):
            if isinstance(iterable_or_item, attrs.get('accepts', ())):
                old_init(self, [iterable_or_item])
                return
            old_init(self, iterable_or_item)
        new_init = update_wrapper(new_init, old_init, assigned=("__name__", "__doc__"), updated=())
        setattr(new_cls, "__init__", new_init)
        return new_cls

class TypedSetBase(set):
    __metaclass__ = TypedSetMeta


class SetDict(defaultdict):
    """A set-oriented defaultdict subclass that allows sets
    as dictionary keys. It (De-)Composes them on the fly.

    e.g:

    >>> a_set = set([1, 2])
    >>>
    >>> sd = SetDict()
    >>> sd[a_set] = 'X'
    >>> sd[1]
    'X'
    >>> sd[2]
    'X'
    >>> sd2 = SetDict()
    >>> sd2[1] = set(['a', 'b'])
    >>> sd2[2] = set(['c', 'd'])
    >>> sd2[a_set]
    set(['a', 'c', 'b', 'd']
    """
    def __init__(self, defaultfactory=set):
        if not issubclass(defaultfactory, set):
            raise TypeError("SetDict can only use set based defaultfactories.")
        super(SetDict, self).__init__(defaultfactory)

    def __getitem__(self, key):
        if isinstance(key, set):
            return reduce(lambda x,y: x | y, (super(SetDict, self).__getitem__(k) for k in key), set())
        return super(SetDict, self).__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, set):
            for k in key:
                super(SetDict, self).__setitem__(k, value)
            return
        super(SetDict, self).__setitem__(key, value)

    def __delitem__(self, key, value):
        if isinstance(key, set):
            for k in key:
                super(SetDict, self).__delitem__(k)
            return
        return super(SetDict, self).__delitem__(key)


class NullHandler(Handler):
    def emit(self, record):
        pass
getLogger("planetwars").addHandler(NullHandler())

