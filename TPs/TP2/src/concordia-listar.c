#include "../includes/lib.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>

int main(int argc, char *argv[])
{
  // get username
  char *username = get_username();
  if (username == NULL)
  {
    perror("[ERROR] Couldn't get username");
    return -1;
  }

  // get received messages path
  char *received_path[100];
  snprintf(received_path, 100, "concordia/%s/received", username);

  // if -a option is passed, print saved messages
  if (argc == 2 && strcmp(argv[1], "-a") == 0)
  {
    // open directory
    DIR *dir = opendir(received_path);
    struct dirent *entry;
    if (dir == NULL)
    {
      perror("[ERROR] Couldn't open directory");
      return -1;
    }

    // print all messages
    while ((entry = readdir(dir)) != NULL)
    {
      // filter out "." and ".." entries
      if (strcmp(entry->d_name, ".") != 0 && strcmp(entry->d_name, "..") != 0)
      {
        char *message_path[100];
        snprintf(message_path, 100, "%s/%s", received_path, entry->d_name);

        int message_fd = open(message_path, O_RDONLY);
        if (message_fd == -1)
        {
          perror("[ERROR] Couldn't open message file");
          return -1;
        }

        MESSAGE m = file_to_message(message_fd);

        // print message
        char *str = message_to_string(m, true);
        printf("Mensagem #%s)\n%s\n", entry->d_name, str);
        fflush(stdout);

        // close message file
        close(message_fd);
      }
    }

    // close directory
    closedir(dir);
  }

  // create response fifo
  char path[100];
  snprintf(path, 100, "tmp/concordia/%s", username);

  umask(000);
  int r = mkfifo(path, 0666);
  if (r == -1)
  {
    perror("[ERROR] Couldn't create response FIFO");
    return -1;
  }

  // open main FIFO for writing
  int fd = open("tmp/main_fifo", O_WRONLY);
  if (fd == -1)
  {
    perror("[ERROR] Couldn't open main FIFO");
    return -1;
  }

  // create message to send
  MESSAGE m;
  strncpy(m.sender, username, STRING_SIZE);
  strncpy(m.receiver, "server", STRING_SIZE);
  m.type = user_list_message;
  strncpy(m.message, "", STRING_SIZE);
  m.timestamp = time(NULL);

  // send message
  r = write(fd, &m, sizeof(MESSAGE));
  if (r == -1)
  {
    perror("[ERROR] Couldn't send message");
    return -1;
  }

  // close main FIFO
  close(fd);

  // open response fifo for reading
  fd = open(path, O_RDWR);
  if (fd == -1)
  {
    perror("[ERROR] Couldn't open response FIFO");
    return -1;
  }

  // count messages
  int nr_msgs = count_files_in_dir(received_path);
  if (nr_msgs == -1)
  {
    return -1;
  }

  // wait for response
  MESSAGE response;
  int bytes_read;

  while ((bytes_read = read(fd, &response, sizeof(MESSAGE))) > 0 && strcmp(response.message, "end") != 0)
  {
    nr_msgs++;

    // write message to file
    char *message_path[100];
    snprintf(message_path, 100, "%s/%d", received_path, nr_msgs);

    int message_fd = open(message_path, O_WRONLY | O_CREAT, 0700);
    if (message_fd == -1)
    {
      perror("[ERROR] Couldn't open/create message file");
      return -1;
    }

    message_to_file(message_fd, response);

    // print message
    char *str = message_to_string(response, true);
    printf("Mensagem #%d)\n%s\n", nr_msgs, str);
    fflush(stdout);

    // close message file
    close(message_fd);
  }

  // close and remove response fifo
  close(fd);
  unlink(path);

  return 0;
}
