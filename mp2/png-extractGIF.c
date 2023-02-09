#include "lib/png.h"
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int png_extractGIF(const char *png_filename, const char *gif_filename) {
  PNG *png = PNG_open(png_filename, "r");
  PNG_Chunk chunk;
  while (1) {
    int i = PNG_read(png, &chunk);
    if (i == 0) {
      PNG_free_chunk(&chunk);
      PNG_close(png);
      return 1;
    }
    if (strcmp(chunk.type, "uiuc") == 0)
      break;
  }
  FILE *fp = fopen(gif_filename, "w");
  for (int i = 0; i < chunk.len; i++) {
    fprintf(fp, "%c", chunk.data[i]);
  }
  fclose(fp);
  PNG_free_chunk(&chunk);
  PNG_close(png);
  return 0;
}

int main(int argc, char *argv[]) {
  // Ensure the correct number of arguments:
  if (argc != 3) {
    printf("Usage: %s <PNG File> <GIF Name>\n", argv[0]);
    return ERROR_INVALID_PARAMS;
  }

  return png_extractGIF(argv[1], argv[2]);
}
