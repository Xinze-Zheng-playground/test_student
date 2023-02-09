/**
 * Malloc
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

typedef struct _metadata_t {
  unsigned int size;    // The size of the memory block.
  unsigned char isUsed; // 0 if the block is free; 1 if the block is used.
  struct _metadata_t *nextFree;
} metadata_t;

/**
 * Allocate space for array in memory
 *
 * Allocates a block of memory for an array of num elements, each of them size
 * bytes long, and initializes all its bits to zero. The effective result is
 * the allocation of an zero-initialized memory block of (num * size) bytes.
 *
 * @param num
 *    Number of elements to be allocated.
 * @param size
 *    Size of elements.
 *
 * @return
 *    A pointer to the memory block allocated by the function.
 *
 *    The type of this pointer is always void*, which can be cast to the
 *    desired type of data pointer in order to be dereferenceable.
 *
 *    If the function failed to allocate the requested block of memory, a
 *    NULL pointer is returned.
 *
 * @see http://www.cplusplus.com/reference/clibrary/cstdlib/calloc/
 */
void *calloc(size_t num, size_t size) {
  void *t = malloc(num * size);
  memset(t, 0, num * size);
  return t;
}

/**
 * Allocate memory block
 *
 * Allocates a block of size bytes of memory, returning a pointer to the
 * beginning of the block.  The content of the newly allocated block of
 * memory is not initialized, remaining with indeterminate values.
 *
 * @param size
 *    Size of the memory block, in bytes.
 *
 * @return
 *    On success, a pointer to the memory block allocated by the function.
 *
 *    The type of this pointer is always void*, which can be cast to the
 *    desired type of data pointer in order to be dereferenceable.
 *
 *    If the function failed to allocate the requested block of memory,
 *    a null pointer is returned.
 *
 * @see http://www.cplusplus.com/reference/clibrary/cstdlib/malloc/
 */
void *startOfHeap = NULL;
metadata_t startOfEmpty = {-1, -1, NULL};
metadata_t *endOfHeap = NULL;
void *malloc(size_t size) {
  if (size <= 0)
    return NULL;
  // printf("malloc: %d\n", size);
  if (startOfHeap == NULL) {
    metadata_t *meta = sbrk(sizeof(metadata_t));
    meta->isUsed = 1;
    meta->size = size;
    meta->nextFree = NULL;
    startOfHeap = meta;
    endOfHeap = meta;
    return sbrk(size);
  }
  metadata_t *ptr = &startOfEmpty;
  while (ptr->nextFree) {
    // printf("Loop malloc\n");
    //  There are sufficient space to reuse.
    if (size <= ptr->nextFree->size) {
      // printf("here\n");
      if (ptr->nextFree->size == size) {
        // printf("A perfect fit\n");
        ptr->nextFree->isUsed = 1;
        void *res = (void *)(ptr->nextFree) + sizeof(metadata_t);
        metadata_t *temp = ptr->nextFree;
        ptr->nextFree = temp->nextFree;
        temp->nextFree = NULL;
        return res;
      } else if (ptr->nextFree->size - sizeof(metadata_t) > size) {
        // printf("Enter split: try to fit %d into %d\n", size,
        //  ptr->nextFree->size);
        // Splitable
        unsigned int orignalSize = ptr->nextFree->size;
        ptr->nextFree->isUsed = 1;
        ptr->nextFree->size = size;
        // printf("Enter split-1\n");
        void *res = (void *)(ptr->nextFree) + sizeof(metadata_t);
        metadata_t *newMeta = res + size;
        // printf("Enter split-2 \n");
        newMeta->isUsed = 0;
        // printf("Enter split-3\n");
        //  Careful on this line
        newMeta->size = orignalSize - size - sizeof(metadata_t);

        newMeta->nextFree = ptr->nextFree->nextFree;
        ptr->nextFree->nextFree = NULL;
        ptr->nextFree = newMeta;
        // printf("split done with %d space remain, original size%d\n",
        //  newMeta->size, orignalSize);
        // printf("New space at %p original space%p\n", newMeta, res +
        // size);
        return res;
      } else {
        // printf("Oversize\n");
        ptr->nextFree->isUsed = 1;
        void *res = ptr->nextFree + sizeof(metadata_t);
        ptr->nextFree = ptr->nextFree->nextFree;
        return res;
      }
    }
    ptr = ptr->nextFree;
  }
  // Need new space;
  metadata_t *meta = sbrk(sizeof(metadata_t));
  if (sbrk(0) == meta)
    return NULL;
  meta->isUsed = 1;
  meta->size = size;
  meta->nextFree = NULL;
  endOfHeap = meta;
  // printf("Add new space of: %d\n", size);
  void *res = sbrk(size);
  if (sbrk(0) == meta)
    return NULL;
  return res;
}

/**
 * Deallocate space in memory
 *
 * A block of memory previously allocated using a call to malloc(),
 * calloc() or realloc() is deallocated, making it available again for
 * further allocations.
 *
 * Notice that this function leaves the value of ptr unchanged, hence
 * it still points to the same (now invalid) location, and not to the
 * null pointer.
 *
 * @param ptr
 *    Pointer to a memory block previously allocated with malloc(),
 *    calloc() or realloc() to be deallocated.  If a null pointer is
 *    passed as argument, no action occurs.
 */
