#include "../includes/lib.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define BLOCK_SIZE 16

int read_from_group(char* group, char* id) {
  char group_path[100];
  snprintf(group_path, 100, "concordia/%s/messages", group);

  char message_path[100];
  snprintf(message_path, 100, "%s/%s", group_path, id);

  int fd = open(message_path, O_RDONLY);
  if (fd == -1)
  { 
    char error[100];
    sprintf(error, "[ERROR] Couldn't open message file %s", message_path);
    perror(error);
    return -1;
  }
  
  MESSAGE m = file_to_message(fd);
  m.type = user_message;

  char *str = message_to_string(m, false);
  printf("Mensagem #%s)\n%s\n", id, str);
  fflush(stdout);

  return 0;

}

int main(int argc, char *argv[])
{
  if (argc < 2)
  {
    char buffer[100];
    snprintf(buffer, 100, "Usage: %s <id> [g-<grupo-name>]\n",
             argv[0]);
    write(1, buffer, strlen(buffer));
    return 1;
  }

  if(strncmp(argv[2], "g-", 2) == 0)
  {
    return read_from_group(argv[2], argv[1]);
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
