# set up X environment
cp xinitrc ~/.xinitrc

# set up X font hinting and subpixel rendering
cp fonts.conf ~/.fonts.conf

# set up uzbl
mkdir -p ~/.config/uzbl

# set up uzbl
cp uzbl ~/.config/uzbl/config

# mix in our custom user CSS
cp userstyle.css ~/.config/uzbl/userstyle.css

# hide GTK scrollbars
cp gtkrc ~/.gtkrc-2.0

# sane vim defaults for remote maintenance
cp vimrc ~/.vimrc