void free(void *ptr) {
  if (ptr == NULL)
    return;
  // printf("Start free memory\n");
  metadata_t *meta = ptr - sizeof(metadata_t);
  // printf("size: %d\n", meta->size);
  meta->isUsed = 0;
  metadata_t *p = &startOfEmpty;
  while (p->nextFree) {
    // printf("%p and %p\n", p->nextFree, meta);
    if (p->nextFree > meta) {
      meta->nextFree = p->nextFree;
      p->nextFree = meta;
      if (p->size != -1) {
        // printf("Enter merge phase\n");
        if (((void *)p) + sizeof(metadata_t) + (p->size) == meta) {
          // merge p and meta
          p->size = p->size + sizeof(metadata_t) + meta->size;
          p->nextFree = meta->nextFree;
          if (((void *)p) + sizeof(metadata_t) + (p->size) == p->nextFree) {
            // merge p and meta->nextFree
            p->size += sizeof(metadata_t) + p->nextFree->size;
            p->nextFree = p->nextFree->nextFree;
          }
          // printf("merge happen\n");
          return;
        }
      }
      // printf("transition\n");
      if (meta->nextFree != NULL &&
          ((void *)meta) + sizeof(metadata_t) + (meta->size) ==
              meta->nextFree) {
        // printf("Enter merge next\n");
        //  merge meta and its next
        metadata_t *nextMeta =
            (metadata_t *)(((void *)meta) + sizeof(metadata_t) + (meta->size));
        meta->size = meta->size + sizeof(metadata_t) + nextMeta->size;
        meta->nextFree = nextMeta->nextFree;
        // printf("merge happen2\n");
        return;
      }
      // printf("middle insertion\n");
      // printf("-------------Check free list -----------------\n");
      // while (p->nextFree) {
      //   printf("A free space at %p with size %d\n", p->nextFree,
      //          p->nextFree->size);
      //   p = p->nextFree;
      // }
      // printf("-------------END -----------------\n");
      return;
    }
    p = p->nextFree;
  }
  p->nextFree = meta;
  if (((void *)p) + sizeof(metadata_t) + (p->size) == meta) {
    // merge p and meta
    p->size = p->size + sizeof(metadata_t) + meta->size;
    p->nextFree = meta->nextFree;
    if (((void *)p) + sizeof(metadata_t) + (p->size) == p->nextFree) {
      // merge p and meta->nextFree
      p->size += sizeof(metadata_t) + p->nextFree->size;
      p->nextFree = p->nextFree->nextFree;
    }
    // printf("merge happen\n");
  }

  // p = &startOfEmpty;
  // printf("-------------Check free list -----------------\n");
  // while (p->nextFree) {
  //   printf("A free space at %p with size %d\n", p->nextFree,
  //   p->nextFree->size); p = p->nextFree;
  // }
  // printf("-------------END -----------------\n");

  meta->nextFree = NULL;
  // printf("%d freed\n", meta->size);
}

/**
 * Reallocate memory block
 *
 * The size of the memory block pointed to by the ptr parameter is changed
 * to the size bytes, expanding or reducing the amount of memory available
 * in the block.
 *
 * The function may move the memory block to a new location, in which case
 * the new location is returned. The content of the memory block is preserved
 * up to the lesser of the new and old sizes, even if the block is moved. If
 * the new size is larger, the value of the newly allocated portion is
 * indeterminate.
 *
 * In case that ptr is NULL, the function behaves exactly as malloc, assigning
 * a new block of size bytes and returning a pointer to the beginning of it.
 *
 * In case that the size is 0, the memory previously allocated in ptr is
 * deallocated as if a call to free was made, and a NULL pointer is returned.
 *
 * @param ptr
 *    Pointer to a memory block previously allocated with malloc(), calloc()
 *    or realloc() to be reallocated.
 *
 *    If this is NULL, a new block is allocated and a pointer to it is
 *    returned by the function.
 *
 * @param size
 *    New size for the memory block, in bytes.
 *
 *    If it is 0 and ptr points to an existing block of memory, the memory
 *    block pointed by ptr is deallocated and a NULL pointer is returned.
 *
 * @return
 *    A pointer to the reallocated memory block, which may be either the
 *    same as the ptr argument or a new location.
 *
 *    The type of this pointer is void*, which can be cast to the desired
 *    type of data pointer in order to be dereferenceable.
 *
 *    If the function failed to allocate the requested block of memory,
 *    a NULL pointer is returned, and the memory block pointed to by
 *    argument ptr is left unchanged.
 *
 * @see http://www.cplusplus.com/reference/clibrary/cstdlib/realloc/
 */
void *realloc(void *ptr, size_t size) {
  if (ptr == NULL)
    return malloc(size);
  // implement realloc:
  if (size == 0) {
    free(ptr);
    return NULL;
  }

  metadata_t *meta = ptr - sizeof(metadata_t);
  int oldSize = meta->size;
  // printf("oldsize: %d\n", meta->size);
  free(ptr);
  metadata_t *p = &startOfEmpty;
  // printf("-------------Check free list -----------------\n");
  // while (p->nextFree) {
  //   printf("A free space at %p with size %d\n", p->nextFree,
  //   p->nextFree->size); p = p->nextFree;
  // }
  // printf("-------------END -----------------\n");
  void *res = malloc(size);
  // printf("Old: %p; new: %p\n", ptr, res);
  if (oldSize > size)
    memcpy(res, ptr, size);
  else
    memcpy(res, ptr, oldSize);
  return res;
}
