#include "encrypt.h"
#include "lib.h"
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define BLOCK_SIZE 16

void serializeMessage(Message *message, char *buffer, size_t buffer_size) {
  snprintf(buffer, buffer_size, "%s|%s|%s|%s|%ld", message->sender,
           message->receiver, message->subject, message->message,
           message->timestamp);
}

int main(int argc, char *argv[]) {
  if (argc < 4) {
    char buffer[100];
    snprintf(buffer, 100, "Usage: %s <receiver> <subject> <message>\n",
             argv[0]);
    write(1, buffer, strlen(buffer));
    return 1;
  }
  write(1, "OLA\n", 4);
  unsigned char key_data[16] = "0123456789abcdef";
  unsigned char iv[16] = "0123456789abcdef";
  unsigned char ciphertext[512];

  Message message;
  message.receiver = argv[1];
  message.subject = argv[2];
  message.message = argv[3];
  message.timestamp = time(NULL);

  int receiver_len = strlen(argv[1]);
  int subject_len = strlen(argv[2]);
  int message_len = strlen(argv[3]);

  if (receiver_len > BLOCK_SIZE || subject_len > BLOCK_SIZE ||
      message_len > 128) {
    char buffer[100];
    snprintf(buffer, 100, "Data length exceeds block size\n");
    write(1, buffer, strlen(buffer));
    return 1;
  }

  // encryptData((unsigned char *)message.sender, sender_len, key_data, iv,
  // ciphertext);
  encryptData((unsigned char *)message.receiver, receiver_len, key_data, iv,
              ciphertext + BLOCK_SIZE);
  encryptData((unsigned char *)message.subject, subject_len, key_data, iv,
              ciphertext + BLOCK_SIZE * 2);
  encryptData((unsigned char *)message.message, message_len, key_data, iv,
              ciphertext + BLOCK_SIZE * 3);

  int fd = open("tmp/main_fifo", O_WRONLY);
  if (fd == -1) {
    perror("Error opening FIFO for writing");
    return 1;
  }

  write(fd, &message, sizeof(Message));
  write(fd, ciphertext, BLOCK_SIZE * 4);

  close(fd);
  return 0;
}
