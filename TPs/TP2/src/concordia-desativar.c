#include "lib.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
  // get username
  char *username = getlogin();
  if (username == NULL)
  {
    perror("[ERROR] Couldn't get username");
    return -1;
  }

  // remove sent directory
  char dir_path[100];
  snprintf(dir_path, 100, "concordia/%s/sent", username);

  int r = rmdir(dir_path);
  if (r == -1)
  {
    perror("[ERROR] Couldn't remove sent directory");
    return -1;
  }

  // remove received directory
  sprintf(dir_path, "concordia/%s/received", username);

  r = rmdir(dir_path);
  if (r == -1)
  {
    perror("[ERROR] Couldn't remove received directory");
    return -1;
  }

  // open AD FIFO for writing
  int fd = open("tmp/ad_fifo", O_WRONLY);
  if (fd == -1)
  {
    perror("[ERROR] Couldn't open AD FIFO");
    return -1;
  }

  // create response fifo
  char path[100];
  snprintf(path, 100, "tmp/concordia/%s", username);

  r = mkfifo(path, 0666);
  if (r == -1)
  {
    perror("[ERROR] Couldn't create response FIFO");
    return -1;
  }

  // create message to send
  MESSAGE m;
  strncpy(m.sender, username, STRING_SIZE);
  strncpy(m.receiver, "server", STRING_SIZE);
  m.type = user_deactivate;
  strncpy(m.message, "", STRING_SIZE);
  m.timestamp = time(NULL);

  // send message
  r = write(fd, &m, sizeof(MESSAGE));
  if (r == -1)
  {
    perror("[ERROR] Couldn't send message");
    return -1;
  }

  // close AD FIFO
  close(fd);

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

  // check if user deactivation was successful
  if (strcmp(response.message, "failed") == 0)
  {
    printf("[ERROR] User deactivation failed\n");
    fflush(stdout);
    return -1;
  }

  printf("User '%s' deactivated.\n", username);
  fflush(stdout);

  // close fifo
  close(fd);

  // remove fifo
  unlink(path);

  return 0;
}
