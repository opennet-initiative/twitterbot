#
# cron-jobs for on-twitterbot
#

MAILTO=root

# export new Opennet Blog entries to Opennet twitter
*/10 *	* * *	on-twitterbot	/usr/share/on-twitterbot/on-twitterbot.py rss >/dev/null
