import praw
import os
import requests
import time
import urllib.parse
from glob import glob
from twython import Twython

CONSUMER_KEY = 'zx28cDrlzCCnUX2JINSFzVRUD'
CONSUMER_SECRET = 'KhtTDX0eANskPe0dyXtpmZxpSj9LohHKypQjoG8Q0JWlJWBv8Q'
ACCESS_TOKEN = '1142179257797566466-6BtiNOKiRCKUWrBASokzJmhLK3OEfq'
ACCESS_SECRET = 'snnc88NAIqaVcPOCdrR8hHzjpHHnR381djjyRd04e4lax'

SUBREDDIT = 'dankmemes'
IMAGE_DIR = '/home/pi/Documents/TweetBot/images'
POSTED_CACHE = '/home/pi/Documents/TweetBot/cache.txt'
MAX_CHARACTER_LENGTH = 280
T_CO_LINKS_LEN = 24
TWEET_SUFFIX = ''

CLIENT_ID = 'ORHnTsw77vaagA'
CLIENT_SECRET = 'KrDlJx11AdDQW9j2YwaYSHcLrs4'
USER_AGENT = 'frc twitter'

def setup_reddit_connection(subreddit):
    print('!!setting up reddit connection!!')
    reddit = praw.Reddit(client_id = CLIENT_ID, client_secret = CLIENT_SECRET, user_agent = USER_AGENT)
    return reddit.subreddit(subreddit)

def tweet_creator(subreddit_info):
    post_dict = {}
    post_ids = []
    print('!!getting posts!!')
    
    for submission in subreddit_info.new(limit=10):
        if not already_tweeted(submission.id):
            post_dict[submission.title] = {}
            post = post_dict[submission.title]
            post['link'] = submission.permalink
            post['img_path'] = get_image(submission.url)
            post_ids.append(submission.id)
        else:
            print('!!already tweeted: {}'.format(str(submission)))
    return post_dict, post_ids

def strip_title(title, character_amt):
    if len(title) <= character_amt:
        return title
    else:
        return title[:character_amt -1] + '...'
        
def get_image(img_url):
    if img_url:
         filename = os.path.basename(urllib.parse.urlsplit(img_url).path)
         img_path = IMAGE_DIR + '/' + filename
         print('!!!downloading img url ' + img_url + ' to ' + img_path + ' !!!')
         resp = requests.get(img_url, stream = True)
         if resp.status_code == 200:
             with open(img_path, 'wb') as image_file:
                 for chunk in resp:
                     image_file.write(chunk)
             return img_path
         else:
             print('!!! image failed to download. status code: ' + str(resp.status_code) + ' !!!')
    else:
        print('!!!Post isnt an imgur link !!!')
    return ''

def tweeter(post_dict, post_ids):
    api = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    
    for post, post_id in zip(post_dict, post_ids):
        img_path = post_dict[post]['img_path']
        
        extra_text = '' + post_dict[post]['link']
        extra_text_len = 1 + T_CO_LINKS_LEN + len(TWEET_SUFFIX) 
        if img_path:
            extra_text_len += T_CO_LINKS_LEN
        post_text = strip_title(post, MAX_CHARACTER_LENGTH - extra_text_len) + ' www.reddit.com' + extra_text
        print('!!! posting link on Twitter!!!')
        print(post_text)
        if img_path:
            img = open(img_path, 'rb')
            response = api.upload_media(media=img)
            print('!!! w/ image ' + img_path + ' !!!')
            api.update_status(status=post_text, media_ids = [response['media_id']])
        else:
            api.update_status(status=post_text)
        log_tweet(post_id)
        time.sleep(30)
        
def log_tweet(post_id):
    with open(POSTED_CACHE, 'a') as out_file:
        out_file.write(str(post_id) + '\n')
    
def already_tweeted(post_id):
    found = False
    with open(POSTED_CACHE, 'r') as in_file:
        for line in in_file:
            if post_id in line:
                found = True
                break
    return found

def main():
    if not os.path.exists(POSTED_CACHE):
        with open(POSTED_CACHE, 'w'):
            pass
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
        
    subreddit = setup_reddit_connection(SUBREDDIT)
    post_dict, post_ids = tweet_creator(subreddit)
    tweeter(post_dict, post_ids)
    
    for filename in glob(IMAGE_DIR + '/*'):
        os.remove(filename)
    
if __name__ == '__main__':
    main()