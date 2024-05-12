#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Usage: %s <user> <group>\n", argv[0], argv[1]);
        return 1;
    }

    char command[150];
    char *user = argv[1];
    char *group = argv[2];
    char path[100];

    sprintf(path, "concordia/%s", group);
    
    sprintf(command, "setfacl -R -m u:%s:rwx %s", user, path);

    int status = system(command);

    if (status == 0) {
        printf("Permissions set successfully for %s. Access restricted for others.\n", path);
    } else {
        printf("Failed to set permissions for %s.\n", path);
    }

    return 0;
}
