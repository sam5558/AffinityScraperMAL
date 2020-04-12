# AffinityScraperMAL
This repository scrapes, sort &amp; reorder your friendlist by affinity. 
Then it outputs the ranking as a png image.

This script comes as a replacement of [MALAffinity-Generator-IMG](https://github.com/sam5558/MALAffinity-Generator-IMG)

# Benefits of this new script compared to my old one
* Old one used to download each user's animelist, then calculates the affinity with me, then get top 10 users... which took a lot of time (the more firends you have the more time if takes)
* The new script uses scraping with the use of username/password, which made me get my list of users 5 or 6 times quicker.
* It's now possible to get a top 10 for anime friends & another one for manga friends, when before all i was able to do is a top 10 for anime friends

# Prepare the environment 

You'll need : 
* Python3.6+

I've mentionned all the necessary packages, all you need to do is execute: 
`pip3 install requirements.txt`
It'll automatically install needed packages.

# Usage
0/ go to `~/AffinityScraperMAL/spiders`

1/ Start by : 
`cp credentials.py.bck credentials.py`

2/ Feed it with your MyAnimeList username/password in `credentials.py` (eg.) : 
```
user_name = 'myuser'
password = 'mypass'
```
3/ then : 
`cp config.py.example config.py`

4/ Note that this script does also store code results in your personal github, if you don't want to bother yourself with this please comment the following line :
`# self.gitsync()` (line 168)

Finally Execute : 

`scrapy crawl weebo`

Get yourself a cup of coffee and wait the magic.
