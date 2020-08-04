# Standard imports
import os
import traceback
import logging
import json
from time import sleep, strftime, localtime, time

# 3rd party imports
import praw
from notifiers import get_notifier

""" LOGGING DETAILS """
# Logging settings for current module
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
os.makedirs(os.path.join(DIR_PATH, "logs"), exist_ok=True)
# Create custom logger
# Put logger to lowest level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Create handlers
sh = logging.StreamHandler()
fh = logging.FileHandler(os.path.join(DIR_PATH, "logs", "printlogs.log"), 'a')
# Set individual debugging level for handlers
sh.setLevel(logging.INFO)
fh.setLevel(logging.DEBUG)
# Create formatter
sh_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
fh_formatter = logging.Formatter("%(asctime)s - %(process)d - %(module)s - %(levelname)s: %(message)s")
# Set formatter
sh.setFormatter(sh_formatter)
fh.setFormatter(fh_formatter)
# Add handlers to the logger
logger.addHandler(sh)
logger.addHandler(fh)
""" ---------  """
# Globals
PUSHBULLET_CRED_FILE = os.path.join(DIR_PATH, 'pushbullet_credentials')
PUSHBULLET_CRED_DICT = {}
PRAW_CRED_FILE = os.path.join(DIR_PATH, 'praw_credentials')
PRAW_CRED_DICT = {}
SUBREDDIT = 'bapcsalescanada'

# Constants
WAIT_TIME = 2  # minute
MAX_POSTS_LIMIT = 10
ITEM_MATCH = ["[CPU", "[MONITOR", '[MOTHERBOARD', '[MOBO', '[GPU', '[SSD']


def read_credentials(cred_items):
    """
    Read the credentials from the file and save it in the dictionary

    Arguments:
        cred_items {tuple} -- Tuple containing credentials file and dict to save result
    """
    cred_file, cred_dict = cred_items
    with open(cred_file, 'r') as f:
        for line in f:
            key, value = line.partition("=")[::2]
            cred_dict[key.strip()] = value.strip()


def main():
    # Save credentials for praw and pushbullet in respective dictionaries
    list(map(read_credentials, zip([PUSHBULLET_CRED_FILE, PRAW_CRED_FILE], [PUSHBULLET_CRED_DICT, PRAW_CRED_DICT])))

    # Initialize notifier and praw instance
    pushbullet_notifier = get_notifier('pushbullet')
    reddit = praw.Reddit(**PRAW_CRED_DICT)

    # Subreddit to read info from and variables to save info to
    subreddit = reddit.subreddit(SUBREDDIT)
    my_items = {'timestamp': None, 'items': {}}
    prev_timestamp = None

    main_loop_iter_count = 1
    while True:
        logger.info(f"+----------------------------------+")
        logger.info(f"# Fetching new subreddit posts")
        logger.info(f"# ITERATION - {main_loop_iter_count}")
        logger.info(f"+----------------------------------+")

        try:
            subreddit_posts_new = subreddit.new(limit=MAX_POSTS_LIMIT)
            prev_timestamp = my_items['timestamp']
            # Read all available posts except stickied
            # Convert title to uppercase to choose with interested matches
            # Every new post added will change the timestamp to identify when to send notification
            for posts_obj in subreddit_posts_new:
                if not posts_obj.stickied and any(x in posts_obj.title.upper() for x in ITEM_MATCH):
                    if posts_obj not in my_items['items']:
                        if len(my_items['items']) >= MAX_POSTS_LIMIT:
                            first_entry = list(my_items['items'])[0]
                            logger.debug(f"Max length reached for items. Removing the oldest entry [{first_entry}]")
                            my_items['items'].pop(first_entry)
                        logger.debug(f"Adding new postobj id: [{posts_obj}]")
                        my_items['items'][posts_obj] = f"Title: {posts_obj.title}\nURL: {posts_obj.url}\n{'*'*30}\n"
                        my_items['timestamp'] = time()
                        logger.debug(f"Updating timestamp to [{my_items['timestamp']}]")
                    else:
                        logger.debug(f"Post object [{posts_obj}] is already in list")

            if prev_timestamp != my_items['timestamp']:  # new entry in item list
                logger.info("New post(s) available. Sending push notification")
                pushbullet_notifier.notify(message=''.join(my_items['items'].values()), **PUSHBULLET_CRED_DICT)
            else:
                logger.info("No new posts with matching pattern")

        except Exception as err:
            err_str = f"Exception occured: [{repr(err)}]"
            logger.error(err_str)
            logger.error("Traceback: ", exc_info=True)
            pushbullet_notifier.notify(message=json.dumps(traceback.format_exc()), **PUSHBULLET_CRED_DICT)

        finally:
            logger.info(f"Waiting for {WAIT_TIME} minute for next iteration...")
            main_loop_iter_count += 1
            sleep(WAIT_TIME * 60)


if __name__ == '__main__':
    main()
    logging.shutdown()
