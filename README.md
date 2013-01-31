SAPO DIGITAL SIGNAGE CLIENT
===========================

## UPDATE:

The client is now working in staging/debug mode, so anyone who checks out the code can get it running out of the box on their local machine.

Work is ongoing to finish refactoring the playlist/browser control engine (it's nearly done).

## IMPORTANT NOTE

> This repository currently contains sources for _the client only_, which is currently being refactored but not quite in a usable state. The server code will follow in a separate repository.

This is being released as-is mostly to enable people to learn from it and use the client in standalone mode.

## SETTING UP FOR TESTING AND DEVELOPMENT

* Clone the repo (no surprises here)
* Copy `data/config.json.dist` to `data/config.json`, making any required changes
* Run it:

    python app.py

* Go to [http://localhost:8000](http://localhost:8000) - or, if you've enabled debugging, [http://localhost:8000/debug](http://localhost:8000/debug) to see a list of all active local URLs

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

- clients therefore run "playlists", i.e. JSON files listing URLs to render locally.
  Playlists can contain URLs to HTML content of various descriptions or to video files,
  and support time intervals and simple "random" groups.

- the server can push new content to the client in near-realtime (depending on content type),
  including whole new playlists.

- communication between client and server was downgraded from websockets to an 
  HTTP(S) polling mechanism to better cope with firewalls, NAT, timeouts, etc.

- accordingly, the client runs its own HTTP server to allow for disconnected
  operation (if the central server goes down, we'll always be able to display
  _something_, and cache some information in the meantime)

- we had no idea what displays would be available, so we settled on 1280x720
  as default and 1024x768 as a fallback. 1920x1080 is possible, but you'll be stretching
  the hardware to the limits when rendering HTML locally so it's not advisable
  (plus most people can't tell the difference when you're projecting or viewing from
  afar).

- resolution is _explicitely_ set on views to make it easier to size and 
  position both HTML and SVG elements (the [Codebits][cb] layouts were extensively
  based on inline SVG, with some dimensions computed inside views).

- since we had to deal with both X and `omxplayer`, resolution is assumed to be
  set in `/boot/config.txt` as well as using `fbset` (and even then we make
  sure `uzbl` is launched with the `geometry` option to clip the rendering
  surface)


## INSTALLATION

The following steps assume you're deploying on the [Raspberry Pi][rpi] as the `pi` user.

* Checkout the repository
* Clone the repo (no surprises here)
* Copy `data/config.json.dist` to `data/config.json`, making any required changes
* install the following packages:

    	sudo apt-get install uzbl unclutter ttf-mscorefonts-installer vim tmux \
        x11-xserver-utils git-core ntpdate ack-grep denyhosts omxplayer watchdog

* edit `/boot/config.txt` to set the framebuffer to 1280x720
* edit `/etc/rc.local` to include these lines before the final command:

        fbset --xres 1280 --yres 720
        sudo -u pi startx

This will undo any automatic detection done during the boot process and start X with our own custom session (see the `install` directory for the startup scrips). 

In stock Raspbian, it will also make it harder for someone to log in at the console (but is not a proper "fix" for that - it's just simpler than tweaking `lxsession` and whatnot).

* run `install/deploy.sh` to setup the configuration files

* **OPTIONAL**: change `sshd` to run on another port (even with `denyhosts`, it makes sense for some deployments) or block port 22 access from everywhere but the address(es) you'll be managing these from.

* **RECOMMENDED:** change the password for the `pi` user.

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

## FURTHER READING

[The original blog post][b1], wherein you'll find some screenshots of the server.

A few photos of this in action: [1](http://fotos.sapo.pt/ndantas/fotos/?uid=HrC41nF3vZfkMA16utoZ), [2](http://fotos.sapo.pt/ndantas/fotos/?uid=9zWgzUQMIwp9NkfMSq1i), [3](http://fotos.sapo.pt/ndantas/fotos/?uid=7ZZZgiyiUhmarZbCzM6p), [4](http://fotos.sapo.pt/ndantas/fotos/?uid=QB91ymIZmvByPuKQ1rwj), [5](http://fotos.sapo.pt/ndantas/fotos/?uid=9zWgzUQMIwp9NkfMSq1i), [6](http://fotos.sapo.pt/rcarmo/fotos/?uid=iznSQ4TuNFKtcpNBdQWS).

## LICENSING

[SAPO](http://www.sapo.pt) has a [strong Open-Source culture](http://oss.sapo.pt) and believes in placing credit where credit is due.

* This entire codebase is [MIT licensed](LICENSE), and therefore free to use as you please for commercial or non-commercial purposes.
* Sample GIF images are [CC Licensed](http://creativecommons.org/licenses/by-sa/3.0/) from [Wikimedia Commons](http://commons.wikimedia.org).
* The [Roboto Font](http://developer.android.com/design/style/typography.html) is bundled as a convenience (and because it's eminently suited to digital signage) under the [Apache License](http://www.apache.org/licenses/LICENSE-2.0.html).
* The [SAPO](http://www.sapo.pt) logo is a registered trademark of [Portugal Telecom](http://www.telecom.pt). It is included as a default part of this software's branding screen and cannot be reused for any other purpose.

As common courtesy, we ask you to preserve (and contribute to) source code comments, attributions and this `README` if you decide to fork, deploy or otherwise redistribute this software.

[cb]: https://codebits.eu
[rpi]: http://www.raspberrypi.org
[b1]: https://codebits.eu/s/blog/c89f80ca02910f48ac4cede8c3ce5cd7