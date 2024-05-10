#include "lib.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define BLOCK_SIZE 16

int main(int argc, char *argv[])
{
  if (argc < 3)
  {
    char buffer[100];
    snprintf(buffer, 100, "Usage: %s <receiver> <message>\n",
             argv[0]);
    write(1, buffer, strlen(buffer));
    return 1;
  }

  MESSAGE message;
  message.receiver = argv[0];
  message.message = argv[1];

  int total_length = 0;
  for (int i = 2; i < argc; i++)
  {
    total_length += strlen(argv[i]) + 1;
  }

  message.message = malloc(total_length);
  if (message.message == NULL)
  {
    perror("Memory allocation failed");
    return 1;
  }

  strcpy(message.message, "");
  for (int i = 2; i < argc; i++)
  {
    strcat(message.message, argv[i]);
    if (i < argc - 1)
    {
      strcat(message.message, " ");
    }
  }

  message.timestamp = time(NULL);
  int type_len = strlen(argv[0]);
  int receiver_len = strlen(argv[1]);
  int message_len = strlen(argv[2]);

  if (receiver_len > BLOCK_SIZE ||
      message_len > 128)
  {
    char buffer[100];
    snprintf(buffer, 100, "Data length exceeds block size\n");
    write(1, buffer, strlen(buffer));
    return 1;
  }

  int fd = open("tmp/main_fifo", O_WRONLY);
  if (fd == -1)
  {
    perror("Error opening FIFO for writing");
    return 1;
  }

  char *username = getlogin();

  if (username == NULL)
  {
    perror("Error getting username");
    return 1;
  }
  else
  {
    message.sender = username;
  }

  printf("MESSAGE: %s \nSize: %d\n", message.message, total_length);
  printf("Sender: %s\n", message.sender);

  // Type of message
  write(fd, message_type_str[message.type], type_len);

  // Separator
  write(fd, "\n", 1);

  // MESSAGE Receiver
  write(fd, message.receiver, receiver_len);

  // Separator
  write(fd, "\n", 1);

  // MESSAGE Body
  write(fd, message.message, total_length);

  // Separator
  write(fd, "\n", 1);

  // MESSAGE Sender
  write(fd, message.sender, strlen(message.sender));

  close(fd);
  return 0;
}
