#include <syslog.h>
#include <stdio.h>

int main() {
    openlog("myapp", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_USER);
    setlogmask(LOG_UPTO(LOG_NOTICE)); 

    syslog(LOG_EMERG, "Log de Emergência");
    syslog(LOG_ALERT, "Log de Alerta");
    syslog(LOG_CRIT, "Log Crítico");

    syslog(LOG_MAKEPRI(LOG_DAEMON | LOG_AUTH, LOG_INFO), "Mensagem combinada: DAEMON e AUTH");

    closelog();

    return 0;
}