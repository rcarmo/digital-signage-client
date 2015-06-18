#! /bin/sh
### BEGIN INIT INFO
# Provides:          bootsplash
# Required-Start:
# Required-Stop:
# Should-Start:      
# Default-Start:     S
# Default-Stop:      0 1 6
# Short-Description: Show boot splashscreen
# Description:       Show boot splashscreen
### END INIT INFO

# Default-Start should possibly be 2 3 4 5 because update-rc.d throws a warning

do_start () {
    # change to a new (blank) console
    chvt 3
    # get the boot animation going
    cd /tmp
    nohup /usr/bin/omxplayer -o local /home/pi/boot.mov > /dev/null 2>&1 &
    # set the background in the meantime, after the movie starts playing
    sleep 5
    /usr/bin/fbi -1 -t 60 -d /dev/fb0 -T 3 -noverbose -a /home/pi/blank.png > /dev/null 2>&1
    # use this instead if you prefer a static image
    #/usr/bin/fbi -1 -t 60 -d /dev/fb0 -T 3 -noverbose -a /home/pi/boot.png > /dev/null 2>&1
    exit 0
}

do_stop () {
    # change to a new (blank) console
    chvt 2
    # get the shutdown animation going
    cd /tmp
    nohup /usr/bin/omxplayer -o local /home/pi/down.mov > /dev/null 2>&1 &
    # use this instead if you prefer a static image
    #/usr/bin/fbi -1 -t 2 -d /dev/fb0 -T 8 -noverbose -a /home/pi/down.png > /dev/null 2>&1
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
    echo "Usage: bootsplash [start|stop]" >&2
    exit 3
    ;;
esac
