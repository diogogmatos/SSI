#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <folder_path>\n", argv[0]);
        return 1;
    }

    char *folder_path = argv[1];

    char command[150];
    char command2[150];

    sprintf(command, "setfacl -Rm g:concordia:rwx %s", folder_path);
    sprintf(command2, "setfacl -m other::0 %s", folder_path);

    
    int status = system(command);
    int status2 = system(command2);
    
    if(status == 0 && status2 == 0) {
        printf("Permissions set successfully for %s. Access restricted for others.\n", folder_path);
    } else {
        printf("Failed to set permissions for %s.\n", folder_path);
    }

    return 0;
}
