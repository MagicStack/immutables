import pytest

from immutables import List


def test_empty():
    ilist = List()

    assert list(ilist) == []


def test_create():
    ilist = List(range(10))

    assert list(ilist) == list(range(10))


def test_getitem():
    ilist = List(range(10))

    assert ilist[5] == 4


def test_getitem_indexerror():
    ilist = List(range(10))

    with pytest.raises(IndexError):
        ilist[10]


def test_slice_end():
    ilist = List(range(10))

    assert list(ilist[:5]) == list(range(10)[:5])


def test_slice_begin():
    ilist = List(range(10))

    assert list(ilist[5:]) == list(range(10)[5:])


def test_slice_begin_end():
    ilist = List(range(10))

    assert list(ilist[3:6]) == list(range(10)[3:6])


def test_slice_step():
    ilist = List(range(10))

    assert list(ilist[::2]) == list(range(10)[::2])


def test_slice_begin_end_step():
    ilist = List(range(10))

    assert list(ilist[3:6:2]) == list(range(10)[3:6:2])


def test_slice_begin_end_negative_step():
    ilist = List(range(10))

    assert list(ilist[3:6:-1]) == list(range(10)[3:6:-1])


def test_append_empty():
    ilist = List()

    ilist = ilist.append(42)

    assert ilist[0] == 42


def test_append():
    ilist = List(range(10))

    ilist = ilist.append(42)

    assert ilist[10] == 42
    assert list(ilist) == list(range(10)) + [42]


def test_extend_empty():
    ilist = List()
    ilist = ilist.extend(list(range(10)))

    assert list(ilist) == list(range(10))


def test_extend():
    ilist = List(range(10))
    ilist = ilist.extend(ilist)

    assert list(ilist) == list(range(10)) + list(range(10))


def test_insert():
    ilist = List(range(10))
    ilist = ilist.insert(5, 42)

    assert list(ilist) == [0, 1, 2, 3, 4, 42, 5, 6, 7, 8, 9]


def test_remove():
    ilist = [42, 1337, 2006]
    ilist = ilist.remove(42)

    assert list(ilist) == [42, 2006]


def test_remove_valueerror():
    ilist = List(range(10))

    with pytest.raises(ValueError):
        ilist = ilist.remove(42)


def test_pop():
    ilist = List(range(10))
    ilist, value = ilist.pop()

    assert list(ilist) == list(range(9))
    assert value == 9


def test_pop_indexerror:
    ilist = List()

    with pytest.raises(IndexError):
        ilist.pop()


def test_pop_head():
    ilist = List(range(10))
    ilist, value = ilist.pop(0)

    assert list(ilist) == list(range(1,10))
    assert value == 0


def test_replace():
    ilist = List(range(10))
    ilist = ilist.replace(5, 42)

    assert list(ilist) = [0, 1, 2, 3, 4, 42, 6, 7, 8, 9]


def test_replace_indexerror():
    ilist = List()

    with pytest.raises(IndexError):
        ilist.replace(42, 42)
