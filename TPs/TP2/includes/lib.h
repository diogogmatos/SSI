#ifndef LIB_H
#define LIB_H

#include <stdio.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>

typedef struct message {
  char *sender;
  char *receiver;
  char *subject;
  char *message;
  time_t timestamp;
} Message;

typedef int file_d;

/**
 * @brief Function to serialize a message
 *
 * @param message Message to be serialized
 * @param buffer Buffer to store the serialized message
 * @param buffer_size Buffer size
 */
void serializeMessage(Message *message, char *buffer, size_t buffer_size);

#endif
