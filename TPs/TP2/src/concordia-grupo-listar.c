#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MAX_COMMAND_LENGTH 200
#define MAX_OUTPUT_LENGTH 500

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <folder_path>\n", argv[0]);
        return 1;
    }

    char *folder_path = argv[1];
    char command[MAX_COMMAND_LENGTH];
    char output[MAX_OUTPUT_LENGTH];

    snprintf(command, sizeof(command), "getfacl %s", folder_path);

    FILE *pipe = popen(command, "r");
    if (pipe == NULL) {
        perror("Error opening pipe");
        return 1;
    }

    // Read the output of the command
    size_t output_length = fread(output, 1, sizeof(output), pipe);
    if (output_length == 0) {
        perror("Error reading command output");
        return 1;
    }

    output[output_length] = '\0';

    pclose(pipe);

    printf("Permissions for %s:\n%s\n", folder_path, output);

    return 0;
}
