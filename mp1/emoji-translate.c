#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "emoji-translate.h"
#include "emoji.h"

#define EMOJI_LOW 0x1F000
#define EMOJI_HIGH 0x1FAFF
int is_emoji(unsigned char *str) {
  if (!str || (str[0] & 0b11110000) != 0b11110000)
    return 0;
  int utf_code = str_to_utf(str);
  if (utf_code >= EMOJI_LOW && utf_code <= EMOJI_HIGH)
    return 1;
  return 0;
}
// Function that return the index in dictionary for matching emoji, -1 if not
// found; Also the size of source is stored in int *size
int find_longest_match_idx(emoji_t *emoji, unsigned char *str, int start,
                           int *size) {
  int idx = -1;
  // Check if there are i consecutive matched pattern
  for (int i = 1; i < (int)strlen(str); i++) {
    int found = 0;
    for (int j = 0; j < emoji->cnt; j++) {
      // Compare the sources pattern
      if (start + i * 4 <= (int)strlen(str) &&
          strncmp(str + start, emoji->sources[j], i * 4) == 0) {
        found = 1;
        char exact_compare[i * 4 + 1];
        strncpy(exact_compare, str + start, i * 4);
        exact_compare[i * 4] = '\0';
        if (strcmp(exact_compare, emoji->sources[j]) == 0)
          idx = j;
      }
    }
    if (!found)
      break;
    *size = i;
  }
  return idx;
}
void emoji_init(emoji_t *emoji) {
  if (!emoji)
    return;
  emoji->size = 20;
  emoji->cnt = 0;
  emoji->sources = malloc(20 * sizeof(char *));
  emoji->translations = malloc(20 * sizeof(char *));
}

void emoji_add_translation(emoji_t *emoji, const unsigned char *source,
                           const unsigned char *translation) {
  if (!emoji)
    return;
  emoji->sources[emoji->cnt] = source;
  emoji->translations[emoji->cnt] = translation;
  emoji->cnt++;
  if (emoji->cnt == emoji->size) {
    emoji->size *= 2;
    emoji->sources = realloc(emoji->sources, emoji->size * sizeof(char *));
    emoji->translations =
        realloc(emoji->translations, emoji->size * sizeof(char *));
  }
  return;
}

// Translates the emojis contained in the file `fileName`.
const unsigned char *emoji_translate_file_alloc(emoji_t *emoji,
                                                const char *fileName) {
  FILE *fp = fopen(fileName, "r");
  if (!fp) {
    return NULL;
  }
  // Read file content into str
  int size = 20;
  int cnt = 0;
  char temp;
  unsigned char *str = malloc(size);
  while (fscanf(fp, "%c", &temp) != EOF) {
    str[cnt++] = temp;
    if (cnt == size) {
      size *= 2;
      str = realloc(str, size);
    }
  }
  str[cnt] = '\0';
  fclose(fp);
  if (!emoji && emoji->cnt == 0)
    return str;
  // Start translation
  for (int i = 0; str[i]; i++) {

    if (is_emoji(str + i)) {
      // Get the index in dictionary
      int size = 0;
      int idx = find_longest_match_idx(emoji, str, i, &size);
      if (idx != -1) {
        // store the first i bit
        char str1[i + 1];
        strncpy(str1, str, i);
        str1[i] = '\0';
        //  Store translation
        char str2[strlen(emoji->translations[idx]) + 1];
        strcpy(str2, emoji->translations[idx]);
        str2[strlen(emoji->translations[idx])] = '\0';
        // store the bits following the translation
        char str3[strlen(str) - idx - size * 4 + 1];
        strcpy(str3, str + i + size * 4);
        // Creating new string via strcat
        char *new_string =
            malloc(strlen(str1) + strlen(str2) + strlen(str3) + 1);
        new_string[0] = '\0';
        strcat(new_string, str1);
        strcat(new_string, str2);
        strcat(new_string, str3);

        free(str);
        str = new_string;

        // char *str2[strlen(str) - i - size + 2];
      }
    }
  }
  return str;
}
void emoji_destroy(emoji_t *emoji) {
  if (emoji == NULL)
    return;
  if (emoji->sources)
    free(emoji->sources);
  if (emoji->translations)
    free(emoji->translations);
}
