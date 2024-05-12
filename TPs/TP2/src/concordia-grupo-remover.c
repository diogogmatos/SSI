#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <group>\n", argv[0]);
        return 1;
    }

    char *group = argv[1];
    char* path[100];
    sprintf(path, "rm -rf concordia/%s/messages", group);
    char command[150];

    int status = system(path);
    if (status == 0) {
        printf("Group %s removed successifly.\n", group);
    } else {
        printf("Failed to remove group %s.\n", group);
    }

    return 0;
}
