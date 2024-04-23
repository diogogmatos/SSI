#include "lib.h"
#include <dirent.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

int main(int argc, char *argv[]) {

  int read_bytes = 1;
  int res = mkfifo("tmp/main_fifo", 0666);
  char buffer2[4096];
  memset(buffer2, 0, 4096);
  int res2 = 0;
  if (res == -1) {
    unlink("tmp/main_fifo");
    res2 = mkfifo("tmp/main_fifo", 0666);
  }
  if (res2 == -1) {
    write(1, "Error creating the main fifo",
          strlen("Error creating the main fifo\n"));

  } else {
    write(1, "Main fifo created\n", strlen("Main fifo created\n"));
    while (true) {
      file_d input = open("tmp/main_fifo", O_RDONLY);
      open("tmp/main_fifo", O_WRONLY);
      read_bytes = read(input, buffer2, 4096);
      write(1, buffer2, read_bytes);
    }
  }
  return 0;
}