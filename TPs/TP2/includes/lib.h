#ifndef LIB_H
#define LIB_H

#include "../src/lib.c"
#include <stdbool.h>

#define STRING_SIZE 100

typedef enum _message_type MESSAGE_TYPE;

const char *message_type_str[];

typedef struct _message MESSAGE;

typedef int file_d;

char *get_username();
char *message_to_string(MESSAGE m, bool simple);
int count_files_in_dir(char *path);
int message_to_file(int fd, MESSAGE m);

#endif
