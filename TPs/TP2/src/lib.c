#include <stdio.h>
#include <stdlib.h>
#include <pwd.h>
#include <unistd.h>
#include <sys/types.h>
#include <dirent.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>
#include <sys/stat.h>
#include <pwd.h>

#include "../includes/lib.h"

#define STRING_SIZE 100

typedef enum _message_type
{
    user_activate,
    user_deactivate,
    user_message,
    user_list_message,
    user_respond_message,
    create_group,
    group_remove
} MESSAGE_TYPE;

const char *message_type_str[] = {
    "user_activate",
    "user_deactivate",
    "user_message",
    "user_list_message",
    "user_respond_message",
    "create_group",
    "remove_group"
};

typedef struct _message
{
    char sender[STRING_SIZE];
    char receiver[STRING_SIZE];
    MESSAGE_TYPE type;
    char message[STRING_SIZE];
    time_t timestamp;
} MESSAGE;

char *get_username()
{
    uid_t uid = geteuid();
    struct passwd *pw = getpwuid(uid);
    if (pw)
    {
        return pw->pw_name;
    }
    return "";
}

int count_files_in_dir(char *path)
{
    // open the directory
    DIR *directory = opendir(path);
    if (directory == NULL)
    {
        perror("[ERROR] Couldn't open directory");
        return -1;
    }

    // count the files
    int file_count = 0;
    struct dirent *entry;
    while ((entry = readdir(directory)) != NULL)
    {
        file_count++;
    }

    // close the directory
    closedir(directory);

    return file_count - 2;
}

int message_to_file(int fd, MESSAGE m)
{
    int r;

    r = write(fd, m.sender, sizeof(char) * strlen(m.sender));
    r = write(fd, "|", 1);
    r = write(fd, m.receiver, sizeof(char) * strlen(m.receiver));
    r = write(fd, "|", 1);
    r = write(fd, m.message, sizeof(char) * strlen(m.message));
    r = write(fd, "|", 1);
    char timestamp[1000];
    snprintf(timestamp, 1000, "%ld", m.timestamp);
    r = write(fd, timestamp, sizeof(char) * strlen(timestamp));

    if (r == -1)
    {
        perror("[ERROR] Couldn't write message to file");
        return -1;
    }

    return 0;
}

MESSAGE str_to_message(char *str)
{
    MESSAGE m;
    struct tm tm_time;

    char *token = strtok(str, "|");
    strncpy(m.sender, token, STRING_SIZE);
    token = strtok(NULL, "|");
    strncpy(m.receiver, token, STRING_SIZE);
    token = strtok(NULL, "|");
    strncpy(m.message, token, STRING_SIZE);
    token = strtok(NULL, "|");
    m.timestamp = atoi(token);

    return m;
}

MESSAGE file_to_message(int fd)
{
    // read message info
    int r;
    char buffer[sizeof(MESSAGE) + sizeof(char) * 3];
    r = read(fd, buffer, STRING_SIZE);
    buffer[r] = '\0';

    // convert to message
    MESSAGE m = str_to_message(buffer);

    return m;
}

char *message_to_string(MESSAGE m, bool simple)
{
    char *str = malloc(sizeof(char) * 1000);

    if (simple)
    {
        snprintf(str, 1000, "sender: %s\nreceiver: %s\ntime: %s", m.sender, m.receiver, ctime(&m.timestamp));
    }
    else
    {
        snprintf(str, 1000, "sender: %s\nreceiver: %s\ntype: %s\nmessage: %s\ntime: %s", m.sender, m.receiver, message_type_str[m.type], m.message, ctime(&m.timestamp));
    }

    return str;
}

void get_file_owner(char* owner, char* path)
{
    struct stat fileStat;
    if (stat(path, &fileStat) == -1) {
        perror("Error getting file status");
        return 1;
    }

    struct passwd *ownerInfo = getpwuid(fileStat.st_uid);
    if (ownerInfo == NULL) {
        perror("Error getting owner information");
        return 1;
    }

    strcpy(owner,ownerInfo->pw_name);
}

