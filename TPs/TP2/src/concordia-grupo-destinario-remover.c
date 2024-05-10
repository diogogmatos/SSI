#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <user> <folder_path>\n", argv[0], argv[1]);
        return 1;
    }

    char command[150];
    char *user = argv[1];
    char *folder_path = argv[2];
    
    sprintf(command, "setfacl -x u:%s %s", user, folder_path);

    int status = system(command);

    if (status == 0) {
        printf("Permissions removed successfully for %s. Access restricted for others.\n", user);
    } else {
        printf("Failed to remove permissions for %s.\n", user);
    }

    return 0;
}
