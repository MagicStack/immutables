immutables
==========

.. image:: https://travis-ci.org/MagicStack/immutables.svg?branch=master
    :target: https://travis-ci.org/MagicStack/immutables

.. image:: https://ci.appveyor.com/api/projects/status/tgbc6tq56u63qqhf?svg=true
    :target: https://ci.appveyor.com/project/MagicStack/immutables

An immutable mapping type for Python.

The underlying datastructure is a Hash Array Mapped Trie (HAMT)
used in Clojure, Scala, Haskell, and other functional languages.
This implementation is used in CPython 3.7 in the ``contextvars``
module (see PEP 550 and PEP 567 for more details).

Immutable mappings based on HAMT have O(log\ :sub:`32`\ N)
performance for both ``set()`` and ``get()`` operations, which is
essentially O(1) for relatively small mappings.

Below is a visualization of a simple get/set benchmark comparing
HAMT to an immutable mapping implemented with a Python dict
copy-on-write approach (the benchmark code is available
`here <https://gist.github.com/1st1/9004813d5576c96529527d44c5457dcd>`_):

.. image:: bench.png


Installation
------------

``immutables`` requires Python 3.5+ and is available on PyPI::

    $ pip install immutables


immutables.Map
--------------

The ``Map`` object implements ``collections.abc.Mapping`` ABC
so working with it is very similar to working with Python dicts.

The only exception is its ``Map.set()`` and ``Map.delete()`` methods
which return a new instance of ``Map``:

.. code-block:: python

    m1 = Map()  # an empty Map
    m2 = m1.set('key1', 'val1')  # m2 has a 'key1' key, m1 is still empty

    m3 = m2.set('key2', 'val2')
    m3 = m3.delete('key1')  # m3 has only a 'key2' key


Further development
-------------------

* An immutable version of Python ``set`` type with efficient
  ``add()`` and ``discard()`` operations.

* Add support for efficient ``Map.update()`` operation, allow to
  pass a set of key/values to ``Map()``, and add support for
  pickling.


License
-------

Apache 2.0
