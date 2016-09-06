RASPBERRY PI DIGITAL SIGNAGE CLIENT
===========================

## PROJECT STATUS (SEPTEMBER 2016):

This repository is an attempt to clean up and merge assorted patches to the original project, as well as taking back ownership (after all, it was originally developed by myself at SAPO).

Back in 2014, this was discontinued in favor of [an Android-based solution][an] due to the lack of accelerated web page rendering on the [Raspberry Pi][rpi].

However, it is still useful for "tactical" enhancements, since it's still very easy to use and deploy for relatively static displays.

Over the years, however, a number of changes have taken place in core components, so this repository may not actually work on Raspbpian/Minibian 8 - your mileage may vary.

## UPDATE (OCT 1ST 2013):

In an attempt to go for an even smaller footprint, we've switched from [Raspbian][rp] to [Moebius][mb] 1.1.1. 

[Moebius][mb] is significantly smaller (it's aimed at embedded deployments) and assumes no desktop environment is installed (it doesn't even ship with X11), so it makes a lot more sense for digital signage.


## SETTING UP FOR TESTING AND DEVELOPMENT

* Clone the repo (no surprises here)
* Copy `etc/config.json.dist` to `etc/config.json`, making any required changes
* Run it:

        python app.py

* Go to [http://localhost:8000](http://localhost:8000) - or, if you've enabled debugging, [http://localhost:8000/debug](http://localhost:8000/debug) to see a list of all active local URLs

## STUFF YOU SHOULD BE AWARE OF

This code was developed internally at SAPO for running the [Codebits 2012](cb)
signage atop [Raspberry Pi][rpi] devices, and quickly evolved from a guerrilla 
solution into a full-blown client-server app.

This is version 2.0 - version 1.0 was used internally at SAPO since October 2012, and 2.0 was deployed mid-2013 before we switched to a simpler video-only solution based on [MEO Kanal](http://kanal.pt) also using [Raspberry Pi][rpi] hardware.

Here's a brief summary of the original requirements and their impact on solution design:

- clients were not supposed to store any content locally, _except_ a handful 
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

The following steps assume you're deploying on the [Raspberry Pi][rpi] as the `root` user and starting from a clean [Moebius][mb] install.

* Bring your image up to date and install required packages (some of these are only required for development and testing, but they add little to the overall footprint):

        sudo apt-get update
        sudo apt-get dist-upgrade
        sudo apt-get install ack-grep bash-completion chkconfig denyhosts \
        fbi git-core htop ntpdate omxplayer python-pygments tmux \
        ttf-mscorefonts-installer unclutter uzbl vim watchdog x11-xserver-utils \
        xinit xserver-xorg-video-fbturbo

* Edit `/boot/config.txt` (`moebius.config` will take you there if you choose `Internals`) to set the framebuffer to 1280x720 by uncommenting these two lines:

        # uncomment to force a console size. By default it will be display's size minus
        # overscan.
        framebuffer_width=1280
        framebuffer_height=720

This will undo any automatic detection done during the boot process and significantly boost browser performance (full HD is nice, but it is also very slow without proper GPU support).

* Still in `/boot/config.txt`, set the GPU memory to 64MB to allow GPU video decoding to work:

        # Set variable gpu_mem
        gpu_mem=64

* Change `/boot/cmdline.txt` to disable the boot logo, move the boot VT to `tty9`, disable the cursor and automatically blank the console:

        dwc_otg.lpm_enable=0 console=ttyAMA0,115200 kgdboc=ttyAMA0,115200 console=tty9 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait logo.nologo loglevel=3 quiet vt.global_cursor_default=0 vt.handoff=7 consoleblank=1

## Setting up the client

* Clone the repo to `/root` (no surprises here):

        cd /root
        git clone https://github.com/sapo/digital-signage-client.git
        cd digital-signage-client

* Copy `etc/config.json.dist` to `etc/config.json`, making any required changes
* Run `install/deploy.sh` to setup the configuration files and startup scripts
 
* **RECOMMENDED**: Check the startup scripts and add corresponding video and image files for your splash screen (if any).

* **RECOMMENDED**: use Hexxeh's [rpi-update](https://github.com/Hexxeh/rpi-update) to upgrade to the latest firmware and kernel

* **RECOMMENDED**: run `sudo dpkg-reconfigure tzdata` and choose your timezone 

* **RECOMMENDED**: enable the [Raspberry Pi][rpi]'s hardware watchdog so that it will automatically reset the board upon freezing:

        sudo modprobe bcm2708_wdog
        sudo sh -c "echo 'bcm2708_wdog' >> /etc/modules"
        sudo apt-get install watchdog chkconfig
        sudo sh -c "echo 'watchdog-device = /dev/watchdog' >> /etc/watchdog.conf"
        sudo chkconfig watchdog on
        sudo /etc/init.d/watchdog restart

* Add the following lines to `/etc/default/rcS` to disable swap and enable `tmpfs`

        RAMTMP=yes
        NOSWAP=yes

* Add the following lines to `/etc/fstab`:

        tmpfs           /tmp            tmpfs   nodev,nosuid,size=16M,mode=1777    0    0
        tmpfs           /var/log        tmpfs   nodev,nosuid,size=16M,mode=1777    0    0

* reboot

## MEDIA ASSETS 

The startup scripts assume you have four media assets in `/root`:

* `boot.mov` is a 20s long, 12fps boot animation
* `down.mov` is a 20s long, 12fps shutdown animation
* `ready.mov` is an arbitrary "welcome" video
* `blank.png` is a 1280x720 PNG that acts as an "intermission" image

The 12fps framerate was chosen beause it yields <10MB files at 1280x720 resolution, and you can change the startup scripts to use static images instead.

## SECURITY CONSIDERATIONS

[Moebius][mb] differs from [Raspbian][rp] in not providing a `pi` user. Given that a signage client does not provide any services (even though it is physically exposed and thus essentially compromisable from the moment you deploy it), running everything as `root` doesn't pose any significant extra risks and significantly simplifies matters.

However, the following are basic security precautions you should follow:

* **RECOMMENDED:** change the `root` user password (it's `raspi` in the default [Moebius][mb] setup, in case you're wondering).

* **RECOMMENDED**: Disable `sshd` password authentication for the root login in `dropbear`.

* **RECOMMENDED**: Set up SSH access and add your public key to `/home/home/pi/.ssh/authorized_keys` for remote maintenance.

* **OPTIONAL**: change `sshd` to run on another port (even with `denyhosts`, it makes sense for some deployments) or block port 22 access from everywhere but the address(es) you'll be managing these from.

## SD CARD IMAGES

Due to popular demand, I have to state that there are none publicly available yet. Still, if there were, they'd be sized for a 4GB SD card (purely out of cost considerations) and could be created by doing something like:

        # a 4GB image has 3904897024 bytes, and we can write it via rdisk devices faster on OS X
        sudo dd of=/dev/rdisk2 if=~/Desktop/signage.raw.img bs=4m count=931

## ON LOGGING

Note that the app has built-in support for diagnostics logging (which is kept in RAM and can be sent back to the server if so desired). This is set up as the `ram` logger in `config.json.dist`.

This can be very helpful in debugging the system remotely, but will not capture tracebacks _as is_ (pull requests towards contributing that functionality are welcome).


## FURTHER READING

[The original blog post][b1], wherein you'll find some screenshots of the server.

A few photos of this in action: [1](http://fotos.sapo.pt/ndantas/fotos/?uid=HrC41nF3vZfkMA16utoZ), [2](http://fotos.sapo.pt/ndantas/fotos/?uid=9zWgzUQMIwp9NkfMSq1i), [3](http://fotos.sapo.pt/ndantas/fotos/?uid=7ZZZgiyiUhmarZbCzM6p), [4](http://fotos.sapo.pt/ndantas/fotos/?uid=QB91ymIZmvByPuKQ1rwj), [5](http://fotos.sapo.pt/ndantas/fotos/?uid=9zWgzUQMIwp9NkfMSq1i), [6](http://fotos.sapo.pt/rcarmo/fotos/?uid=iznSQ4TuNFKtcpNBdQWS).

## LICENSING

[SAPO](http://www.sapo.pt) has a [strong Open-Source culture](http://oss.sapo.pt) and believes in placing credit where credit is due.

* This entire codebase is [MIT licensed](LICENSE), and therefore free to use as you please for commercial or non-commercial purposes.
* Sample GIF images are [CC Licensed](http://creativecommons.org/licenses/by-sa/3.0/) from [Wikimedia Commons](http://commons.wikimedia.org).
* The [Roboto Font](http://developer.android.com/design/style/typography.html) is bundled as a convenience (and because it's eminently suited to digital signage) under the [Apache License](static/fonts/COPYING.txt).
* The [SAPO](http://www.sapo.pt) logo is a registered trademark of [Portugal Telecom](http://www.telecom.pt). It is included as a default part of this software's branding screen and cannot be reused for any other purpose.

As common courtesy, we ask you to preserve (and contribute to) source code comments, attributions and this `README` if you decide to fork, deploy or otherwise redistribute this software.

[an]: https://github.com/sapo/android-signage-client
[cb]: https://codebits.eu
[rpi]: http://www.raspberrypi.org
[b1]: https://codebits.eu/s/blog/c89f80ca02910f48ac4cede8c3ce5cd7
[rp]: http://www.raspbian.org
[mb]: http://moebiuslinux.sourceforge.net
