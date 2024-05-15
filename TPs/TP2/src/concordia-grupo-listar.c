#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MAX_COMMAND_LENGTH 200
#define MAX_OUTPUT_LENGTH 500

void filterUsers(const char *data) {
    char *line;
    char *copy = strdup(data); 
    if (copy == NULL) {
        perror("Memory allocation failed");
        return;
    }

    line = strtok(copy, "\n");
    for(int i = 0; line != NULL; i) {
        if (strncmp(line, "user", 4) == 0 ) {
            i++;
            if( i > 1) {
                printf("%d - %s\n", i - 1, line + 5); 
            }

        }
        line = strtok(NULL, "\n");
    }

    free(copy);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <group_name>\n", argv[0]);
        return 1;
    }

    char group_path[100];
    snprintf(group_path, 100, "concordia/g-%s/messages", argv[1]);
    char command[MAX_COMMAND_LENGTH];
    char output[MAX_OUTPUT_LENGTH];

    snprintf(command, sizeof(command), "getfacl %s", group_path);

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

    printf("Users with acesse for %s:\n", group_path);
    filterUsers(output);

    return 0;
}
