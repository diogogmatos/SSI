#include <syslog.h>
#include <unistd.h>

int main(int argc, char const *argv[])
{   
    int i  = 0;
    while(1) {
        openlog("myDaemon", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_USER);
        syslog(LOG_INFO, " (%d) Daemon a correr...", i++);
        closelog();
        sleep(100);
    }

    return 0;
}
