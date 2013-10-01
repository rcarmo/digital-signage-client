#! /bin/sh
### BEGIN INIT INFO
# Provides:          readysplash
# Required-Start:    
# Required-Stop:
# Should-Start:      
# Default-Start:     2
# Default-Stop:      0 1 6
# Short-Description: Show ready splashscreen
# Description:       Show ready splashscreen
### END INIT INFO

do_start () {
    # change to a different, blank console
    chvt 3 
    # kill any running players
    killall -9 fbi > /dev/null 2>&1 
    # set the background
    /usr/bin/fbi -1 -t 60 -d /dev/fb0 -T 3 -noverbose -a /root/blank.png > /dev/null 2>&1 &
    # play the ready animation
    cd /tmp
    killall -9 omxplayer.bin > /dev/null 2>&1 
    NOREFRESH=1 /usr/bin/omxplayer /root/ready.mov > /dev/null 2>&1 &
    # get the client going
    cd /root/digital-signage-client
    python ./app.py > /dev/null 2>&1 & 
    exit 0
}

do_stop () {
    # kill off any players (quietly)
    killall -9 uzbl > /dev/null 2>&1 &
    killall -9 python > /dev/null 2>&1 &
    exit 0
}

case "$1" in
  start|"")
    do_start
    ;;
  restart|reload|force-reload)
    echo "Error: argument '$1' not supported" >&2
    exit 3
    ;;
  stop)
    do_stop
    ;;
  status)
    exit 0
    ;;
  *)
    echo "Usage: readysplash [start|stop]" >&2
    exit 3
    ;;
esac
