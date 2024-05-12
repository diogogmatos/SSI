#ifndef LIB_H
#define LIB_H

#include <stdio.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>

#include "../src/lib.c"

#define STRING_SIZE 100

typedef enum _message_type
{
  user_activate,
  user_deactivate,
  user_message,
  user_list_message
} MESSAGE_TYPE;

const char *message_type_str[] = {
    "user_activate",
    "user_deactivate",
    "user_message",
};

typedef struct _message
{
  char sender[STRING_SIZE];
  char receiver[STRING_SIZE];
  MESSAGE_TYPE type;
  char message[STRING_SIZE];
  time_t timestamp;
} MESSAGE;

typedef int file_d;

char *get_username();

#endif
