#include "../includes/lib.h"
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

void handle_fifo(int fd, bool is_main_fifo)
{
  MESSAGE m;
  int bytes_read;

  while ((bytes_read = read(fd, &m, sizeof(MESSAGE))) > 0)
  {
    bool valid = true;

    // verify that user exists
    if (is_main_fifo)
    {
      char *path = strcat("concordia/", m.sender);
      int r = open(path, O_RDONLY);
      if (r == -1)
      {
        perror("[ERROR] User doesn't exist.");
        valid = false;
      }
    }

    if (valid)
    {
      switch (m.type)
      {
      case user_activate:
        /* code */
        break;

      case user_deactivate:
        /* code */
        break;

      case user_message:
        /* code */
        break;

      default:
        break;
      }
    }
  }
}

int main(int argc, char *argv[])
{
  // create main fifo
  int r1 = mkfifo("tmp/main_fifo", 0666);
  if (r1 == -1)
  {
    perror("[ERROR] Couldn't create main FIFO");
    return -1;
  }

  printf("> Main FIFO created.\n");
  fflush(stdout);

  // create activate/deactivate (AD) fifo
  int r2 = mkfifo("tmp/ad_fifo", 0666);
  if (r2 == -1)
  {
    perror("[ERROR] Couldn't create AD FIFO");
    return -1;
  }

  printf("> AD FIFO created.\n");
  fflush(stdout);

  // open main fifo
  int main_fd = open("tmp/main_fifo", O_RDONLY);
  if (main_fd == -1)
  {
    perror("[ERROR] Couldn't open main FIFO");
    return -1;
  }

  printf("> Main FIFO opened.\n");
  fflush(stdout);

  // open AD fifo
  int ad_fd = open("tmp/ad_fifo", O_RDONLY);
  if (ad_fd == -1)
  {
    perror("[ERROR] Couldn't open AD FIFO");
    return -1;
  }

  printf("> AD FIFO opened.\n");
  fflush(stdout);

  // allows server to keep fifo's open
  int keep_open = open("tmp/main_fifo", O_WRONLY);
  keep_open = open("tmp/ad_fifo", O_WRONLY);

  // handle both fifos concurrently
  pid_t pid = fork();
  if (pid == 0) // child process
  {
    handle_fifo(ad_fd, false);
  }
  else // parent process
  {
    handle_fifo(main_fd, true);
  }

  // close fifos
  close(main_fd);
  close(ad_fd);
  unlink("tmp/main_fifo");
  unlink("tmp/ad_fifo");

  return 0;
}
