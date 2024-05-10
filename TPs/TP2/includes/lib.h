#ifndef LIB_H
#define LIB_H

#include <stdio.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>

typedef enum _message_type
{
  user_activate,
  user_deactivate,
  user_message,
} MESSAGE_TYPE;

const char *message_type_str[] = {
    "user_activate",
    "user_deactivate",
    "user_message",
};

typedef struct _message
{
  char *sender;
  char *receiver;
  MESSAGE_TYPE type;
  char *message;
  time_t timestamp;
} MESSAGE;

typedef int file_d;

/**
 * @brief Function to serialize a message
 *
 * @param message MESSAGE to be serialized
 * @param buffer Buffer to store the serialized message
 * @param buffer_size Buffer size
 */
void serializeMESSAGE(MESSAGE *message, char *buffer, size_t buffer_size);

#endif
