#coding=utf-8
import os
import time
from importlib import reload
import scrapy
import AffinityScraperMAL.spiders.config
import AffinityScraperMAL.spiders.credentials
from scrapy.http import FormRequest
from scrapy.http.request import Request
from jikanpy import Jikan
from collections import OrderedDict
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# variables
userlist = []
e = []
affinity = {}
results = {}
resultsmanga = {}
topaff = []
topaffmanga = []
names = []
namesmanga = []
var = []
varsmanga = []
#user_name = 'Guts__'
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M")
jikan = Jikan()

# friends get data
ufriends = jikan.users(username=AffinityScraperMAL.spiders.credentials.user_name, extension='friends')
#print(len(ufriends['data']))
ufriends2 = jikan.users(username=AffinityScraperMAL.spiders.credentials.user_name, extension='friends', page=2)
#print(len(ufriends2['data']))
# merge all users
for i in range(len(ufriends['data'])):
  userlist.append(ufriends['data'][int(i)])
for i in range(len(ufriends2['data'])):
  userlist.append(ufriends2['data'][int(i)])
# create a list of friend names
#print(userlist)
friend_names = [f["user"]["username"] for f in userlist]
print(friend_names)
for i in range(0,len(friend_names)):
    e.append(str('https://myanimelist.net/profile/') + str(friend_names[i]))



class MAL_spider(scrapy.Spider):
    name = 'weebo'
    mal_login_url = 'https://myanimelist.net/'
    start_urls = [mal_login_url]

    user_name = AffinityScraperMAL.spiders.credentials.user_name
    password = AffinityScraperMAL.spiders.credentials.password
    # custom headers
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'fr-FR,fr;q=0.5',
        'cache-control': 'no-cache',
        'cookie': 'reviews_sort=recent; search_view2=list; search_sort_anime=score; search_view=list; m_gdpr_mdl_6=1; MALSESSIONID=sprklh2jv21n78rv5mng39vao1; is_logged_in=1; MALHLOGSESSID=4bc6195b0831ebb8ed582dec33d35600; text_ribbon=%5B6%2C7%2C8%5D; clubcomments=a%3A1%3A%7Bi%3A59197%3Bi%3A1673722378%3B%7D',
        'pragma': 'no-cache',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'sec-gpc': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    token = None

    def parse(self, response):
        if self.password == '':
            self.logger.error('first add a pasword')
            return
        self.token = response.xpath('//meta[@name="csrf_token"]/@content').extract()
        self.log('token {}'.format(self.token))

        return [FormRequest(
                    url = self.mal_login_url,
                    method = 'POST',
                    formdata =
                        {
                            'user_name':  self.user_name,
                            'password' :  self.password,
                            'csrf_token': self.token,
                            'submit' : '1',
                            'cookie' : '1'
                        },
                    headers = self.headers,
                    callback = self.after_login
                    )]

    def after_login(self, response):
        for i in range(0,len(e)):
            yield Request(
                url=e[i],
                headers=self.headers,
                meta={'Title': friend_names[i]},
                callback=self.action)
        #yield Request(
        #    url='https://randomlogger.ml',
        #    callback=self.generateimg)

    def action(self, response):
        affinity = response.xpath('/html/body/div[1]/div[2]/div[3]/div[2]/div/div[1]/div/div[4]/div[2]/div[2]/span/text()').get()
        affinitymanga = response.xpath('/html/body/div[1]/div[2]/div[3]/div[2]/div/div[1]/div/div[4]/div[4]/div[2]/span/text()').get()
        pureaff = str(affinity).replace('%','').replace('\xa0\xa0','').replace('None','0')
        pureaffmanga = str(affinitymanga).replace('%','').replace('\xa0\xa0','').replace('None','0')
        pureaff = "{:05.2f}".format(float(pureaff))
        pureaffmanga = "{:05.2f}".format(float(pureaffmanga))
        #filename = 'output2.log'
        #f = open(filename, 'a+')
        #f.write("%s: %s\r\n" %(response.meta['Title'] , pureaff))
        #f.write("%s: %s\r\n" %(response.meta['Title'] , pureaffmanga))
        results[response.meta['Title']]= pureaff
        resultsmanga[response.meta['Title']]= pureaffmanga
        if len(results) == len(e):
            print('#############################################')
            sortedaff = OrderedDict(sorted(results.items(), key=lambda t: t[1], reverse=True))
            sortedaffmanga = OrderedDict(sorted(resultsmanga.items(), key=lambda t: t[1], reverse=True))
            topaff = list(sortedaff.items())[:10]
            topaffmanga = list(sortedaffmanga.items())[:10]
            f = open('config.py','w+')
            f.write("rankedaff = %s\nrankedaffmanga = %s" % (topaff,topaffmanga))
            f.close()
            self.generateimg()

        time.sleep(2)

    def gitsync(self):
        os.system('git add .')
        os.system('git commit -m "updates"')
        os.system('git push origin master')

    def generateimg(self):
        #print(myaffinity)
        image = Image.open('top-friends.png').convert('RGBA')
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('Roboto-Bold.ttf', size=45)
        updatefont = ImageFont.truetype('Roboto-Bold.ttf', size=30)
        # starting position of the message
        (x, y) = (50, 50)
        message = "TOP 20 MyAnimeList Friends"
        color = 'rgb(47,82,162)' # black color
        draw.text((x, y), message, fill=color, font=font)

        (x, y) = (50, 150)
        message = "Anime Friends"
        color = 'rgb(47,82,162)' # black color
        draw.text((x, y), message, fill=color, font=font)

        (x, y) = (550, 150)
        message = "Manga Friends"
        color = 'rgb(47,82,162)' # black color
        draw.text((x, y), message, fill=color, font=font)

        (x, y) = (50, 850)
        lasttime = "last updated : " + dt_string
        color = 'rgb(177,116,104)'
        draw.text((x, y), lasttime, fill=color, font=updatefont)

        AffinityScraperMAL.spiders.config = reload(AffinityScraperMAL.spiders.config)
        for i in range(0,10):
            names.append(''.join([v for v in AffinityScraperMAL.spiders.config.rankedaff[i][0]]))
            namesmanga.append(''.join([v for v in AffinityScraperMAL.spiders.config.rankedaffmanga[i][0]]))
            var.append(''.join([v for v in AffinityScraperMAL.spiders.config.rankedaff[i][1]])+"%")
            varsmanga.append(''.join([v for v in AffinityScraperMAL.spiders.config.rankedaffmanga[i][1]])+"%")

        color = 'rgb(159, 99, 63)' # white color
        for i in range(0,10):
            (x, y) = (50, 200)
            y=y+(i*50)
            draw.text((x, y), names[i], fill=color, font=font)
            (x, y) = (350, 200)
            y=y+(i*50)
            draw.text((x, y), var[i], fill=color, font=font)

            (x, y) = (550, 200)
            y=y+(i*50)
            draw.text((x, y), varsmanga[i], fill=color, font=font)
            (x, y) = (750, 200)
            y=y+(i*50)
            draw.text((x, y), namesmanga[i], fill=color, font=font)

        # save the edited image
        image.save('top-20-friends.png')
        self.gitsync()
