#include "lib/png.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int png_hideGIF(const char *png_filename, const char *gif_filename) {
  PNG_Chunk chunk;
  int size = 500;
  chunk.data = malloc(size);
  chunk.len = 0;
  strcpy(chunk.type, "uiuc");
  FILE *fp = fopen(gif_filename, "r");
  unsigned char c;
  while (fscanf(fp, "%c", &c) != EOF) {
    chunk.data[chunk.len++] = c;
    if (chunk.len == size) {
      size *= 2;
      chunk.data = realloc(chunk.data, size);
    }
  }
  // Inject
  PNG *new = PNG_open("new.png", "w");
  PNG *old = PNG_open(png_filename, "r");
  int cnt = 0;
  while (1) {
    // Read chunk and ensure we get a valid result (exit on error):
    PNG_Chunk new_chunk;
    if (PNG_read(old, &new_chunk) == 0) {
      PNG_close(new);
      PNG_close(old);
      return 1;
    }

    // Report data about the chunk to the command line:
    int bytesWritten = PNG_write(new, &new_chunk);

    // Check for the "IEND" chunk to exit:
    if (strcmp(new_chunk.type, "IEND") == 0) {
      PNG_free_chunk(&new_chunk);
      break;
    }
    cnt++;
    if (cnt == 1) {
      int inject = PNG_write(new, &chunk);
    }
    // Free the memory associated with the chunk we just read:
    PNG_free_chunk(&new_chunk);
  }

  PNG_close(old);
  PNG_close(new);
  PNG_free_chunk(&chunk);
  // Copy
  new = PNG_open(png_filename, "w");
  old = PNG_open("new.png", "r");
  while (1) {
    // Read chunk and ensure we get a valid result (exit on error):
    PNG_Chunk new_chunk;
    if (PNG_read(old, &new_chunk) == 0) {
      PNG_close(new);
      PNG_close(old);
      return 1;
    }

    // Report data about the chunk to the command line:
    int bytesWritten = PNG_write(new, &new_chunk);

    // Check for the "IEND" chunk to exit:
    if (strcmp(new_chunk.type, "IEND") == 0) {
      PNG_free_chunk(&new_chunk);
      break;
    }
    // Free the memory associated with the chunk we just read:
    PNG_free_chunk(&new_chunk);
  }

  return 0;
}

int main(int argc, char *argv[]) {
  // Ensure the correct number of arguments:
  if (argc != 3) {
    printf("Usage: %s <PNG File> <GIF File>\n", argv[0]);
    return ERROR_INVALID_PARAMS;
  }

  return png_hideGIF(argv[1], argv[2]);
}
