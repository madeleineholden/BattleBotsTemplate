from abc_classes import ADetector
from teams_classes import DetectionMark

class Detector(ADetector):
    def detect_bot(self, session_data):
        # todo logic
        marked_account = [] # Empty list to put DetectionMark objects

        #print("Session Metadata:", session_data.metadata)
        #print("Users Dataset:", session_data.users)
        #print("Posts Dataset:", session_data.posts)

        # CHECKING FOR BOT IN USERS:
        users=session_data.users
        for user in users:
            is_bot=False
            #print("User #", users.index(user)+1)
            for item in user:
                #print("\t", item, ":", user[item])
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
            for item in post:
                #print("\t", item, ":", post[item])
                if "bot" in str(post[item]).lower(): # Check if item contains the word "bot"
                    # CHECK IF USER IS ALREADY IN MARKED ACCOUNT
                    if DetectionMark(user_id=post["author_id"], confidence=75, bot=True) not in marked_account:
                        marked_account.append(DetectionMark(user_id=post["author_id"], confidence=75, bot=True))

        return marked_account
    