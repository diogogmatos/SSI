#include "../includes/lib.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>


#define BLOCK_SIZE 16

int main(int argc, char *argv[]) {
  if (argc < 2) {
    char buffer[100];
    snprintf(buffer, 100, "Usage: %s [-a]\n",
             argv[0]);
    write(1, buffer, strlen(buffer));
    return 1;
  }

  int fd = open("tmp/main_fifo", O_WRONLY);
  if (fd == -1) {
    perror("Error opening FIFO for writing");
    return 1;
  }

  char *username = get_username();
  if (username == NULL) {
    perror("Error getting username");
    return 1;
  }

  umask(000);
  char path[150] = "tmp/concordia/";
  strcat(path, username);
  int response = mkfifo(path, O_RDONLY);
  if (response == -1) {
    perror("Error creating response FIFO");
    return 1;
  }

  MESSAGE message;
  snprintf(message.sender, STRING_SIZE, "%s", username);
  snprintf(message.receiver, STRING_SIZE, "server");
  message.timestamp = time(NULL);
  message.type = user_list_message;
  strncpy(message.message, "", STRING_SIZE);

  int r = write(fd, &message, sizeof(MESSAGE));
  if (r == -1) {
    perror("Error writing to FIFO");
    return 1;
  }

  close(fd);

  MESSAGE m;
  int read_bytes = 0;
  int number = 0;
  while(read_bytes = read(response, &m, sizeof(MESSAGE))) {
    if (read_bytes == -1) {
      perror("Error reading from FIFO");
      return 1;
    }
    number++;
    printf("Message from %s: %s\n", message.sender, message.message);

    char* message_path;
    snprintf(message_path, 100, "concordia/%s/received/%d", username, number);

    int message_fd = open(message_path, O_WRONLY | O_CREAT, 0666);
    if (message_fd == -1) {
      perror("Error opening message file");
      return 1;
    }
    
    write(message_fd, m.sender, sizeof(char) * strlen(m.sender));
    write(message_fd, "/n", 1);
    write(message_fd, m.receiver, sizeof(char) * strlen(m.receiver));
    write(message_fd, "/n", 1);
    write(message_fd, m.message, sizeof(char) * strlen(m.message));
    write(message_fd, "/n", 1);

    close(message_fd);
  }

  return 0;
}
