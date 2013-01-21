SAPO DIGITAL SIGNAGE CLIENT
===========================

## IMPORTANT NOTE

> This repository currently contains sources for _the client only_, which is _broken_ - as in, it's currently being refactored but not quite in a usable state. The server code will follow in a separate repository.

This is being released as-is mostly to enable people to learn from it and use the client in standalone mode.

## STUFF YOU SHOULD BE AWARE OF

This code was developed internally at SAPO for running the [Codebits 2012](cb)
signage atop [Raspberry Pi][rpi] devices, and quickly evolved from a guerrilla 
solution into a full-blown client-server app.

This is going to be version 2.0 - version 1.0 is being used internally at SAPO 
since October 2012 and will be replaced by this (and a few custom add-ons) 
once it's finished.

Here's a brief summary of the requirements and their impact on solution design:

- clients are not supposed to store any content locally, _except_ a handful 
  of templates to render baseline content. The idea here is that you'll be 
  running this against a set of web services or a full web server that will 
  render pages to the devices.

- clients therefore run "playlists" that JSON files listing URLs to render locally.
  Playlists can contain URLs to HTML content of various descriptions or to video files,
  and support time intervals and simple "random" groups.

- communication between client and server was downgraded from websockets to an 
  HTTP(S) polling mechanism to better cope with firewalls, NAT, timeouts, etc.

- accordingly, the client runs its own HTTP server to allow for disconnected
  operation (if the central server goes down, we'll always be able to display
  _something_, and cache some information in the meantime)

- we had no idea what displays would be available, so we settled on 1280x720
  as default and 1024x768 as a fallback

- resolution is _explicitely_ set on views to make it easier to size and 
  position both HTML and SVG elements (the [Codebits][cb] layouts were extensively
  based on inline SVG, with some dimensions computed inside views).

- since we had to deal with both X and `omxplayer`, resolution is assumed to be
  set in `/boot/config.txt` as well as using `fbset` (and even then we make
  sure `uzbl` is launched with the `geometry` option to clip the rendering
  surface)



INSTALLATION
============

The following steps assume you're deploying on the [Raspberry Pi][rpi]:

* install the following packages:

    	sudo apt-get install uzbl unclutter ttf-mscorefonts-installer vim tmux \
        x11-xserver-utils git-core ntpdate ack-grep denyhosts omxplayer watchdog

* edit `/boot/config.txt` to set the framebuffer to 1280x720

* change password

* edit `/etc/rc.local` to include these lines before the final command:

        fbset --xres 1280 --yres 720
        sudo -u pi startx

This will undo any automatic detection done during the boot process and start X with our own custom session (see the `install` directory for the startup scrips). 

In stock Raspbian, it will also make it harder for someone to log in at the console (but is not a proper "fix" for that - it's just simpler than tweaking `lxsession` and whatnot).

* run `install/deploy.sh` to setup the configuration files

* **OPTIONAL**: change `sshd` to run on another port (even with `denyhosts`, it makes sense for some deployments) or block port 22 access from everywhere but the address(es) you'll be managing these from.

* **RECOMMENDED**: Disable `sshd` password authentication and add your public key to `/home/pi/.ssh/authorized_keys`.

* **OPTIONAL**: use Hexxeh's `rpi-update` to upgrade to the latest firmware and kernel (this is of debatable value, but might improve `omxplayer` stability.)

* **RECOMMENDED**: enable the [Raspberry Pi][rpi]'s hardware watchdog so that it will automatically reset the board upon freezing:

        sudo modprobe bcm2708_wdog
        sudo sh -c "echo 'bcm2708_wdog' >> /etc/modules"
        sudo apt-get install watchdog chkconfig
        sudo chkconfig watchdog on
        sudo /etc/init.d/watchdog start
        sudo sh -c "echo 'watchdog-device = /dev/watchdog' >> /etc/watchdog.conf"

* reboot

[cb]: https://codebits.eu
[rpi]: http://www.raspberrypi.org