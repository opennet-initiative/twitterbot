# Manual Installation
 * install required python libs:
   (sudo) apt install python3-feedparser python3-twython python3-html2text
 * configure twitterbot twitter API keys
   mv config.ini.template config.ini
   Insert the needed values. See below.

# Run Application
 * start application (foreground, once)
   python3 twitterbot.py rss

# Debian Installation
 * create DEB file
   make dist-deb
 * upload and install DEB file on host
   make upload-deb ..
 * or use manual installation
   cd tmp
   wget https://downloads.opennet-initiative.de/debian/on-twitterbot_<version>_all.deb
   apt -f install ./on-twitterbot_<version>_all.deb 
 * install includes creating a user, placing the executable, 
   placing an template config file and adding a cron job.
 * configure twitterbot
   cd /usr/share/on-twitterbot; mv config.ini.template config.ini
   Insert the needed values. See below.
 * application will be regulary started based on cron job

# Generate Twitter key and access token
 * goto https://apps.twitter.com/
 * use "create new app"
   Name: Twitterbot
   Description: RSS2Twitter Converter
   Website: https://www.opennet-initaitive.de
 * Store 'Comsumer Key'
 * Store 'Consumer Secret' (via tab 'Keys and Access Tokens')
 * use "create my access tocken"
 * Store 'Access Token'
 * Store 'Access Token Secret'
 * insert all data into twitterbot config.ini
