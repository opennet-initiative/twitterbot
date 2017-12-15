# Manual Installation

 * install required python libs:
   sudo aptitude install python3-feedparser python3-twython python3-html2text
 
 * configure twitter API keys
   see file config.ini

# Run Application

 * start application (foreground, once)
   python3 twitterbot.py rss

# Debian Installation

 * create DEB file
   make dist-deb

 * upload DEB file to repository
   make upload-deb

 * install DEB file from repository on host
   This includes creating a user, placing the executable, config and adding a cron job.
