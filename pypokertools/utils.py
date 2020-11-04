from collections import defaultdict

class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result


class NumericDict(defaultdict):
    """
    allows addiction, substraction, multiplication and divizion beetwen NumericDicts ind scalars
    """
    @classmethod
    def _NewDict(cls):
        return cls()

    def __add__(self, other):
        res = other.copy()
        for k, v in self.items():
            res[k] = v + other[k]
        return res

    def __sub__(self, other):
        res = self.copy()
        if isinstance(other, (int, float)):
            for k, v in self.items():
                res[k] = self[k] - other
        elif isinstance(other, self.__class__):
            for k, v in other.items():
                res[k] = self[k] - v
        else:
            raise TypeError('Invalid operand type')
        return res

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            res = self._NewDict()
            for k, v in self.items():
                res[k] = v * other
        elif isinstance(other, self.__class__):
            res = self._NewDict()
            keys = set(self.keys()) & set(other.keys())
            for k in keys:
                res[k] = self[k] * other[k]
        else:
            raise TypeError('Invalid operand type')
        return res

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            res = self._NewDict()
            for k, v in self.items():
                res[k] = v / other
            return res
        raise TypeError('Invalid operand type: expected int or float')

    def __repr__(self):

        res = '{'
        for k, v in self.items():
            res = res + f'{k}: {v}, '

        res = self.__class__.__name__ + '(' + res + '})'
        return res

    def __str__(self):
        res = '{'
        for k, v in self.items():
            res = res + f'{k}: {v}, '

        res = res + '}'
        return res
