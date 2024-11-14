from abc_classes import ADetector
from teams_classes import DetectionMark

import numpy as np
from datetime import datetime

import json

class Detector(ADetector):
    def detect_bot(self, session_data):
        # todo logic
        marked_account = [] # Empty list to put DetectionMark objects
        
        max_confidence=8 # CHANGE TO THE NUMBER OF CRITERIA I COME UP WITH

        #print("Session Data:", session_data)
        posts=session_data.posts
        users=session_data.users

        ######################### GETTING AVERAGE Z-SCORE AND TWEET COUNT #########################
        z_scores=[]
        tweet_counts=[]

        for user in users:
            z_scores.append(user['z_score'])
            tweet_counts.append(user['tweet_count'])

        avg_z_score=np.mean(z_scores)
        std_z_score=np.std(z_scores)

        avg_tweet_count=np.mean(tweet_counts)
        std_tweet_count=np.std(tweet_counts)
        #########################################################################################
        
        for user in users:
            bot_criteria=0
            
            ############################################################################################
            # CHECK 1 - check if user has "bot" in any of their fields
            for item in user:
                if "bot" in str(user[item]).lower():
                    bot_criteria+=1

            ############################################################################################
            # CHECK 2 - check if user has a non-alphanumeric ID
            if not user['id'].isalnum():
                bot_criteria+=1

            ############################################################################################
            # CHECK 3 - check if user has multiple posts with the exact same content
            current_users_posts=[]
            for post in posts:
                if user['id']==post['author_id']:
                    current_users_posts.append(post['text'])

            if len(current_users_posts) != len(set(current_users_posts)): # indicates duplicates
                bot_criteria+=1

            ############################################################################################
            # CHECK 4 - check if time between posts is less than a certain threshold (e.g. 30 seconds?)
            post_times=[]

            for post in posts:
                if post['author_id']==user['id']:
                    time_posted=datetime.strptime(post['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')#.date()
                    post_times.append(time_posted)

            time_differences=[]

            for i in range(1,len(post_times)):
                time1=post_times[i] # current post's time
                time2=post_times[i-1] # previous post's time
                time_differences.append((time1-time2).total_seconds()) # get the time difference in seconds

            if any(time_diff<30 for time_diff in time_differences): # if any differences are <30 seconds
                bot_criteria+=1
            
            ############################################################################################
            # CHECK 5 - check if all tweets are from the same day
            post_dates=[time.date() for time in post_times] # get only the date part of the datetime object

            if len(set(post_dates))==1: # indicates all tweets from same day (all dates are the same)
                bot_criteria+=1

            ############################################################################################
            # CHECK 6 - check if z-score is above mean + std?
            if user['z_score'] > avg_z_score + 2*std_z_score:
                bot_criteria+=1

            ############################################################################################
            # CHECK 7 - check if tweet count is above mean + std?
            if user['tweet_count'] > avg_tweet_count + 2*std_tweet_count:
                bot_criteria+=1

            ############################################################################################
            # CHECK 8 - check if date posted is in the future
            today=datetime.today()

            # Check if any times are after today:
            if any(time > today for time in post_times):
                bot_criteria+=1
                #print("CHECK 8 HAPPENED")

            ############################################################################################
            # FINAL BOT CLASSIFICATION
            classifier = 1 / (1 + np.exp(3)*np.exp(-bot_criteria))
    
            if classifier>=0.5:
                is_bot=True
            else:
                is_bot=False
            
            conf=round(1 / (1 + np.exp(8/2)*np.exp(-4))*100) # 1 / (1 + e^(-x)) (shifted to be between 0 & 8, automatically bounded btw 0 & 100)
        
            marked_account.append(DetectionMark(user_id=user['id'], confidence=conf, bot=is_bot))
            '''
            is_bot = bot_criteria>0 # If any of the criteria are met, classify as bot

            if is_bot:
                #conf = int(round(bot_criteria/max_confidence*100,0)) # Confidence = num of criteria met / max confidence
                # TRYING SIGMOID FUNCTION TO CALCULATE CONFIDENCE
                if bot_criteria==8:
                    print('ALL CRITERIA SATISFIED')
                conf = round(1 / (1 + max_confidence*np.exp(-bot_criteria))*100) # 1 / (1 + e^(-x)) (shifted to be between 0 & 8, automatically bounded btw 0 & 100)
            else:
                conf=1

            marked_account.append(DetectionMark(user_id=user['id'], confidence=conf, bot=is_bot))
            '''
            

        #print("\nMarked Accounts:")
        i=1
        #user_ids=[]
        confidence_levels=[]
        for account in marked_account:
            #print(i, account)
            i+=1
            if account.confidence!=0:
                confidence_levels.append(account.confidence)
                #if account.confidence==100:
                    #print("CONFIDENCE LEVEL 100 FOUND")
            #user_ids.append(account.user_id)

        #if len(user_ids)!=len(set(user_ids)):
        #    print("DUPLICATE USER IDS FOUND")
        #print(confidence_levels)
            
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

'''
-----------------------------------PREVIOUS CODE-----------------------------------

# CHECKING FOR BOT IN USERS:
        users=session_data.users
        for user in users:
            is_bot=False
            print("\nUser #", users.index(user)+1)
            for item in user:
                print("\t", item, ":", user[item])
                if "bot" in str(user[item]).lower(): # Check if item contains the word "bot"
                    is_bot=True # If it does, set is_bot to True
                # Check if ID contains any letters or special characters
                if item=="id" and not user["id"].isalnum():
                    is_bot=True
            if is_bot:
                marked_account.append(DetectionMark(user_id=user["id"], confidence=75, bot=True))
            else:
                marked_account.append(DetectionMark(user_id=user["id"], confidence=75, bot=False))

        # CHECKING FOR BOT IN POSTS:
        posts=session_data.posts
        for post in posts:
            # Skip if not the bot:
            if post["author_id"] != '5fbc46b0-2a80-4dc5-b499-fae4bdb335c1':
                break
            print("\nPost #", posts.index(post)+1)
            for item in post:
                print("\t", item, ":", post[item])
                if "bot" in str(post[item]).lower(): # Check if item contains the word "bot"
                    # CHECK IF USER IS ALREADY IN MARKED ACCOUNT
                    #if DetectionMark(user_id=post["author_id"], confidence=75, bot=True) not in marked_account:
                    #    marked_account.append(DetectionMark(user_id=post["author_id"], confidence=75, bot=True))
                    # Check if author_id is already in marked_account
                    for account in marked_account:
                        
                        #if account.user_id == post["author_id"]:
                            account.bot=True
                            break
                        
                        print(account.user_id)
                        
                    
                    #else:
                        #marked_account.append(DetectionMark(user_id=post["author_id"], confidence=75, bot=True))
        print("\nMarked Accounts:")
        for account in marked_account:
            print(account)
            #print(account.user_id, "is a bot:", account.bot, "with a confidence of", account.confidence)
        return marked_account

'''