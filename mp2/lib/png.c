#include <arpa/inet.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
//#include <sys/_endian.h>

#include "crc32.h"
#include "png.h"

const int ERROR_INVALID_PARAMS = 1;
const int ERROR_INVALID_FILE = 2;
const int ERROR_INVALID_CHUNK_DATA = 3;
const int ERROR_NO_UIUC_CHUNK = 4;

/**
 * Opens a PNG file for reading (mode == "r" or mode == "r+") or writing (mode
 * == "w").
 *
 * (Note: The function follows the same function prototype as `fopen`.)
 *
 * When the file is opened for reading this function must verify the PNG
 * signature.  When opened for writing, the file should write the PNG signature.
 *
 * This function must return NULL on any errors; otherwise, return a new PNG
 * struct for use with further fuctions in this library.
 */
PNG *PNG_open(const char *filename, const char *mode) {
  FILE *fp;
  fp = fopen(filename, mode);
  if (fp == NULL) {
    return NULL;
  }
  uint8_t verify[8] = {137, 80, 78, 71, 13, 10, 26, 10};
  if (strcmp(mode, "r") == 0 || strcmp(mode, "r+") == 0) {
    unsigned char c;
    int verified = 0;
    for (int i = 0; i < 8 && fscanf(fp, "%c", &c) != EOF; i++) {
      if (c != verify[i])
        break;
      if (i + 1 == 8)
        verified = 1;
    }
    if (!verified) {
      return NULL;
    } else {
      PNG *png = malloc(sizeof(PNG));
      png->fp = fp;
      return png;
    }
  } else if (*mode == 'w') {
    for (int i = 0; i < 8; i++) {
      fprintf(fp, "%c", verify[i]);
    }
    PNG *png = malloc(sizeof(PNG));
    png->fp = fp;
    return png;
  } else {
    // Invalid mode
    return NULL;
  }
}

/**
 * Reads the next PNG chunk from `png`.
 *
 * If a chunk exists, a the data in the chunk is populated in `chunk` and the
 * number of bytes read (the length of the chunk in the file) is returned.
 * Otherwise, a zero value is returned.
 *
 * Any memory allocated within `chunk` must be freed in `PNG_free_chunk`.
 * Users of the library must call `PNG_free_chunk` on all returned chunks.
 */
size_t PNG_read(PNG *png, PNG_Chunk *chunk) {
  if (!png)
    return 0;
  // This is a extremely stupid bug, always use unsigned
  unsigned char c;
  uint32_t len = 0;

  for (int i = 0; i < 4; i++) {
    if (fscanf(png->fp, "%c", &c) == EOF)
      return 0;
    len += c;
    if (i + 1 != 4)
      len = len << 8;
  }
  chunk->len = len;
  for (int i = 0; i < 4; i++) {
    if (fscanf(png->fp, "%c", &c) == EOF) {
      return 0;
    }
    chunk->type[i] = c;
  }
  chunk->type[4] = '\0';
  chunk->data = malloc(chunk->len);
  for (int i = 0; i < chunk->len; i++) {
    if (fscanf(png->fp, "%c", &c) == EOF) {
      return 0;
    }
    chunk->data[i] = c;
  }
  uint32_t crc = 0;
  for (int i = 0; i < 4; i++) {
    if (fscanf(png->fp, "%c", &c) == EOF) {
      return 0;
    }
    crc += c;
    if (i + 1 != 4)
      crc = crc << 8;
  }
  chunk->crc = crc;
  return 12 + chunk->len;
}

/**
 * Writes a PNG chunk to `png`.
 *
 * Returns the number of bytes written.
 */
size_t PNG_write(PNG *png, PNG_Chunk *chunk) {
  int cnt = 0;
  uint32_t net_length = htonl(chunk->len);
  unsigned char *length = (unsigned char *)&net_length;
  for (int i = 0; i < 4; i++) {
    fprintf(png->fp, "%c", length[i]);
  }
  for (int i = 0; i < 4; i++) {
    fprintf(png->fp, "%c", chunk->type[i]);
  }
  for (int i = 0; i < chunk->len; i++) {
    fprintf(png->fp, "%c", chunk->data[i]);
  }
  uint32_t host_crc = 0;
  char *mem = malloc(chunk->len + 4);
  for (int i = 0; i < 4; i++) {
    mem[i] = chunk->type[i];
  }
  for (int i = 0; i < chunk->len; i++) {
    mem[i + 4] = chunk->data[i];
  }
  crc32(mem, 4 + chunk->len, &host_crc);
  free(mem);
  mem = NULL;
  uint32_t net_crc = ntohl(host_crc);
  char *crc = (char *)&net_crc;
  for (int i = 0; i < 4; i++) {
    fprintf(png->fp, "%c", crc[i]);
  }
  return 12 + chunk->len;
}

/**
 * Frees all memory allocated by this library related to `chunk`.
 */
void PNG_free_chunk(PNG_Chunk *chunk) {
  if (chunk->data != NULL)
    free(chunk->data);
}

/**
 * Closes the PNG file and frees all memory related to `png`.
 */
void PNG_close(PNG *png) {
  if (png && png->fp)
    fclose(png->fp);
  if (png)
    free(png);
}