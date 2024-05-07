#include "lib.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>


#define BLOCK_SIZE 16

int main(int argc, char *argv[]) {
  if (argc < 3) {
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

  char *username = getlogin();

  if (username == NULL) {
    perror("Error getting username");
    return 1;
  }




  close(fd);
  return 0;
}