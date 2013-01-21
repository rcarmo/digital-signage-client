# set up X environment
cp xinitrc ~/.xinitrc

# set up uzbl
mkdir -p ~/.config/uzbl

# configuration
cp uzbl ~/.config/uzbl/config

# custom CSS
cp userstyle.css ~/.config/uzbl/userstyle.css

# hide GTK scrollbars
cp gtkrc ~/.gtkrc-2.0

# sane vim defaults for remote maintenance
cp vimrc ~/.vimrc
