# Standard imports
import os
import traceback
import logging
from time import sleep, time

# 3rd party imports
import praw
from notifiers import get_notifier

# Globals
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PUSHBULLET_CRED_FILE = os.path.join(DIR_PATH, 'pushbullet_credentials')
PUSHBULLET_CRED_DICT = {}
PRAW_CRED_FILE = os.path.join(DIR_PATH, 'praw_credentials')
PRAW_CRED_DICT = {}

# Initializers
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")
map(read_credentials, zip([PUSHBULLET_CRED_FILE, PRAW_CRED_FILE], [PUSHBULLET_CRED_DICT, PRAW_CRED_DICT]))
logging.debug(f"[INFO] - Pushbullet creds: {PUSHBULLET_CRED_DICT}")
logging.debug(f"[INFO] - Praw creds: {PRAW_CRED_DICT}")
pushbullet_notifier = get_notifier('pushbullet')
reddit = praw.Reddit(**PRAW_CRED_DICT)

# Constants
NEW_POSTS_LIMIT = 10
ITEM_MATCH = ["[CPU", "[MONITOR", '[MOTHERBOARD', '[MOBO', '[GPU']

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


# Define the subreddit to read notifications from
# Read only new posts
subreddit = reddit.subreddit('bapcsalescanada')

# Loop through all the new posts and look for predefined text
# If exists, create a list of such posts and send notification to pushbullet
my_items = {'timestamp': None, 'items': {}}
prev_timestamp = None


def read_credentials(cred_file, cred_dict):
    """
    Read the credentials from file and save it in the dictionary

    Arguments:
        cred_file {path} -- OS path to the cred file location
        cred_dict {dict} -- Dictionary that will save the credentials

    Returns:
        dict -- Returns dict with 'token' as keyname and token value
    """
    logging.debug(f"Cred file: {cred_file}, Cred_dict: {cred_dict}")
    with open(cred_file, 'r') as f:
        for line in f:
            key, value = line.partition("=")[::2]
            cred_dict[key.strip()] = value.strip()


def main():
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


if __name__:
    '__main__':
    main()
