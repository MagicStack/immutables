from collections import namedtuple
from math import log2

#
# Balanced binary tree based on Log-Balanced Search Trees (LBST)
# and slib's wttree
#
# ref: https://scholar.google.fr/scholar?cluster=16806430159882137269
#

LBST = namedtuple('LBST', 'comparator root')

Node = namedtuple('Node', 'key value weight left right')


NODE_NULL = Node(None, None, 0, None, None)


def make(comparator):
    return LBST(comparator, NODE_NULL)


def _node_weight(node):
    if node is None:
        return 0
    else:
        return node.weight


def _is_less(a, b):
    assert isinstance(a, int)
    assert isinstance(b, int)

    # `a` is less than `b`, when the position of the left-most bit set
    # of `a` is less than the position of the left-most bit set of `b`;
    # the left-most bit set position is given by int.bit_length (3.1+)
    return a.bit_length() < b.bit_length()


def _is_too_big(a, b):
    return _is_less(a, b >> 1)


def _node_join(key, value, left, right):
    return Node(key, value, _node_weight(left) + _node_weight(right) + 1, left, right)


def _node_single_left_rotation(key, value, left, right):
    return _node_join(right.key, right.value, _node_join(key, value, left, right.left), right.right)


def _node_double_left_rotation(key, value, left, right):
    return _node_join(
        right.left.key,
        right.left.value,
        _node_join(key, value, left, right.left.left),
        _node_join(right.key, right.value, right.left.right, right.right)
    )


def _node_single_right_rotation(key, value, left, right):
    return _node_join(left.key, left.value, left.left, _node_join(key, value, left.right, right))


def _node_double_right_rotation(key, value, left, right):
    return _node_join(
        left.right.key,
        left.right.value,
        _node_join(left.key, left.value, left.left, left.right.left),
        _node_join(key, value, left.right.right, right)
    )


def _node_rebalance(key, value, left, right):
    if _is_too_big(_node_weight(left), _node_weight(right)):
        # right is too big, does it require one or two rotations?
        if not _is_less(_node_weight(right.right), _node_weight(right.left)):
            return _node_single_left_rotation(key, value, left, right)
        else:
            return _node_double_left_rotation(key, value, left, right)

    if _is_too_big(_node_weight(right), _node_weight(left)):
        # left is too big, does it require one or two rotations?
        if not _is_less(_node_weight(left.left), _node_weight(left.right)):
            return _node_single_right_rotation(key, value, left, right)
        else:
            return _node_double_right_rotation(key, value, left, right)

    # both sides are the same weight, join the two trees with a top
    # level node.
    return Node(key, value, _node_weight(left) + _node_weight(right) + 1, left, right)


def _node_set(node, comparator, key, value):
    if node is NODE_NULL:
        return Node(key, value, 1, NODE_NULL, NODE_NULL)

    if comparator(key, node.key):
        # The given KEY is less that node.key, recurse left side.
        return _node_rebalance(
            node.key,
            node.value,
            _node_set(node.left, comparator, key, value),
            node.right
        )

    if comparator(node.key, key):
        # The given KEY is more than node.key, recurse right side.
        return _node_rebalance(
            node.key,
            node.value,
            node.left,
            _node_set(node.right, comparator, key, value)
        )

    # otherwise, `key` is equal to `node.key`, create a new node with
    # the given `value`.

    return Node(key, value, _node_weight(node.left) + _node_weight(node.right) + 1, node.left, node.right)


def set(lbst, key, value):
    if lbst.root is NODE_NULL:
        return LBST(lbst.comparator, Node(key, value, 1, NODE_NULL, NODE_NULL))

    return LBST(lbst.comparator, _node_set(lbst.root, lbst.comparator, key, value))


def _node_to_dict(node, out):
    if node.left is not NODE_NULL:
        _node_to_dict(node.left, out)

    out[node.key] = node.value

    if node.right is not NODE_NULL:
        _node_to_dict(node.right, out)


def to_dict(lbst):
    # The created dict is sorted according to `lbst.comparator`.
    out = dict()
    _node_to_dict(lbst.root, out)
    return out


def _node_is_balanced(node):
    if node is NODE_NULL:
        return True

    out = (
        not _is_too_big(_node_weight(node.left), _node_weight(node.right))
        and not _is_too_big(_node_weight(node.right), _node_weight(node.left))
        and _node_is_balanced(node.right)
        and _node_is_balanced(node.left)
    )

    return out


def is_balanced(lbst):
    return _node_is_balanced(lbst.root)
