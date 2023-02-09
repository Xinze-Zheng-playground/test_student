#define EMOJI_LOW 0x1F000
#define EMOJI_HIGH 0x1FAFF

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int str_to_utf(const unsigned char *str) {
  int res = 0;
  res += str[0] & 0b00000111;
  res = res << 3;
  for (int i = 1; i < 4; i++) {
    res += str[i] & 0b00111111;
    if (i != 3)
      res = res << 6;
  }
  return res;
}
// convert a utf number to 4 bytes encoded binary numbers
// Assume val is valid for 4 bytes storage
char *utf_to_str(int val) {
  char *res = (char *)malloc(5);
  for (int i = 3; i >= 1; i--) {
    char segment = (char)val;      // Get the last 1 byte
    segment &= 0b00111111;         // Make second most sig bit 1
    res[i] = segment | 0b10000000; // Make first bit 1
    val = val >> 6;                // Last 6 bits are stored
  }
  char segment = (char)val;
  segment &= 0b00000111;
  res[0] = segment | 0b11110000;
  res[4] = '\0';
  return res;
}
// Return your favorite emoji.  Do not allocate new memory.
// (This should **really** be your favorite emoji, we plan to use this later in
// the semester. :))
char *emoji_favorite() {
  char *str = "\U0001F973";
  return str;
}

// Count the number of emoji in the UTF-8 string `utf8str`, returning the count.
// You should consider everything in the ranges starting from (and including)
// U+1F000 up to (and including) U+1FAFF.
int emoji_count(const unsigned char *utf8str) {
  int cnt = 0;
  for (int i = 0; utf8str[i];) {
    char byte = utf8str[i];
    // All emoji uses 4 bytes, check if the following segment is a 4 bytes
    if ((byte & 0b11110000) != 0b11110000) {
      i++;
    } else {
      int utf_code = str_to_utf(utf8str + i);
      if (utf_code >= EMOJI_LOW && utf_code <= EMOJI_HIGH)
        cnt++;
      i += 4;
    }
  }
  return cnt;
}

// Return a random emoji stored in new heap memory you have allocated.  Make
// sure what you return is a valid C-string that contains only one random emoji.
char *emoji_random_alloc() {
  int random = EMOJI_LOW + rand() % (EMOJI_HIGH - EMOJI_LOW);
  return utf_to_str(random);
}

// Modify the UTF-8 string `utf8str` to invert the FIRST character (which may be
// up to 4 bytes) in the string if it the first character is an emoji.  At a
// minimum:
// - Invert "😊" U+1F60A ("\xF0\x9F\x98\x8A") into ANY non-smiling face.
// - Choose at least five more emoji to invert.
void emoji_invertChar(unsigned char *utf8str) {
  char byte = utf8str[0];
  if ((byte & 0b11110000) != 0b11110000) {
    // Not 4 bytes
    return;
  } else {
    int utf_code = str_to_utf(utf8str);
    if (utf_code >= EMOJI_LOW && utf_code <= EMOJI_HIGH) {
      char *map = NULL;
      if (utf_code == 0x1F60A) {
        map = utf_to_str(0x1F972);
      } else if (utf_code == 0x1F973) {
        map = utf_to_str(0x1F618);
      } else if (utf_code == 0x1F923) {
        map = utf_to_str(0x1F602);
      } else if (utf_code == 0x1F97A) {
        map = utf_to_str(0x1F61A);
      } else if (utf_code == 0x1F621) {
        map = utf_to_str(0x1F92C);
      }
      if (map) {
        for (int i = 0; i < 4; i++) {
          utf8str[i] = map[i];
        }
        free(map);
      }
    } else {
      // Use 4 bytes but not an emoji
      return;
    }
  }
}

// Modify the UTF-8 string `utf8str` to invert ALL of the character by calling
// your `emoji_invertChar` function on each character.
void emoji_invertAll(unsigned char *utf8str) {
  for (int i = 0; utf8str[i]; i++) {
    emoji_invertChar(utf8str + i);
  }
}

// Reads the full contents of the file `fileName, inverts all emojis, and
// returns a newly allocated string with the inverted file's content.
unsigned char *emoji_invertFile_alloc(const char *fileName) {
  int size = 70;
  int cnt = 0;
  char temp;
  char *res = (char *)malloc(70);
  FILE *fp = fopen(fileName, "r");
  if (!fp) {
    free(res);
    return NULL;
  }
  // Read in all file char
  while (fscanf(fp, "%c", &temp) != EOF) {
    res[cnt++] = temp;
    if (cnt == size) {
      size *= 2;
      res = realloc(res, size);
    }
  }
  res[cnt] = '\0';
  // res = realloc(res, cnt + 1);
  fclose(fp);
  // Convert
  emoji_invertAll(res);
  res = realloc(res, cnt + 1);
  return res;
}
