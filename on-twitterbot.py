#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Get RSS feed items from http://example.net/feed/ and post tweets to @youraccount.
# By Peter M. Dahlgren, @peterdalle

# adopted by Opennet Initiative e.V. - https://www.opennet-initiative.de/
# Martin Garbe <monomartin@opennet-initiative.de> 
# Mathias Mahnke <ap27@opennet-initiative.de>
# last update 2017/12/18

from twython import Twython, TwythonError
import csv
import sys
import os
import re
import time
import datetime
import feedparser
from datetime import date
import html2text
import configparser

# Read settings
def getConfigValue(key):
	config = configparser.ConfigParser(interpolation=None)
	try:
		config.read("/etc/on-twitterbot.conf")
		configDict = {
			"FeedUrl": config['Settings']['FeedUrl'],
			"TweetStart": config['Settings']['TweetStart'],
			"TweetEnd": config['Settings']['TweetEnd'],
			"PostedUrlsOutputFile": config['Settings']['PostedUrlsOutputFile'],
			"PostedRetweetsOutputFile": config['Settings']['PostedRetweetsOutputFile'],
			"ConsumerKey": config['TwitterAuth']['ConsumerKey'],
			"ConsumerSecret": config['TwitterAuth']['ConsumerSecret'],
			"AccessToken": config['TwitterAuth']['AccessToken'],
			"AccessTokenSecret": config['TwitterAuth']['AccessTokenSecret']
		}
		return configDict.get(key)
	except KeyError as e:
		print("Error: Cannot read key '"+key+"' from file 'config.ini'", file=sys.stderr)

# Post tweet to account.
def PostTweet(title, link):
	# Truncate title and append ... at the end if length exceeds 113 chars.
	title = (title[:113] + '...') if len(title) > 113 else title
	message = title + " " + link
	try:
		# Tweet message.
		twitter = Twython(getConfigValue("ConsumerKey"), getConfigValue("ConsumerSecret"),
			getConfigValue("AccessToken"), getConfigValue("AccessTokenSecret")) 
		# Connect to Twitter.
		twitter.update_status(status = message)
	except TwythonError as e:
		print(e, file=sys.stderr)

# Read RSS and post tweet.
def ReadRssAndTweet(url):
	feed = feedparser.parse(url)
	for item in feed["items"]:
		title = item["title"]
		link = item["link"]
		desc = item["description"]
		h = html2text.HTML2Text()
		h.ignore_links = True #do not post inline links
		text = Opennet h.handle(desc)
		# do Opennet magic...
    text = CleanupTextOpennet(text)
		# add start / end to tweet text
		text = getConfigValue("TweetStart") + " " + text + " " + getConfigValue("TweetEnd")
		#print(text) #for DEBUG
		# Make sure we don't post any duplicates.
		if not (IsUrlAlreadyPosted(link)):
			PostTweet(text, link)
			MarkUrlAsPosted(link)
			print("Posted: " + link)
		else:
			print("Already posted: " + link)

# Clean up text, Opennet specific
def CleanupTextOpennet(text):
  # remove table of contents
  text = text.replace("## Inhaltsverzeichnis","")
  # remove empty lines (even with CR)
  text = re.sub(r'\n(\s)+', r'\n', text, flags=re.MULTILINE)
  # remove headings
  # before:  "###  Montagstreffen (24.07.2017)"
  # after: "Montagstreffen (24.07.2017)"
  text = re.sub(r'^##+  ', r'', text, flags=re.MULTILINE)
  # remove numbering
  # before:  "  * [1 Montagstreffen (13.11.2017)]"
  # atfer: "[1 Montagstreffen (13.11.2017)]""
  text = re.sub(r'^ +\*\s\[', r'[', text, flags=re.MULTILINE)
  # remove lists
  # before:  "* 1 Montagstreffen (13.11.2017)"
  # before:  " * 1.1 Borwinschule"
  # after: "1 Montagstreffen (13.11.2017)"
  # after: "1.1 Borwinschule"
  text = re.sub(r'^ *\*\s(\d)', r'\1', text, flags=re.MULTILINE)
  # remove initial spaces
  # before:  "  * letzte Verfeinerungen"
  # after: "* letzte Verfeinerungen"
  text = re.sub(r'^  \* ', r'* ', text, flags=re.MULTILINE)
  # remove (other) empty lines
  text = text.replace("\n\n","\n")
  ''' TODO
  #suche erstes Bild aus Text
  #z.B. "(https://wiki.opennet-initiative.de/wiki/Datei:Oni-usb-rs232.jpg)"
  search_resultsphoto = open('/path/to/file/image.jpg', 'rb')
  response = twitter.upload_media(media=photo)
  twitter.update_status(status='Checkout this cool image!', media_ids=[response['media_id']])
  '''
	return(text)	

