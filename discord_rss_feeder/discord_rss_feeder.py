# Discord RSS Feeder
# Just run this with a task scheduler or cron job
import feedparser
import requests
import yaml
from datetime import datetime
from time import mktime


# Helper function for pickle
class YAMLHelper:
    def __init__(self, file_path):
        self.file_path = file_path
    def read(self):
        with open(self.file_path, 'rb') as f:
            return yaml.safe_load(f)        
    def save(self, obj):
        with open(self.file_path, 'w') as f:
            yaml.dump(obj, f)


# YAML 
yaml_file = r'discord_rss_feeder.yaml'
dct_yaml_template = {'change_me': {'feed_url': 'change_me', 'discord_webook_url': 'change_me', 'discord_last_push_epoch': 0}}
yaml_obj = YAMLHelper(yaml_file)
try:
    dct_yaml = yaml_obj.read()
except:
    yaml_obj.save(dct_yaml_template)
    pickled_push_publish_epoch = yaml_obj.read()
    print("Please edit %s" & yaml_file)

# Iterate through YAML configured feeds
for feed_site in dct_yaml:
    #print('Processing feed %s ...' % (feed_site))
    
    # Prepare feed_site variables
    feed_url = dct_yaml[feed_site]['feed_url']
    webhook_url = dct_yaml[feed_site]['discord_webhook_url']
    yaml_push_publish_epoch = int(dct_yaml[feed_site]['discord_last_push_epoch'])
    
    # Parse the RSS feed
    feed = feedparser.parse(feed_url)

    # Get the newest published date as epoch time
    dt = datetime.fromtimestamp(mktime(feed.entries[0]['published_parsed'])) 
    newest_publish_epoch = int(dt.timestamp())

    # Iterate through the feed and post to Discord
    for entry in feed.entries:
        pub_epoch = datetime.fromtimestamp(mktime(entry.published_parsed)).timestamp()
        # Ignore items already posted using yaml stored epoch
        if int(pub_epoch) > yaml_push_publish_epoch:
            message = entry.title + "\n" + entry.link
            requests.post(webhook_url, json={"content": message})

    # Store the feed updates in the YAML file
    dct_yaml[feed_site]['discord_last_push_epoch'] = newest_publish_epoch
    yaml_obj.save(dct_yaml)
