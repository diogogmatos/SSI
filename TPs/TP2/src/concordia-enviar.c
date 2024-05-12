#include "../includes/lib.h"
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
  char *username = get_username();

  if (username == NULL)
  {
    perror("Error getting username");
    return 1;
  }
  else
  {
    snprintf(message.sender, STRING_SIZE, "%s", username);
  }

  snprintf(message.receiver, STRING_SIZE, "%s", argv[1]);

  int message_len = strlen(argv[2]);
  int total_length = message_len + 1;

  message.timestamp = time(NULL);
  message.type = user_message;

  if (message_len > STRING_SIZE)
  {
    char buffer[100];
    snprintf(buffer, 100, "Message length exceeds string size\n");
    write(1, buffer, strlen(buffer));
    return 1;
  }

  snprintf(message.message, STRING_SIZE, "%s", argv[2]);

  int fd = open("tmp/main_fifo", O_WRONLY);
  if (fd == -1)
  {
    perror("Error opening FIFO for writing");
    return 1;
  }

  printf("MESSAGE: %s \nSize: %d\n", message.message, total_length);
  printf("Sender: %s\n", message.sender);
  printf("Receiver: %s\n", message.receiver);
  printf("Timestamp: %ld\n", message.timestamp);
  printf("Type: %d\n", message.type);


  // Type of message
  int rs = write(fd, &message, sizeof(MESSAGE));
  printf("rs: %d\n", rs);
  if (rs == -1)
  {
    perror("Error writing to FIFO");
    return 1;
  }

  close(fd);

  // make the code to write to the sent folder
  char sent_path[100];
  snprintf(sent_path, 100, "concordia/%s/sent/%s.txt", username, message.receiver);

  int sent = open(sent_path, O_WRONLY | O_CREAT, 0666);
  if (sent == -1)
  {
    perror("Error opening sent file");
    return 1;
  }

  char* message_str = message_to_string(message, true);
  write(sent, message_str, strlen(message_str) * sizeof(char));

  close(sent);

  return 0;
}
