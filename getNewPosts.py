import praw
reddit = praw.Reddit(client_id='5Q4B5b7Vpz5bRA',
                     client_secret="jtA8J5Pc9jUjixO2VMQyETpzLkU",
                     user_agent="praw-reddit")
                    #  password='PASSWORD',
                    #  username='USERNAME')

subreddit = reddit.subreddit('bapcsalescanada')

subreddit_posts_new = subreddit.new(limit=3)   # iterator of post object id

for posts_obj in subreddit_posts_new:
    if not posts_obj.stickied:
        print(f"Post Title: {posts_obj.title}, Ups: {posts_obj.ups}, Downs: {posts_obj.downs}, IsVisited: {posts_obj.visited}")
        print('--comments--')
        """
        Other options we have:
        Help: https://www.reddit.com/dev/api#POST_api_vote
        Submissions (threads/comments)
            .upvote()   # Could get us banned. Meant for 'human' use
            .clear_vote()
            .downvote()
            .reply()
        Subreddits:
            .subscribe()
            .unsubscribe()
        """
        # Parsing comments
        comments = posts_obj.comments
        for comment in comments:
            print(comment.body)
            print(f"Replies on this comment: {comment.replies}")
        