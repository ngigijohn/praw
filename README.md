# Fetch new posts from Reddit
* Usage for PRAW-Reddit api to get new posts from a subreddit
* New posts are saved in a dictionary along with the timestamp which gets updated whenever new entry is added
    * Send a push notification to android through _pushbullet_ for new posts
* Also provided _Dockerfile_ in case you want to run it as a docker container

# USAGE
* Clone the repo
* Fill in the correct credentials for both _pushbullet_ and _praw_
* Either you can run the code as `python3 main.py` or through Dockerfile as follows
    * Build image from Dockerfile `docker build --tag <name>:<tag> .`
    * Run the image in detatched mode `docker run -d -v $(pwd)/logs:/praw/logs --name <container_name> <name>:<tag>`
        * Or run it in interactive mode by using `-it` instead of `-d`
    * It should create a directory called _logs_ with the log file in it

# Requirements
* Python 3+ (tested on version 3.7.7)
* Install [PRAW](https://praw.readthedocs.io/en/latest/) to interact with Reddit
* Install [Notifiers](https://github.com/notifiers/notifiers) to send notifications to android
* Create 2 files _without extension_ in parent directory named `pushbullet_credentials` and `praw_credentials` and save information in those. Format will be `key=value`

# Optional
* Install Docker _(ext-id: ms-azuretools.vscode-docker)_ extension in VSCode for easy docker operations
