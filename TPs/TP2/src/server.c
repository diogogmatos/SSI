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

int set_permissions(char *username, char *permissions, char *dir_path)
{
  // set command
  char *execute;
  sprintf(execute, "setfacl -m u:%s:%s %s", username, permissions, dir_path);

  // execute command
  int status = system(execute);
  if (status == 0)
    return 0;
  else
  {
    char *msg;
    sprintf(msg, "[ERROR] Failed to set permissions for %s", username);
    perror(msg);
    return -1;
  }
}

void handle_fifo(int fd, bool is_main_fifo)
{
  MESSAGE m;
  int bytes_read;

  while ((bytes_read = read(fd, &m, sizeof(MESSAGE))) > 0)
  {
    printf("%s", m.type);
    fflush(stdout);

    bool valid = true;

    // get user's dir path
    char path[100];
    snprintf(path, 100, "concordia/%s", m.sender);

    // verify that user exists
    if (is_main_fifo)
    {
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
      {
        printf("entrou no user_activate\n");
        fflush(stdout);

        // open response fifo
        char response_path[100];
        snprintf(response_path, 100, "tmp/concordia/%s", m.sender);
    
        int r = open(response_path, O_WRONLY);
        if (r == -1)
        {
          perror("[ERROR] Couldn't open response FIFO");
          break;
        }

        // create user's directory
        r = mkdir(path, 0700);
        if (r == -1)
        {
          perror("[ERROR] Couldn't create user's directory.");

          // create response message
          MESSAGE response = {
              .sender = "server",
              .receiver = m.sender,
              .type = user_activate,
              .message = "failed",
              .timestamp = time(NULL),
          };

          // send response
          r = write(fd, &response, sizeof(MESSAGE));
          break;
        }

        // set permissions
        set_permissions(m.sender, "rwx", path);

        // create response message
        MESSAGE response = {
            .sender = "server",
            .receiver = m.sender,
            .type = user_activate,
            .message = "succeeded",
            .timestamp = time(NULL),
        };

        // send response
        r = write(fd, &response, sizeof(MESSAGE));
        break;
      }

      case user_deactivate:
      {
        int r = rmdir(path);
        if (r == -1)
        {
          perror("[ERROR] Couldn't remove user's directory.");
          break;
        }
        break;
      }

      case user_message:
      {
        /* code */
        break;
      }

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

  // handle both fifos concurrently
  pid_t pid = fork();
  if (pid == 0) // child process
  {
    // open AD fifo for reading
    int ad_fd = open("tmp/ad_fifo", O_RDONLY);
    if (ad_fd == -1)
    {
      perror("[ERROR] Couldn't open AD FIFO");
      return -1;
    }

    printf("> AD FIFO opened.\n");
    fflush(stdout);

    // int keep_open = open("tmp/ad_fifo", O_WRONLY);

    handle_fifo(ad_fd, false);

    close(ad_fd);
  }
  else // parent process
  {
    // open main fifo for reading
    int main_fd = open("tmp/main_fifo", O_RDONLY);
    if (main_fd == -1)
    {
      perror("[ERROR] Couldn't open main FIFO");
      return -1;
    }

    printf("> Main FIFO opened.\n");
    fflush(stdout);

    // int keep_open = open("tmp/main_fifo", O_WRONLY);

    handle_fifo(main_fd, true);

    close(main_fd);
  }

  unlink("tmp/main_fifo");
  unlink("tmp/ad_fifo");

  return 0;
}
