#include "http.h"

#include <netinet/in.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

void *client_thread(void *vptr) {
  int fd = *((int *)vptr);
  HTTPRequest req;
  httprequest_read(&req, fd);
  char *file_name = httprequest_get_path(&req);
  unsigned char *path;
  if (strcmp(file_name, "/") == 0) {
    path = calloc(strlen("static/index.html") + 1, 1);
    strcpy(path, "static/index.html");
  } else {
    path = calloc(strlen(file_name) + 7, 1);
    strcpy(path, "static");
    strcat(path, file_name);
  }
  FILE *fp = fopen(path, "rb");
  if (fp == NULL) {
    write(fd, "HTTP/1.1 404 Not Found\r\n\r\n",
          strlen("HTTP/1.1 404 Not Found\r\n\r\n"));
    close(fd);
    close(fp);
    free(path);
    return NULL;
  }
  unsigned char *response_status = strdup("HTTP/1.1 200 OK\r\n");
  unsigned char *response_content;
  if (path[strlen(path) - 1] == 'g') {
    response_content = strdup("Content-Type: image/png\r\n");
  } else {
    response_content = strdup("Content-Type: text/html\r\n");
  }
  fseek(fp, 0, SEEK_END);       // Move to the last position in the file stream
  long file_length = ftell(fp); // The last position of the file stream = number
                                // of bytes in that file
  fseek(fp, 0,
        SEEK_SET); // Reset to the first position so we can read in the file
  unsigned char *content_buffer[file_length];
  int cnt = fread(content_buffer, 1, file_length, fp);
  unsigned char *response_header = strcat(response_status, response_content);
  response_header = strcat(response_header, "\r\n");
  unsigned char *response =
      calloc(strlen(response_header) + file_length + 1, 1);
  memcpy(response, response_header, strlen(response_header));
  memcpy(response + strlen(response_header), content_buffer, file_length);
  write(fd, response, strlen(response_header) + file_length);
  close(fd);
  free(path);
  free(response_status);
  close(fp);

  return NULL;
}

int main(int argc, char *argv[]) {
  if (argc != 2) {
    printf("Usage: %s <port>\n", argv[0]);
    return 1;
  }
  int port = atoi(argv[1]);
  printf("Binding to port %d. Visit http://localhost:%d/ to interact with your "
         "server!\n",
         port, port);

  // socket:
  int sockfd = socket(AF_INET, SOCK_STREAM, 0);

  // bind:
  struct sockaddr_in server_addr, client_address;
  memset(&server_addr, 0x00, sizeof(server_addr));
  server_addr.sin_family = AF_INET;
  server_addr.sin_addr.s_addr = INADDR_ANY;
  server_addr.sin_port = htons(port);
  bind(sockfd, (const struct sockaddr *)&server_addr, sizeof(server_addr));

  // listen:
  listen(sockfd, 10);

  // accept:
  socklen_t client_addr_len;
  while (1) {
    int *fd = malloc(sizeof(int));
    *fd = accept(sockfd, (struct sockaddr *)&client_address, &client_addr_len);
    printf("Client connected (fd=%d)\n", *fd);

    pthread_t tid;
    pthread_create(&tid, NULL, client_thread, fd);
    pthread_detach(tid);
  }

  return 0;
}