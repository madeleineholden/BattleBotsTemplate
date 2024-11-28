from abc_classes import ADetector
from teams_classes import DetectionMark

import numpy as np
#from datetime import datetime
import json
from textblob import TextBlob

class Detector(ADetector):
    def detect_bot(self, session_data):
        # todo logic
        marked_account = [] # Empty list to put DetectionMark objects

        posts=session_data.posts
        users=session_data.users

        user_sentiment={user['id']:0 for user in users}

        for post in posts: # get sentiment score for each post
            text=post['text']

            analysis=TextBlob(text) # Calculate sentiment score for each post
            polarity=analysis.sentiment.polarity # score between -1 and 1
            sentiment_score=abs(polarity)

            if sentiment_score > 0: # polarity if not neutral
                user_sentiment[post['author_id']]+=sentiment_score # update user's sentiment score

        for user in users:
            user_id=user['id']

            if user['tweet_count']!=0: # if user has tweets
                sentiment_per_post=user_sentiment[user_id]/user['tweet_count'] # get avg sentiment per post

                if sentiment_per_post < 0.75: # if sentiment less than 0.75 threshold, probably not bot
                    conf=(1-sentiment_per_post)*100 # conf = inverse of sentiment
                    is_bot=False
                else: # if sentiment greater than avg, probably bot
                    conf=sentiment_per_post*100 # use sentiment per post as conf
                    is_bot=True

                marked_account.append(DetectionMark(user_id=user_id, confidence=round(conf), bot=is_bot))

            else: # if user has no tweets, mark as bot
                marked_account.append(DetectionMark(user_id=user_id, confidence=99, bot=True))
        
        return marked_account
        

'''
NOTES:
* POST LEVEL:
- author_id
- created_at
- lang

* USER LEVEL:
- id
- tweet_count
- z_score
- username
- name
- description
- location

IDEAS:
- do something with language? --> one of the bot tweets has "string" instead of "en"
- for confidence: have some metrics that updates, so if you get multiple indicators of a bot, increase confidence
- check if user posting multiple times in a row
- check if multiple posts have the exact same content
- check if all tweets are from the same day
- check if date posted is in the future -> DONE
UNTRIED:
- check if some tweets don't have any letters (e.g. all emojis, all numbers, etc.)
- could look into topic model from llcu 255?
- something with TFIDF
'''