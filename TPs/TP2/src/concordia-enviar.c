#include "../includes/lib.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define BLOCK_SIZE 16

int send_to_group(char* group, char* message) {

  char group_path[100];
  snprintf(group_path, 100, "concordia/%s/messages", group);

  int nr_msgs = count_files_in_dir(group_path);
  if (nr_msgs == -1)
  {
    return -1;
  }

  MESSAGE m;
  sprintf(m.sender, get_username());
  sprintf(m.receiver, group + 2);
  sprintf(m.message, message);
  m.timestamp = time(NULL);

  char message_path[100];
  snprintf(message_path, 100, "%s/%d", group_path, nr_msgs + 1);
  
  int fd = open(message_path, O_WRONLY | O_CREAT, 0755);
  if (fd == -1)
  {
    perror("[ERROR] Couldn't open/create message file");
    return -1;
  }
  message_to_file(fd, m);
  close(fd);

  char group_owner[100];
  get_file_owner(group_owner, group_path);
  if (group_owner == NULL)
  {
    return -1;
  }
  
  char owner_perms[100];
  snprintf(owner_perms, 100, "setfacl -m u:%s:r-x %s", group_owner, message_path);

  int r = system(owner_perms);
  if (r == -1)
  {
    perror("[ERROR] Couldn't set owner permissions");
    return -1;
  }

  return 0;
  
}


int main(int argc, char *argv[])
{
  if (argc < 3)
  {
    char buffer[100];
    snprintf(buffer, 100, "Usage: %s <receiver> <message>\n",
             argv[0]);
    write(1, buffer, strlen(buffer));
    return -1;
  }

  // if(strncmp(argv[1], "g-", 2) == 0) {
  //   return send_to_group(argv[1], argv[2]);
  // }

  // get username
  char *username = get_username();
  if (username == NULL)
  {
    perror("[ERROR] Couldn't get username");
    return -1;
  }

  // check msg length
  int message_len = strlen(argv[2]);
  int total_length = message_len + 1;

  if (message_len > STRING_SIZE)
  {
    printf("[ERROR] Message length exceeds maximum size\n");
    fflush(stdout);
    return -1;
  }

  // create message
  MESSAGE message;
  strncpy(message.sender, username, STRING_SIZE);
  strncpy(message.receiver, argv[1], STRING_SIZE);
  message.type = user_message;
  strncpy(message.message, argv[2], STRING_SIZE);
  message.timestamp = time(NULL);

  // open main FIFO for writing
  int fd = open("tmp/main_fifo", O_WRONLY);
  if (fd == -1)
  {
    perror("[ERROR] Couldn't open main FIFO");
    return -1;
  }

  // send message
  int r = write(fd, &message, sizeof(MESSAGE));
  if (r == -1)
  {
    perror("[ERROR] Couldn't send message");
    return -1;
  }

  // close main FIFO
  close(fd);

  // get sent path
  char sent_path[100];
  snprintf(sent_path, 100, "concordia/%s/sent", username);

  // count messages
  int nr_msgs = count_files_in_dir(sent_path);
  if (nr_msgs == -1)
  {
    return -1;
  }

  // get message path
  char message_path[100];
  snprintf(message_path, 100, "%s/%d", sent_path, nr_msgs + 1);

  // create message file
  fd = open(message_path, O_WRONLY | O_CREAT, 0666);
  if (fd == -1)
  {
    perror("[ERROR] Couldn't create message file");
    return -1;
  }

  // write message to file
  message_to_file(fd, message);

  // close file
  close(fd);

  printf("Message sent to user '%s'\n", argv[1]);
  fflush(stdout);

  return 0;
}
