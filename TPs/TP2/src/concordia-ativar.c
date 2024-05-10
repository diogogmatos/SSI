#include "lib.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
  // open AD FIFO for writing
  int fd = open("tmp/ad_fifo", O_WRONLY);
  if (fd == -1)
  {
    perror("[ERROR] Couldn't open AD FIFO");
    return -1;
  }

  // get username
  char *username = getlogin();
  if (username == NULL)
  {
    perror("[ERROR] Couldn't get username");
    return -1;
  }

  // create response fifo
  char path[100];
  snprintf(path, 100, "tmp/concordia/%s", username);

  int r = mkfifo(path, 0666);
  if (r == -1)
  {
    perror("[ERROR] Couldn't create response FIFO");
    return -1;
  }

  // create message to send
  MESSAGE m = {
      .sender = username,
      .receiver = "server",
      .type = user_activate,
      .message = "",
      .timestamp = time(NULL),
  };

  // send message
  r = write(fd, &m, sizeof(MESSAGE));
  if (r == -1)
  {
    perror("[ERROR] Couldn't send message");
    return -1;
  }

  // open response fifo for reading
  fd = open(path, O_RDONLY);
  if (fd == -1)
  {
    perror("[ERROR] Couldn't open response FIFO");
    return -1;
  }

  // wait for response
  MESSAGE response;
  int bytes_read = read(fd, &response, sizeof(MESSAGE));
  if (bytes_read == -1)
  {
    perror("[ERROR] Couldn't read response");
    return -1;
  }

  // check if user creation was successful
  if (strcmp(response.message, "failed") == 0)
  {
    perror("[ERROR] User creation failed");
    return -1;
  }

  // create sent directory
  char *dir_path;
  sprintf(dir_path, "concordia/%s/sent", username);
  r = mkdir(dir_path, 0700);
  if (r == -1)
  {
    perror("[ERROR] Couldn't create sent directory");
    return -1;
  }

  // create received directory
  sprintf(dir_path, "concordia/%s/received", username);
  r = mkdir(dir_path, 0700);
  if (r == -1)
  {
    perror("[ERROR] Couldn't create received directory");
    return -1;
  }

  close(fd);
  return 0;
}
