#ifndef IMMUTABLES_MAP_H
#define IMMUTABLES_MAP_H

#include <stdint.h>
#include "Python.h"

#define _Py_HAMT_MAX_TREE_DEPTH 8


#define Map_Check(o) (Py_TYPE(o) == &_Map_Type)
#define MapMutation_Check(o) (Py_TYPE(o) == &_MapMutation_Type)


/* Abstract tree node. */
typedef struct {
    PyObject_HEAD
} MapNode;


#define _MapCommonFields(pref)          \
    PyObject_HEAD                       \
    MapNode *pref##_root;               \
    PyObject *pref##_weakreflist;       \
    Py_ssize_t pref##_count;


/* Base mapping struct; used in methods shared between
   MapObject and MapMutationObject types. */
typedef struct {
    _MapCommonFields(b)
} BaseMapObject;


/* An HAMT immutable mapping collection. */
typedef struct {
    _MapCommonFields(h)
    Py_hash_t h_hash;
} MapObject;


/* MapMutation object (returned from `map.mutate()`.) */
typedef struct {
    _MapCommonFields(m)
    uint64_t m_mutid;
} MapMutationObject;


/* A struct to hold the state of depth-first traverse of the tree.

   HAMT is an immutable collection.  Iterators will hold a strong reference
   to it, and every node in the HAMT has strong references to its children.

   So for iterators, we can implement zero allocations and zero reference
   inc/dec depth-first iteration.

   - i_nodes: an array of seven pointers to tree nodes
   - i_level: the current node in i_nodes
   - i_pos: an array of positions within nodes in i_nodes.
*/
typedef struct {
    MapNode *i_nodes[_Py_HAMT_MAX_TREE_DEPTH];
    Py_ssize_t i_pos[_Py_HAMT_MAX_TREE_DEPTH];
    int8_t i_level;
} MapIteratorState;


/* Base iterator object.

   Contains the iteration state, a pointer to the HAMT tree,
   and a pointer to the 'yield function'.  The latter is a simple
   function that returns a key/value tuple for the 'Items' iterator,
   just a key for the 'Keys' iterator, and a value for the 'Values'
   iterator.
*/

typedef struct {
    PyObject_HEAD
    MapObject *mv_obj;
    binaryfunc mv_yield;
    PyTypeObject *mv_itertype;
} MapView;

typedef struct {
    PyObject_HEAD
    MapObject *mi_obj;
    binaryfunc mi_yield;
    MapIteratorState mi_iter;
} MapIterator;


/* PyTypes */


PyTypeObject _Map_Type;
PyTypeObject _MapMutation_Type;
PyTypeObject _Map_ArrayNode_Type;
PyTypeObject _Map_BitmapNode_Type;
PyTypeObject _Map_CollisionNode_Type;
PyTypeObject _MapKeys_Type;
PyTypeObject _MapValues_Type;
PyTypeObject _MapItems_Type;
PyTypeObject _MapKeysIter_Type;
PyTypeObject _MapValuesIter_Type;
PyTypeObject _MapItemsIter_Type;


#endif
