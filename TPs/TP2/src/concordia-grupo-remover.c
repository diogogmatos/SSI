#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include "lib.h"

int main(int argc, char *argv[]) {
    // get group_name
  char *group_name = argv[1];
  if (group_name == NULL)
  {
    perror("[ERROR] Couldn't get group_name");
    return -1;
  }

  // remove sent directory
  char command[100];
  snprintf(command, 100, "rm -rf concordia/g-%s/messages", group_name);

  int r = system(command);
  if (r == -1)
  {
    perror("[ERROR] Couldn't remove messages directory");
    return -1;
  }

  // open Main FIFO for writing
  int fd = open("tmp/main_fifo", O_WRONLY);
  if (fd == -1)
  {
    perror("[ERROR] Couldn't open AD FIFO");
    return -1;
  }

  // create response fifo
  char path[100];
  snprintf(path, 100, "tmp/concordia/%s", group_name);
  unlink(path);
  
  umask(000);
  r = mkfifo(path, 0666);
  if (r == -1)
  {
    perror("[ERROR] Couldn't create response FIFO");
    return -1;
  }

  char* username = get_username();

  // create message to send
  MESSAGE m;
  strncpy(m.sender, username, STRING_SIZE);
  strncpy(m.receiver, "server", STRING_SIZE);
  m.type = group_remove;
  strncpy(m.message, group_name, STRING_SIZE);
  m.timestamp = time(NULL);

  // send message
  r = write(fd, &m, sizeof(MESSAGE));
  if (r == -1)
  {
    perror("[ERROR] Couldn't send message");
    return -1;
  }

  // close Main FIFO
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
    printf("[ERROR] Group deletion failed\n");
    fflush(stdout);
    return -1;
  }

  printf("Group '%s' deleted.\n", group_name);
  fflush(stdout);

  // close fifo
  close(fd);

  // remove fifo
  unlink(path);

  return 0;
}
