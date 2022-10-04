# Standard imports
import os
import traceback
import logging
import json
from time import sleep, strftime, localtime, time
from datetime import datetime
from random import choice, sample
from RedDownloader import RedDownloader

import urllib.request



# 3rd party imports

import praw
import tweepy
from dotenv import load_dotenv, dotenv_values

load_dotenv()
config = dotenv_values(".env")

# Globals
SUBREDDITS = ['weatherporn','architectureporn', 'showerthoughts', 'imaginarysliceoflife', 'qoutesporn']

# Constants
WAIT_TIME = 60   # minute
MAX_POSTS_LIMIT = 1


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


def post_tweet(post):
    # Initialize and tweepy instance
    auth = tweepy.OAuthHandler(config['consumer_key'], config['consumer_secret'])
    auth.set_access_token(config['access_token'], config['access_token_secret'])
    api = tweepy.API(auth, wait_on_rate_limit=True)

    if post_type(post)== 'text':
        api.update_status(post.title + "\n\n" + post.selftext)
    elif post_type(post) == 'image':
        urllib.request.urlretrieve(post.url, "downloaded.jpeg")
        logger.info(f"# Downloading post image")
        sleep(5)
        api.update_status_with_media(post.title, "downloaded.jpeg")
    elif post_type(post) == 'video':
        RedDownloader.Download(post.url, 1080)
        api.update_status_with_media(post.title, "downloaded.mp4")

def post_type(subm) -> str:
    if getattr(subm, 'post_hint', '') == 'image':
        return 'image'
    elif getattr(subm, 'is_gallery', False):
        return 'gallery'
    elif subm.is_video:
        return 'video'
    elif hasattr(subm, 'poll_data'):
        return 'poll'
    elif hasattr(subm, 'crosspost_parent'):
        return 'crosspost'
    elif subm.is_self:
        return 'text'
    else:
        return 'link'


def main():
    # Initialize and praw instance
    reddit = praw.Reddit(
    client_id = config["client_id"],
    client_secret = config["client_secret"],
    user_agent = config["user_agent"])

    

    my_items = {'timestamp': None, 'items': {}}
    prev_timestamp = None

    main_loop_iter_count = 0
    while main_loop_iter_count <= 5:
        main_loop_iter_count += 1

        # Subreddit to read info from and variables to save info to
        subreddit = reddit.subreddit(choice(SUBREDDITS))
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
                # if not posts_obj.stickied and any(x in posts_obj.title.upper() for x in ITEM_MATCH):
                if not posts_obj.stickied:
                    if posts_obj not in my_items['items']:
                        if len(my_items['items']) >= MAX_POSTS_LIMIT:
                            first_entry = list(my_items['items'])[0]
                            logger.debug(f"Max length reached for items. Removing the oldest entry [{first_entry}]")
                            my_items['items'].pop(first_entry)
                        logger.debug(f"Adding new postobj id: [{posts_obj}]")
                        my_items['items'][posts_obj] = posts_obj
                        my_items['timestamp'] = time()
                        logger.debug(f"Updating timestamp to [{my_items['timestamp']}]")
                    else:
                        logger.debug(f"Post object [{posts_obj}] is already in list")

            if prev_timestamp != my_items['timestamp']:  # new entry in item list
                logger.info("New post(s) available. posting Tweet")
                post = list(my_items['items'])[-1]
                logger.info(f"fetched: {post}, Title: {post.title}")
                
                post_tweet(post)
                logger.info(f"updated status...")
                
            else:
                logger.info("No new posts with matching pattern")

        except Exception as err:
            err_str = f"Exception occurred: [{repr(err)}]"
            logger.error(err_str)
            logger.error("Traceback: ", exc_info=True)
            print(json.dumps(traceback.format_exc()))
        finally:
            logger.info(f"Waiting for {WAIT_TIME} minute for next iteration...")
            main_loop_iter_count += 1
            sleep(WAIT_TIME * 60)


if __name__ == '__main__':
    main()
    logging.shutdown()



