immutables
==========

.. image:: https://travis-ci.org/MagicStack/immutables.svg?branch=master
    :target: https://travis-ci.org/MagicStack/immutables

.. image:: https://ci.appveyor.com/api/projects/status/tgbc6tq56u63qqhf?svg=true
    :target: https://ci.appveyor.com/project/MagicStack/immutables

.. image:: https://img.shields.io/pypi/v/immutables.svg
    :target: https://pypi.python.org/pypi/immutables
    
.. image:: https://img.shields.io/conda/vn/conda-forge/immutables.svg
    :target: https://anaconda.org/conda-forge/immutables    

An immutable mapping type for Python.

The underlying datastructure is a Hash Array Mapped Trie (HAMT)
used in Clojure, Scala, Haskell, and other functional languages.
This implementation is used in CPython 3.7 in the ``contextvars``
module (see PEP 550 and PEP 567 for more details).

Immutable mappings based on HAMT have O(log N) performance for both
``set()`` and ``get()`` operations, which is essentially O(1) for
relatively small mappings.

Below is a visualization of a simple get/set benchmark comparing
HAMT to an immutable mapping implemented with a Python dict
copy-on-write approach (the benchmark code is available
`here <https://gist.github.com/1st1/292e3f0bbe43bd65ff3256f80aa2637d>`_):

.. image:: bench.png


Installation
------------

``immutables`` requires Python 3.5+ and is available on PyPI::

    $ pip install immutables


API
---

``immutables.Map`` is an unordered immutable mapping.  ``Map`` objects
are hashable, comparable, and pickleable.

The ``Map`` object implements the ``collections.abc.Mapping`` ABC
so working with it is very similar to working with Python dicts:

.. code-block:: python

    import immutables

    map = immutables.Map(a=1, b=2)

    print(map['a'])
    # will print '1'

    print(map.get('z', 100))
    # will print '100'

    print('z' in map)
    # will print 'False'

Since Maps are immutable, there is a special API for mutations that
allow apply changes to the Map object and create new (derived) Maps:

.. code-block:: python

    map2 = map.set('a', 10)
    print(map, map2)
    # will print:
    #   <immutables.Map({'a': 1, 'b': 2})>
    #   <immutables.Map({'a': 10, 'b': 2})>

    map3 = map2.delete('b')
    print(map, map2, map3)
    # will print:
    #   <immutables.Map({'a': 1, 'b': 2})>
    #   <immutables.Map({'a': 10, 'b': 2})>
    #   <immutables.Map({'a': 10})>

Maps also implement APIs for bulk updates: ``MapMutation`` objects:

.. code-block:: python

    map_mutation = map.mutate()
    map_mutation['a'] = 100
    del map_mutation['b']
    map_mutation.set('y', 'y')

    map2 = map_mutation.finish()

    print(map, map2)
    # will print:
    #   <immutables.Map({'a': 1, 'b': 2})>
    #   <immutables.Map({'a': 100, 'y': 'y'})>

``MapMutation`` objects are context managers.  Here's the above example
rewritten in a more idiomatic way:

.. code-block:: python

    with map.mutate() as mm:
        mm['a'] = 100
        del mm['b']
        mm.set('y', 'y')
        map2 = mm.finish()

    print(map, map2)
    # will print:
    #   <immutables.Map({'a': 1, 'b': 2})>
    #   <immutables.Map({'a': 100, 'y': 'y'})>


Further development
-------------------

* An immutable version of Python ``set`` type with efficient
  ``add()`` and ``discard()`` operations.


License
-------

Apache 2.0
