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

# Default-Start should possibly be 2 3 4 5 because update-rc.d throws a warning

do_start () {
    # change to a different, blank console
    chvt 3 
    # play the ready animation
    cd /tmp
    
    # move .local to tmp
    rm -rf /tmp/.local
    rm -rf /home/pi/.local
    mkdir /tmp/.local
    ln -s /tmp/.local /home/pi/.local

    killall -9 omxplayer.bin > /dev/null 2>&1 
    NOREFRESH=1 /usr/bin/omxplayer /home/pi/ready.mov > /dev/null 2>&1 &
    sleep 5
    # set background
    /usr/bin/fbi -1 -t 60 -d /dev/fb0 -T 3 -noverbose -a /home/pi/blank.png > /dev/null 2>&1 &
    # get the client going indirectly via starting X
    sleep 1
    fbset -xres 1280 -yres 720
    # won't cd to /root otherwise, and won't run .xinitrc there
    sudo -u root startx &
    # a chvt may be needed here: need to ctrl-alt-f1 manually
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
