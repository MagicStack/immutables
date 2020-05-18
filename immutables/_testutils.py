class HashKey:
    _crasher = None

    def __init__(self, hash, name, *, error_on_eq_to=None):
        assert hash != -1
        self.name = name
        self.hash = hash
        self.error_on_eq_to = error_on_eq_to

    def __repr__(self):
        if self._crasher is not None and self._crasher.error_on_repr:
            raise ReprError
        return '<Key name:{} hash:{}>'.format(self.name, self.hash)

    def __hash__(self):
        if self._crasher is not None and self._crasher.error_on_hash:
            raise HashingError

        return self.hash

    def __eq__(self, other):
        if not isinstance(other, HashKey):
            return NotImplemented

        if self._crasher is not None and self._crasher.error_on_eq:
            raise EqError

        if self.error_on_eq_to is not None and self.error_on_eq_to is other:
            raise ValueError('cannot compare {!r} to {!r}'.format(self, other))
        if other.error_on_eq_to is not None and other.error_on_eq_to is self:
            raise ValueError('cannot compare {!r} to {!r}'.format(other, self))

        return (self.name, self.hash) == (other.name, other.hash)


class KeyStr(str):

    def __hash__(self):
        if HashKey._crasher is not None and HashKey._crasher.error_on_hash:
            raise HashingError
        return super().__hash__()

    def __eq__(self, other):
        if HashKey._crasher is not None and HashKey._crasher.error_on_eq:
            raise EqError
        return super().__eq__(other)

    def __repr__(self, other):
        if HashKey._crasher is not None and HashKey._crasher.error_on_repr:
            raise ReprError
        return super().__eq__(other)


class HashKeyCrasher:

    def __init__(self, *, error_on_hash=False, error_on_eq=False,
                 error_on_repr=False):
        self.error_on_hash = error_on_hash
        self.error_on_eq = error_on_eq
        self.error_on_repr = error_on_repr

    def __enter__(self):
        if HashKey._crasher is not None:
            raise RuntimeError('cannot nest crashers')
        HashKey._crasher = self

    def __exit__(self, *exc):
        HashKey._crasher = None


class HashingError(Exception):
    pass


class EqError(Exception):
    pass


class ReprError(Exception):
    pass
