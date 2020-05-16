#! /usr/bin/python3
import os
import traceback
from time import sleep, time

import praw
from notifiers import get_notifier

# Globals
NEW_POSTS_LIMIT = 10
ITEM_MATCH = ["[CPU]", "[MONITOR]"]

# Credentials file for praw reddit api and pushbullet to send notificaion to android
CWD = os.getcwd() + '/workspace/'
pushbullet_credentials_file = os.path.join(CWD, 'pushbullet_credentials')
praw_credentials_file = os.path.join(CWD, 'praw_credentials')

# Read credentials file and convert to a dict with key-value pairs
pushbullet_credentials = {}  # contains token
praw_credentials = {}  # contains client_id, client_secret, user_agent
for cred_file, cred_dict in zip([pushbullet_credentials_file, praw_credentials_file], [pushbullet_credentials, praw_credentials]):
    with open(cred_file, 'r') as myfile:
        for line in myfile:
            key, value = line.partition("=")[::2]
            cred_dict[key.strip()] = value.strip()

# Initialize praw-reddit instance
# Initialize notifier instance
pushbullet_notifier = get_notifier('pushbullet')
reddit = praw.Reddit(**praw_credentials)

# Define the subreddit to read notifications from
# Read only new posts
subreddit = reddit.subreddit('bapcsalescanada')

# Loop through all the new posts and look for predefined text
# If exists, create a list of such posts and send notification to pushbullet
my_items = {'timestamp': None, 'items': {}}
prev_timestamp = None
try:
    while True:
        subreddit_posts_new = subreddit.new(limit=NEW_POSTS_LIMIT)
        prev_timestamp = my_items['timestamp']
        for posts_obj in subreddit_posts_new:
            if not posts_obj.stickied and any(x in posts_obj.title.upper() for x in ITEM_MATCH):
                if posts_obj not in my_items['items']:
                    print(f"Adding postobj: [{posts_obj}]")
                    my_items['items'][posts_obj] = f"Title: {posts_obj.title}\nURL: {posts_obj.url}\n{'*'*30}\n"
                    my_items['timestamp'] = time()
                    print(f"Updating timestamp to [{my_items['timestamp']}]")
                else:
                    print(f"Post object [{posts_obj}] is already in list")

        if prev_timestamp != my_items['timestamp']:  # new entry in item list
            print("New timestamp!!!")
            pushbullet_notifier.notify(message=''.join(my_items['items'].values()), **pushbullet_credentials)

        sleep(60)
except Exception as e:
    print("Exception occured.")
    print(traceback.format_exc())
