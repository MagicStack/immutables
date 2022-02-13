import time
import operator
import random
from immutables import lbst


MAGIC = 100
TREE_MAX_SIZE = random.randint(MAGIC, MAGIC * 100)
INTEGER_MAX = random.randint(1, MAGIC * 10_000)


def test_balanced_and_sorted_random_trees_of_positive_integers():
    for _ in range(MAGIC):
        # given
        expected = dict()
        tree = lbst.make(operator.lt)
        for i in range(TREE_MAX_SIZE):
            key = value = random.randint(0, INTEGER_MAX)
            tree = lbst.set(tree, key, value)
            expected[key] = value
        # when
        out = tuple(lbst.to_dict(tree).items())
        # then
        assert lbst.is_balanced(tree)
        expected = tuple(sorted(expected.items()))
        assert out == expected


def test_balanced_and_sorted_random_trees_of_integers():
    for _ in range(MAGIC):
        # given
        expected = dict()
        tree = lbst.make(operator.lt)
        for i in range(TREE_MAX_SIZE):
            key = value = random.randint(-INTEGER_MAX, INTEGER_MAX)
            tree = lbst.set(tree, key, value)
            expected[key] = value
        # when
        out = tuple(lbst.to_dict(tree).items())
        # then
        assert lbst.is_balanced(tree)
        expected = tuple(sorted(expected.items()))
        assert out == expected


def test_balanced_and_sorted_random_trees_of_floats():
    for _ in range(MAGIC):
        # given
        expected = dict()
        tree = lbst.make(operator.lt)
        for i in range(TREE_MAX_SIZE):
            key = value = random.uniform(-INTEGER_MAX, INTEGER_MAX)
            tree = lbst.set(tree, key, value)
            expected[key] = value
        # when
        out = tuple(lbst.to_dict(tree).items())
        # then
        assert lbst.is_balanced(tree)
        expected = tuple(sorted(expected.items()))
        assert out == expected


def test_balanced_and_sorted_random_trees_of_positive_floats():
    for _ in range(MAGIC):
        # given
        expected = dict()
        tree = lbst.make(operator.lt)
        for i in range(TREE_MAX_SIZE):
            key = value = random.uniform(0, INTEGER_MAX)
            tree = lbst.set(tree, key, value)
            expected[key] = value
        # when
        out = tuple(lbst.to_dict(tree).items())
        # then
        assert lbst.is_balanced(tree)
        expected = tuple(sorted(expected.items()))
        assert out == expected


def test_faster_than_naive():

    def make_lbst_tree(values):
        out = lbst.make(operator.lt)
        for value in values:
            out = lbst.set(out, value, value)
        return out

    def make_naive(values):
        out = dict()
        for value in values:
            out[value] = value
            out = sorted(out.items())
            out = dict(out)
        return out


    values = [random.randint(-INTEGER_MAX, INTEGER_MAX) for _ in range(TREE_MAX_SIZE)]

    start = time.perf_counter()
    make_lbst_tree(values)
    lsbt_timing = time.perf_counter() - start

    start = time.perf_counter()
    make_naive(values)
    naive_timing = time.perf_counter() - start

    assert lsbt_timing < naive_timing