# Has the URL already been posted?
def IsUrlAlreadyPosted(url):
	if os.path.isfile(getConfigValue("PostedUrlsOutputFile")):
		# Check whether URL is in log file.
		f = open(getConfigValue("PostedUrlsOutputFile"))
		posted_urls = f.readlines()
		f.close()
		if (url + "\n" or url) in posted_urls:
			return(True)
		else:
			return(False)
	else:
		return(False)

# Mark the specific URL as already posted.
def MarkUrlAsPosted(url):
	try:
		# Write URL to log file.
		f = open(getConfigValue("PostedUrlsOutputFile"), "a")
		f.write(url + "\n")
		f.close()
	except:
		print("Write error:", sys.exc_info()[0])

# Search for particular keywords in tweets and retweet those tweets.
def SearchAndRetweet():
	exclude_words = [] 		# Do not include tweets with these words.
	include_words = ["#hashtag"]	# Include tweets with these words.

	# Create Twitter search query with included words minus the excluded words.
	filter = " OR ".join(include_words)
	blacklist = " -".join(exclude_words)
	keywords = filter + blacklist

	# Connect to Twitter.
	twitter = Twython(getConfigValue("ConsumerKey"), getConfigValue("ConsumerSecret"),
		getConfigValue("AccessToken"), getConfigValue("AccessTokenSecret"))
	search_results = twitter.search(q=keywords, count=10)
	try:
		for tweet in search_results["statuses"]:
			# Make sure we don't retweet any dubplicates.
			if not IsTweetAlreadyRetweeted(tweet["id_str"]):
				try:
					twitter.retweet(id = tweet["id_str"])
					MarkTweetAsRetweeted(tweet["id_str"])
					print("Retweeted " + tweet["text"].encode("utf-8") + " (tweetid " + str(tweet["id_str"]) + ")")
				except TwythonError as e:
					print(e, file=sys.stderr)
			else:
				print("Already retweeted " + tweet["text"].encode("utf-8") + " (tweetid " + str(tweet["id_str"]) + ")")
	except TwythonError as e:
		print(e, file=sys.stderr)

# Has the tweet already been retweeted?
def IsTweetAlreadyRetweeted(tweetid):
	if os.path.isfile(getConfigValue("getPostedRetweetsOutputFile")):
		# Check whether tweet IDs is in log file.
		f = open(getConfigValue("PostedRetweetsOutputFile"))
		posted_tweets = f.readlines()
		f.close()
		if (tweetid + "\n" or tweetid) in posted_tweets:
			return(True)
		else:
			return(False)
	else:
		return(False)

# Mark the specific tweet as already retweeted.
def MarkTweetAsRetweeted(tweetid):
	try:
		# Write tweet ID to log file.
		f = open(getConfigValue("PostedRetweetsOutputFile"), "a")
		f.write(tweetid + "\n")
		f.close()
	except:
		print("Write error:", sys.exc_info()[0])

# Show available commands.
def DisplayHelp():
	print("Syntax: python twitterbot.py [cmd]")
	print
	print(" Available commands:")
	print("    rss    Read URL and post new items to Twitter account (change account in source code)")
	print("    rt     Search and retweet keywords (see source code for keywords)")
	print("    help   Show this help screen")
	print

# Main.
if (__name__ == "__main__"):
	if len(sys.argv) > 1:
		cmd = sys.argv[1]
		if (cmd == "rss"):
			ReadRssAndTweet(getConfigValue("FeedUrl"))
		elif (cmd == "rt"):
			#SearchAndRetweet()
			print("Retweet feature deactivated!")
		else:
			DisplayHelp()
	else:
		DisplayHelp()
		sys.exit()
