#include "../includes/lib.h"
#include "../includes/queue.h"

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

int execute_command(char *command)
{
  int status = system(command);
  if (status == 0)
    return 0;
  else
  {
    perror("[ERROR] Failed to execute command");
    return -1;
  }
}

int set_permissions(char *username, char *permissions, char *dir_path)
{
  // set command
  char execute[100];
  snprintf(execute, 100, "setfacl -m u:%s:%s %s", username, permissions, dir_path);

  // execute command
  execute_command(execute);
}

void handle_fifo(int fd, bool is_main_fifo, QUEUE *queue)
{
  MESSAGE m;
  int bytes_read;

  while ((bytes_read = read(fd, &m, sizeof(MESSAGE))) > 0)
  {
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
        perror("[ERROR] User doesn't exist");
        valid = false;
      }
      close(r);
    }

    if (valid)
    {
      switch (m.type)
      {
      case user_activate:
      {
        set_permissions(m.sender, "rwx", "tmp/main_fifo");
        set_permissions(m.sender, "rwx", "tmp/concordia/");
        // open response fifo
        char response_path[100];
        snprintf(response_path, 100, "tmp/concordia/%s", m.sender);

        int response_fd = open(response_path, O_WRONLY);
        if (response_fd == -1)
        {
          perror("[ERROR] Couldn't open response FIFO");
          break;
        }

        // create user's directory
        int r = mkdir(path, 0700);
        if (r == -1)
        {
          perror("[ERROR] Couldn't create user's directory");

          // create response message
          MESSAGE response;
          strncpy(response.sender, "server", STRING_SIZE);
          strncpy(response.receiver, m.sender, STRING_SIZE);
          response.type = user_activate;
          strncpy(response.message, "failed", STRING_SIZE);
          response.timestamp = time(NULL);

          // send response
          r = write(response_fd, &response, sizeof(MESSAGE));

          // close response fifo
          close(response_fd);

          break;
        }

        // set permissions
        set_permissions(m.sender, "rwx", path);

        // create response message
        MESSAGE response;
        strncpy(response.sender, "server", STRING_SIZE);
        strncpy(response.receiver, m.sender, STRING_SIZE);
        response.type = user_activate;
        strncpy(response.message, "success", STRING_SIZE);
        response.timestamp = time(NULL);

        // send response
        r = write(response_fd, &response, sizeof(MESSAGE));

        // close response fifo
        close(response_fd);

        printf("> User '%s' activated.\n", m.sender);
        fflush(stdout);

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

        // open response fifo
        char response_path[100];
        snprintf(response_path, 100, "tmp/concordia/%s", m.sender);

        int response_fd = open(response_path, O_WRONLY);
        if (response_fd == -1)
        {
          perror("[ERROR] Couldn't open response FIFO");

          // create response message
          MESSAGE response;
          strncpy(response.sender, "server", STRING_SIZE);
          strncpy(response.receiver, m.sender, STRING_SIZE);
          response.type = user_deactivate;
          strncpy(response.message, "failed", STRING_SIZE);
          response.timestamp = time(NULL);

          // send response
          r = write(response_fd, &response, sizeof(MESSAGE));

          // close response fifo
          close(response_fd);

          break;
        }

        // create response message
        MESSAGE response;
        strncpy(response.sender, "server", STRING_SIZE);
        strncpy(response.receiver, m.sender, STRING_SIZE);
        response.type = user_deactivate;
        strncpy(response.message, "success", STRING_SIZE);
        response.timestamp = time(NULL);

        // send response
        r = write(response_fd, &response, sizeof(MESSAGE));

        // close response fifo
        close(response_fd);

        printf("> User '%s' deactivated.\n", m.sender);
        fflush(stdout);

        break;
      }

      case create_group:
      {
        // open response fifo
        char response_path[100];
        snprintf(response_path, 100, "tmp/concordia/%s", m.message);

        int response_fd = open(response_path, O_WRONLY);
        if (response_fd == -1)
        {
          perror("[ERROR] Couldn't open response FIFO");
          break;
        }

        // create group's directory
        char group_path[100];
        snprintf(group_path, 100, "concordia/%s", m.message);
        int r = mkdir(group_path, 0700);
        if (r == -1)
        {
          char error[100];
          snprintf(error, 100, "[ERROR] Couldn't create group's directory '%s'", path);
          perror(error);

          // create response message
          MESSAGE response;
          strncpy(response.sender, "server", STRING_SIZE);
          strncpy(response.receiver, m.sender, STRING_SIZE);
          response.type = user_activate;
          strncpy(response.message, "failed", STRING_SIZE);
          response.timestamp = time(NULL);

          // send response
          r = write(response_fd, &response, sizeof(MESSAGE));

          // close response fifo
          close(response_fd);

          break;
        }

        // set permissions
        set_permissions(m.sender, "rwx", group_path);

        // create response message
        MESSAGE response;
        strncpy(response.sender, "server", STRING_SIZE);
        strncpy(response.receiver, m.sender, STRING_SIZE);
        response.type = user_activate;
        strncpy(response.message, "success", STRING_SIZE);
        response.timestamp = time(NULL);

        // send response
        r = write(response_fd, &response, sizeof(MESSAGE));

        // close response fifo
        close(response_fd);

        printf("> New group '%s' created.\n", m.message);
        fflush(stdout);

        break;
      }

      case user_message:
      {
        // store new message in queue
        int r = push_message(queue, m);
        if (r == -1)
          break;

        printf("> New message received from '%s'\n", m.sender);
        fflush(stdout);

        break;
      }

      case user_list_message:
      {
        // open response fifo
        char response_path[100];
        snprintf(response_path, 100, "tmp/concordia/%s", m.sender);

        int response_fd = open(response_path, O_WRONLY);
        if (response_fd == -1)
        {
          perror("[ERROR] Couldn't open response FIFO");
          break;
        }

        // send all new messages to user
        for (int i = queue->current_index; i > 0; i--)
        {
          MESSAGE stored_msg = pop_message(queue);

          // if message receiver is the user that sent the list command
          if (strcmp(stored_msg.receiver, m.sender) == 0)
          {
            // send message
            int r = write(response_fd, &stored_msg, sizeof(MESSAGE));
            if (r == -1)
            {
              perror("[ERROR] Couldn't send stored message");
              break;
            }
          }
        }

        // create final response message
        MESSAGE response;
        strncpy(response.sender, "server", STRING_SIZE);
        strncpy(response.receiver, m.sender, STRING_SIZE);
        response.type = user_list_message;
        strncpy(response.message, "end", STRING_SIZE);
        response.timestamp = time(NULL);

        // send response
        int r = write(response_fd, &response, sizeof(MESSAGE));
        if (r == -1)
        {
          perror("[ERROR] Couldn't send response message");
        }

        // close response fifo
        close(response_fd);

        printf("> New messages sent to user '%s'.\n", m.sender);
        fflush(stdout);

        break;
      }

      case user_respond_message:
      {
        char fifo_path[100];
        snprintf(fifo_path, 100, "tmp/main_fifo");
        int fifo;
      }

      default:
        break;
      }
    }
  }
}

