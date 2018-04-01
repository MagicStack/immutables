#ifndef IMMUTABLES_MAP_H
#define IMMUTABLES_MAP_H

#include <stdint.h>
#include "Python.h"

#define _Py_HAMT_MAX_TREE_DEPTH 7


#define Map_Check(o) (Py_TYPE(o) == &_Map_Type)


/* Abstract tree node. */
typedef struct {
    PyObject_HEAD
} MapNode;


/* An HAMT immutable mapping collection. */
typedef struct {
    PyObject_HEAD
    MapNode *h_root;
    PyObject *h_weakreflist;
    Py_ssize_t h_count;
    Py_hash_t h_hash;
} MapObject;


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
    MapObject *hi_obj;
    MapIteratorState hi_iter;
    binaryfunc hi_yield;
} MapIterator;


PyTypeObject _Map_Type;
PyTypeObject _Map_ArrayNode_Type;
PyTypeObject _Map_BitmapNode_Type;
PyTypeObject _Map_CollisionNode_Type;
PyTypeObject _MapKeys_Type;
PyTypeObject _MapValues_Type;
PyTypeObject _MapItems_Type;


#endif
