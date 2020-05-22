from os import path,stat,environ,makedirs
from shutil import copy2
import tweepy
from subprocess import call
import argparse
import ConfigParser

#twitter account password Fr35hPr1nc3
THIS_DIR = path.dirname(__file__)
ORIGINAL_DIR = 'files/original/'
LIVE_DIR = 'files/live/'

ORIGINAL_FILE = ''
LIVE_FILE = ''

def file_exists(file):
	return path.isfile(file)

def file_is_empty(file):
	return stat(file).st_size < 2

def new_file_please(filename):
	"""Create the live file from the original if it doesn't exist or it's empty"""
	global THIS_DIR
	global LIVE_DIR
	global LIVE_FILE
	global ORIGINAL_FILE

	ORIGINAL_FILE = path.join(THIS_DIR, ORIGINAL_DIR, filename)
	LIVE_FILE = path.join(THIS_DIR, LIVE_DIR, filename)

	# create the directory for live files, if it doesn't exist
	if not path.exists(LIVE_DIR):
		makedirs(LIVE_DIR)

	# create the live file from the original if it doesn't exist
	if not path.isfile(LIVE_FILE):
		copy2(ORIGINAL_FILE, LIVE_FILE)

	# if the file is empty, replace it with the original file
	if stat(LIVE_FILE).st_size < 2:
		copy2(ORIGINAL_FILE, LIVE_FILE)

def authenticate(consumer_key, consumer_secret, access_token, access_token_secret):
	"""Oauth process for twitter"""

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	return auth

def send_tweet(account, text):
	"""Connect to the Twitter API and send the tweet"""

	# Create the interface with the twitter API, using the auth info
	api = tweepy.API(account)

	# send the tweet
	api.update_status(text)

def remove_first_line():
	"""
	remove the line just tweeted from the file, have to do this using tail,
	because doing this in pythonmeans storing the contents in memory.This method
	writes line 2 and onwards to the file
	"""
	cmd = 'echo "$(tail -n +2 %s)" > %s' % (LIVE_FILE, LIVE_FILE)
	call(cmd, shell=True)

def read_config(filepath):
	config_file = '%s/%s' % (THIS_DIR, filepath)
	parser = ConfigParser.ConfigParser()
	parser.read(config_file)
	return parser

def __main__():
	parser = argparse.ArgumentParser()
	parser.add_argument("--config")
	args = parser.parse_args()

	config = read_config(args.config)

	consumer_key = config.get('default', 'CONSUMER_KEY')
	consumer_secret = config.get('default', 'CONSUMER_SECRET')
	access_token = config.get('default', 'ACCESS_TOKEN')
	access_token_secret = config.get('default', 'ACCESS_TOKEN_SECRET')
	filename = config.get('default', 'FILENAME')

	# prep the new file
	new_file_please(filename)

	# extract the first line from the file
	line = open(LIVE_FILE).readline()

	# authenticate with the API
	account = authenticate(consumer_key, consumer_secret, access_token, access_token_secret)

	# send the tweet!
	send_tweet(account, line)

	# remove the line just tweeted from the file
	remove_first_line()

if __name__ == '__main__':
	__main__()
