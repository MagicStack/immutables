import timeit

import immutables
import pyimmutable
import pyrsistent


def dict_set(m, k, v):
    m[k] = v
    return m

def update(m, kvs):
    m.update(kvs)
    return m


implementations = (
    (
        'Map',
        immutables.Map,
        immutables.Map.set,
        immutables.Map.update,
    ),
    (
        'PMap',
        pyrsistent.pmap,
        pyrsistent.PMap.set,
        lambda m, items: m.update(dict(items)),  # Does not accept a generator.
    ),
    # Does not work with Pypy3.
    (
        'ImmutableDict',
        pyimmutable.ImmutableDict,
        pyimmutable.ImmutableDict.set,
        pyimmutable.ImmutableDict.update,
    ),
    (
        'dict',
        dict,
        dict_set,
        dict.update,  # Does not return the updated dict!!
    ),
)


# This test does not care about dataset size so it's handled separately.
print('Create empty:')
for iname, map, *_ in implementations:
    timer = timeit.Timer('map()', globals={'map': map})
    loop_count, seconds = timer.autorange()
    print('\t%s:\t%.2g' % (iname, seconds / loop_count))


tests = (
    #("Create empty", "map()", "pass"),

    ("Create", "map((i, i) for i in range(data_size))", "pass"),

    (
        "Random set to",
        "for i in values: m = set(m, i, i)",
        """
m = map((i, i) for i in range(data_size))

values = list(range(data_size)) * (1 if data_size >= 1000 else 1000 // data_size)
import random
random.seed(42)
random.shuffle(values)
values = values[1000:]
        """,
    ),

    (
        "Random update to",
        "update(m, ((i, -i) for i in values))",
        """
m = map((i, i) for i in range(data_size))

values = list(range(data_size)) * (1 if data_size >= 1000 else 1000 // data_size)
import random
random.seed(42)
random.shuffle(values)
values = values[1000:]
        """,
    ),

    (
        "Random read from",
        "update(m, ((i, -i) for i in values))",
        """
m = map((i, i) for i in range(data_size))

values = list(range(data_size)) * (1 if data_size >= 1000 else 1000 // data_size)
import random
random.seed(42)
random.shuffle(values)
values = values[1000:]
        """,
    ),

    (
        "Iterate keys from",
        "for k in m: pass",
        "m = map((i, i) for i in range(data_size))",
    ),

    (
        "Iterate values from",
        "for k in m.values(): pass",
        "m = map((i, i) for i in range(data_size))",
    ),

    (
        "Iterate items from",
        "for k in m.items(): pass",
        "m = map((i, i) for i in range(data_size))",
    ),

)
for test_name, test, test_setup in tests:
    for dname, dsize in (('small', 10), ('medium', 2000), ('large', 1_000_000)):
        print(test_name, dname, ':')

        for iname, map, set, update in implementations:
            timer = timeit.Timer(
                test,
                setup=test_setup,
                globals={
                    'map': map,
                    'set': set,
                    'update': update,
                    'data_name': dname,
                    'data_size': dsize,
                },
            )
            loop_count, seconds = timer.autorange()
            print('\t%s:\t%.2g' % (iname, seconds / loop_count))
