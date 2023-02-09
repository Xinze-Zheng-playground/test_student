#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "http.h"

/**
 * httprequest_parse_headers
 *
 * Populate a `req` with the contents of `buffer`, returning the number of bytes
 * used from `buf`.
 */
ssize_t httprequest_parse_headers(HTTPRequest *req, char *buffer,
                                  ssize_t buffer_len) {
  // printf("%d", __LINE__);
  // printf("%s\n", buffer);
  // req->head = (link_list*)calloc(sizeof(link_list),1);   // init link list
  req->head = NULL;
  req->payload = NULL;

  char *tmp;
  char *each_line;
  char *sub_line;
  char *subtmp;
  // first line
  each_line = strtok_r(buffer, "\r\n", &tmp);
  // action
  sub_line = strtok_r(each_line, " ", &subtmp);
  req->action = (char *)calloc(strlen(sub_line) + 1, 1);
  strcpy(req->action, sub_line);
  // path
  sub_line = strtok_r(NULL, " ", &subtmp);
  req->path = (char *)calloc(strlen(sub_line) + 1, 1);
  strcpy(req->path, sub_line);
  // version
  sub_line = strtok_r(NULL, "\r\n", &subtmp);
  req->version = (char *)calloc(strlen(sub_line) + 1, 1);
  strcpy(req->version, sub_line);
  // header
  char *valtmp;
  link_list *current;

  while (*(tmp + 1) != '\r' || *(tmp + 2) != '\n') {
    each_line = strtok_r(NULL, "\r\n", &tmp);
    link_list *node = (link_list *)calloc(1, sizeof(link_list));
    node->key = strdup(strtok_r(each_line, ":", &valtmp));
    node->value = strdup(valtmp + 1);
    if (req->head == NULL) {
      req->head = node;
      node->next = NULL;
      current = node;
    } else {
      current->next = node;
      node->next = NULL;
      current = node;
    }
  }
  link_list *temp = req->head;
  // printf("my link list\n");
  while (temp != NULL) {
    // printf("key: %s\n", temp->key);
    // printf("value: %s\n", temp->value);
    temp = temp->next;
  }
  // printf("my link list end\n");
  if (httprequest_get_header(req, "Content-Length") != NULL) {
    int len_payload = atoi(httprequest_get_header(req, "Content-Length"));
    req->payload = calloc(len_payload, 1);
    // printf("hello\n");
    memcpy(req->payload, tmp + 3, len_payload);
  }
  return -1;
}

/**
 * httprequest_read
 *
 * Populate a `req` from the socket `sockfd`, returning the number of bytes read
 * to populate `req`.
 */
ssize_t httprequest_read(HTTPRequest *req, int sockfd) {
  char buffer[5000];
  ssize_t length = read(sockfd, buffer, 5000);
  httprequest_parse_headers(req, buffer, length);
  return length;
}

/**
 * httprequest_get_action
 *
 * Returns the HTTP action verb for a given `req`.
 */
const char *httprequest_get_action(HTTPRequest *req) { return req->action; }

/**
 * httprequest_get_header
 *
 * Returns the value of the HTTP header `key` for a given `req`.
 */
const char *httprequest_get_header(HTTPRequest *req, const char *key) {
  link_list *tmp = req->head;
  while (tmp != NULL) {
    if (tmp->key && strcmp(tmp->key, key) == 0) {
      return tmp->value;
    }
    tmp = tmp->next;
  }
  return NULL;
}

/**
 * httprequest_get_path
 *
 * Returns the requested path for a given `req`.
 */
const char *httprequest_get_path(HTTPRequest *req) { return req->path; }

/**
 * httprequest_destroy
 *
 * Destroys a `req`, freeing all associated memory.
 */
void httprequest_destroy(HTTPRequest *req) {
  free(req->action);
  free(req->version);
  free(req->path);
  if (req->payload != NULL) {
    free(req->payload);
  }
  link_list *tmp = req->head;
  while (tmp != NULL) {
    link_list *tmp2 = tmp->next;
    free(tmp->key);
    free(tmp->value);
    free(tmp);
    tmp = tmp2;
  }
}