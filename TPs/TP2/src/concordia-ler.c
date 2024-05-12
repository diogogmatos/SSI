#include "../includes/lib.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define BLOCK_SIZE 16

int main(int argc, char *argv[])
{
  if (argc < 2)
  {
    char buffer[100];
    snprintf(buffer, 100, "Usage: %s <id>\n",
             argv[0]);
    write(1, buffer, strlen(buffer));
    return 1;
  }

  // get username
  char *username = get_username();
  if (username == NULL)
  {
    perror("[ERROR] Couldn't get username");
    return -1;
  }

  // open message file
  char path[100];
  snprintf(path, 100, "concordia/%s/received/%s", username, argv[1]);

  int fd = open(path, O_RDONLY);
  if (fd == -1)
  {
    perror("[ERROR] Couldn't open message file");
    return -1;
  }

  // convert to message
  MESSAGE m = file_to_message(fd);

  // close message file
  close(fd);

  // print message
  char *str = message_to_string(m, false);
  printf("Mensagem #%s)\n%s\n", argv[1], str);
  fflush(stdout);

  return 0;
}