void reapply_perms(const char *dirname)
{
  DIR *dir;
  struct dirent *entry;

  // open directory
  dir = opendir(dirname);
  if (dir == NULL)
  {
    perror("opendir");
    return;
  }

  // read directory entries
  while ((entry = readdir(dir)) != NULL)
  {
    // exclude current directory and parent directory entries
    if (strcmp(entry->d_name, ".") != 0 && strcmp(entry->d_name, "..") != 0)
    {
      // give rwx permission to the main FIFO for the user
      set_permissions(entry->d_name, "rwx", "tmp/main_fifo");
    }
  }

  // close directory
  closedir(dir);
}

int main(int argc, char *argv[])
{
  // ensure permissions are not masked
  umask(000);

  // create tmp directory
  int r = mkdir("tmp", 0755);

  // create tmp/concordia directory
  r = mkdir("tmp/concordia", 0777);

  // create concordia directory, if it doesn't exist
  r = mkdir("concordia", 0755);

  // create main fifo
  int r1 = mkfifo("tmp/main_fifo", 0700);
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

  // open main fifo for reading and writing
  int main_fd = open("tmp/main_fifo", O_RDWR);
  if (main_fd == -1)
  {
    perror("[ERROR] Couldn't open main FIFO");
    return -1;
  }

  printf("> Main FIFO opened.\n");
  fflush(stdout);

  // open AD fifo for reading and writing
  int ad_fd = open("tmp/ad_fifo", O_RDWR);
  if (ad_fd == -1)
  {
    perror("[ERROR] Couldn't open AD FIFO");
    return -1;
  }

  printf("> AD FIFO opened.\n");
  fflush(stdout);

  // reapply main FIFO permissions for existing users
  reapply_perms("concordia");

  // handle both fifos concurrently
  pid_t pid = fork();
  if (pid == 0) // child process
  {
    // close write end of AD fifo
    close(ad_fd);

    // create message queue
    QUEUE queue;
    queue.current_index = 0;

    // handle main fifo
    handle_fifo(main_fd, true, &queue);

    close(main_fd);
  }
  else // parent process
  {
    // close write end of main fifo
    close(main_fd);

    // handle AD fifo
    handle_fifo(ad_fd, false, NULL);

    close(ad_fd);
  }

  unlink("tmp/main_fifo");
  unlink("tmp/ad_fifo");
  unlink("tmp/concordia");
  unlink("tmp");

  return 0;
}
