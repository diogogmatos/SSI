#include "../includes/lib.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <folder_name>\n", argv[0]);
        return 1;
    }
    umask(000);
    char *folder_name = argv[1];

    char command[150];
    char command2[150];
    char command3[150];

    int fd = open("tmp/ad_fifo", O_WRONLY);
    if (fd == -1)
    {
        perror("[ERROR] Couldn't open AD FIFO");
        return -1;
    }

    char* username = get_username();
    char path[100];
    snprintf(path, 100, "tmp/concordia/%s", folder_name);

    int r = mkfifo(path, 0666);
    if (r == -1){
        perror("[ERROR] Couldn't create a response FIFO");
        return -1;
    }

    MESSAGE m;
    strncpy(m.sender, username, STRING_SIZE);
    strncpy(m.receiver, "server", STRING_SIZE);
    m.type = create_group;
    strncpy(m.message, folder_name, STRING_SIZE);
    m.timestamp = time(NULL);

    r = write(fd, &m, sizeof(MESSAGE));
    if ( r == -1){
        perror("[ERROR] Couldn't send message");
        return -1;
    }


    close(fd);

    fd = open(path, O_RDONLY);
    if (fd == -1)
    {
        perror("[ERROR] Couldn't open response FIFO");
        return -1;
    }

    MESSAGE response;
    int bytes_read = read(fd, &response, sizeof(MESSAGE));
    if (bytes_read == -1)
    {
        perror("[ERROR] Couldn't read response");
        return -1;
    }

    if (strcmp(response.message, "failed") == 0)
    {
        printf("[ERROR] Folder creation failed\n");
        fflush(stdout);
        return -1;
    }

    char* user = get_username();

    // Create Messages Directory
    char dir_path[100];
    snprintf(dir_path, 100, "concordia/%s/messages", folder_name);
    r = mkdir(dir_path, 0700);
    if (r == -1)
    {
        perror("[ERROR] Couldn't create sent directory");
        return -1;
    }

    sprintf(command2, "setfacl -m other::0 %s", dir_path);
    sprintf(command3, "setfacl -m u:%s:rwx %s", user, dir_path);
    
    int status2 = system(command2);
    int status3 = system(command3);

    if(status2 == 0 && status3 == 0) {
        printf("Permissions set successfully for %s. Access restricted for others.\n", dir_path);
    } else {
        printf("Failed to set permissions for %s.\n", dir_path);
    }

    return 0;
}
