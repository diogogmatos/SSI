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
  user_list_message,
  user_respond_message,
  create_group
} MESSAGE_TYPE;

const char *message_type_str[] = {
    "user_activate",
    "user_deactivate",
    "user_message",
    "user_list_message",
    "user_respond_message",
    "create_group"
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

char *message_to_string(MESSAGE m)
{
  char *str = malloc(sizeof(char) * 1000);
  snprintf(str, 1000, "sender: %s\nreceiver: %s\ntype: %s\nmessage: %s\ntime: %s", m.sender, m.receiver, message_type_str[m.type], m.message, ctime(&m.timestamp));
  return str;
}

#endif
