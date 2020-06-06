# Fetch new posts from Reddit (PRAW)
* Usage for PRAW-Reddit api to get new posts from a subreddit
* New posts are saved in a dictionary along with the timestamp which gets updated whenever new entry is added
    * Send a push notification to android through _pushbullet_ for new posts
* Also provided _Dockerfile_ in case you want to run it as a docker container
    * Run it as `docker run -it -v $(pwd)/logs:/praw/logs --name HelloWorld praw:1.0`

# Requirements
* Install [PRAW](https://praw.readthedocs.io/en/latest/) to interact with Reddit
* Install [Notifiers](https://github.com/notifiers/notifiers) to send notifications to android
* Create 2 files _without extension_ in parent directory named `pushbullet_credentials` and `praw_credentials` and save information in those. Format will be `key=value`
