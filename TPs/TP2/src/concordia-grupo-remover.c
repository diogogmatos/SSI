#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Usage: %s <group> <folder_path>\n", argv[0]);
        return 1;
    }

    char *group = argv[1];
    char *folder_path = argv[2];

    char command[150];

    sprintf(command, "setfacl -x g:%s %s", group, folder_path);

    int status = system(command);
    
    if (status == 0) {
        printf("Permissions set successfully for %s. Access restricted for others.\n", folder_path);
    } else {
        printf("Failed to set permissions for %s.\n", folder_path);
    }

    return 0;
}
