#! /bin/sh
### BEGIN INIT INFO
# Provides:     ${name}-python-supervisor
# Required-Start:   $syslog
# Required-Stop:    $syslog
# Should-Start:     $local_fs
# Should-Stop:      $local_fs
# Default-Start:    2 3 4 5
# Default-Stop:     0 1 6
# Short-Description:    ${name}-python-supervisor
# Description:      ${name}-python-supervisor
### END INIT INFO
#
# Simple init.d script conceived to work on Linux systems
# as it does use of the /proc filesystem.

NAME=${name}
ENV=/server/www/$NAME/${env}
USER=www-data
PIDFILE=$ENV/run/supervisord.pid


case "$1" in
    start)
        if [ -f $PIDFILE ]
        then
                echo "$PIDFILE exists, process is already running or crashed"
        else
                echo "Starting $NAME server..."
                sudo -u $USER HOME=$(eval echo ~$USER) $ENV/env/bin/supervisord -c $ENV/supervisor.cfg
        fi
        ;;
    stop)
        if [ ! -f $PIDFILE ]
        then
                echo "$PIDFILE does not exist, process is not running"
        else
                echo "Stopping ..."
                $ENV/env/bin/supervisorctl -c $ENV/supervisor.cfg shutdown
                while [ -x /proc/$PIDFILE ]
                do
                    echo "Waiting for python to shutdown ..."
                    sleep 1
                done
                echo "$NAME stopped"
        fi
        ;;
    *)
        echo "Please use start or stop as first argument"
        ;;
esac
