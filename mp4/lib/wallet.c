#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
//#include <sys/_pthread/_pthread_cond_t.h>

#include "wallet.h"

/**
 * Initializes an empty wallet.
 */
void wallet_init(wallet_t *wallet) {
  // Implement
  wallet->head = malloc(sizeof(wallet_resource));
  wallet->head->next = NULL;
  pthread_mutex_init(&wallet->lock, NULL);
  pthread_cond_init(&wallet->cond, NULL);
}

/**
 * Returns the amount of a given `resource` in the given `wallet`.
 */
int wallet_get(wallet_t *wallet, const char *resource) {
  // Implement this
  wallet_resource *cur = wallet->head;
  pthread_mutex_lock(&wallet->lock);
  while (cur->next) {
    if (strcmp(cur->next->resource_name, resource) == 0) {
      // printf("Find %s: %d", cur->next->resource_name, cur->next->amount);
      pthread_mutex_unlock(&wallet->lock);
      return cur->next->amount;
    }
    cur = cur->next;
  }
  // printf("name not found");
  pthread_mutex_unlock(&wallet->lock);
  return 0;
}

/**
 * Modifies the amount of a given `resource` in a given `wallet by `delta`.
 * - If `delta` is negative, this function MUST NOT RETURN until the resource
 * can be satisfied. (Ths function MUST WAIT until the wallet has enough
 * resources to satisfy the request; there are several ways to accomplish this
 * waiting and it does not have to be fancy.)
 */
void wallet_change_resource(wallet_t *wallet, const char *resource,
                            const int delta) {
  // Implement this
  wallet_resource *cur = wallet->head;
  pthread_mutex_lock(&wallet->lock);
  while (cur->next) {
    if (strcmp(cur->next->resource_name, resource) == 0) {
      break;
    }
    cur = cur->next;
  }
  if (cur->next == NULL) {
    // printf("Add %s\n", resource);
    cur->next = malloc(sizeof(wallet_resource));
    cur->next->amount = 0;
    cur->next->resource_name = resource;
    cur->next->next = NULL;
    // printf("Finish add %s\n", resource);
  }
  pthread_mutex_unlock(&wallet->lock);

  if (delta >= 0) {
    pthread_mutex_lock(&wallet->lock);

    cur->next->amount += delta;

    pthread_cond_broadcast(&wallet->cond);
    pthread_mutex_unlock(&wallet->lock);
  } else {
    pthread_mutex_lock(&wallet->lock);
    while (cur->next->amount + delta < 0) {
      pthread_cond_wait(&wallet->cond, &wallet->lock);
    }
    cur->next->amount += delta;

    pthread_cond_broadcast(&wallet->cond);
    pthread_mutex_unlock(&wallet->lock);
  }
}

/**
 * Destroys a wallet, freeing all associated memory.
 */
void wallet_destroy(wallet_t *wallet) {
  // Implement this
  wallet_resource *node = wallet->head;
  while (node) {
    wallet_resource *next = node->next;
    free(node);
    node = next;
  }
  // printf("End destroy");
}