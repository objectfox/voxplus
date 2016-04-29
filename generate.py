#!/usr/bin/env python

from twython import Twython
import os
import feedparser
import re
import urllib, cStringIO
from PIL import Image, ImageFont, ImageDraw
import string
import dateutil
from dateutil import parser, tz
from time import strftime
import pytz
import random
import warnings
warnings.filterwarnings("ignore")

twitter = Twython(os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'],
                  os.environ['ACCESS_TOKEN'], os.environ['ACCESS_TOKEN_SECRET'])

sites = [["http://www.theverge.com/rss/index.xml", "theverge_template.png", "@verge"],
["http://www.vox.com/rss/index.xml", "vox_template.png", "@voxdotcom"],
["http://www.eater.com/rss/index.xml", "eater_template.png", "@eater"],
["http://www.racked.com/rss/index.xml", "racked_template.png", "@racked"],
["http://www.curbed.com/rss/index.xml", "curbed_template.png", "@curbed"],
["http://www.polygon.com/rss/index.xml", "polygon_template.png", "@polygon"],
["http://www.sbnation.com/rss/index.xml", "sbnation_template.png", "@sbnation"]]

rss, template_file, handle = random.choice(sites)

feed = feedparser.parse(rss)
headline = ""
author = ""
image = ""
url = ""
publish_time = None

for entry in feed.entries:
	m = re.search('^<img[^>]+ src="([^"]+)"', entry.content[0]['value'])
	if m and m.group(1):
		image = m.group(1)
		headline = entry.title
		author = entry.author
		url = entry.link
		publish_time = parser.parse(entry.published)
		break

local_tz = pytz.timezone('US/Eastern')

publish_time = publish_time.astimezone(local_tz)

# print publish_time
# print headline

lines = []
headlines = string.split(headline)
workline = ""
for word in headlines:
	if len(workline + word) > 30:
		lines.append(workline)
		workline = ""
	workline = workline + word + " "

if workline:
	lines.append(workline)

broken_headline = "\n".join(lines)

# print author
# print image

base = Image.open(template_file)

base = base.convert("1")


imagefile = cStringIO.StringIO(urllib.urlopen(image).read())
img = Image.open(imagefile)
img.thumbnail([250,300])
bwimg = img.convert("1")

base.paste(bwimg,(20,65))

time_image = Image.new("1", (400,15), (1))
time_font = ImageFont.truetype("resources/chicagobold.ttf", 12)
timeline = ImageDraw.Draw(time_image)
timeline = timeline.text((0,0), publish_time.strftime('Published on %A, %B %d, %Y at %I:%M %p %Z'), font=time_font, fill=(0))
base.paste(time_image,(20,45))

title_image = Image.new("1", (388,60), (1))
title_font = ImageFont.truetype("resources/chicagobold.ttf", 20)
title_line = ImageDraw.Draw(title_image)
title_line = title_line.multiline_text((0,0), broken_headline, font=title_font, fill=(0))


base.paste(title_image,(20,238))

author_image = Image.new("1", (100,12), (1))
author_font = ImageFont.truetype("resources/chicagobold.ttf", 10)
user_byline = ImageDraw.Draw(author_image)
user_byline = user_byline.text((0,0), "By "+author, font=author_font, fill=(0))

base.paste(author_image,(20,300))
base = base.resize((1024,684), Image.ANTIALIAS)

base.save("output.gif")

photo = open('output.gif', 'rb')
response = twitter.upload_media(media=photo)
twitter.update_status(status=headline+" - "+handle+"\n"+url, media_ids=[response['media_id']])

