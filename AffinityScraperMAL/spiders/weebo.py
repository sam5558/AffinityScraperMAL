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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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
friend_names = [f["user"]["username"] for f in userlist]
for i in range(0,len(friend_names)):
    e.append(str('https://myanimelist.net/profile/') + str(friend_names[i]))

class MAL_spider(scrapy.Spider):
    name = 'weebo'
    mal_login_url = 'https://myanimelist.net/login.php'
    start_urls = [mal_login_url]

    user_name = AffinityScraperMAL.spiders.credentials.user_name
    password = AffinityScraperMAL.spiders.credentials.password
    chrome_options = Options()
    #chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless")
    global driver
    driver = webdriver.Chrome(options=chrome_options)

    driver.get('https://myanimelist.net/login.php')
    if("Login" in driver.title):
        id_box = driver.find_element(By.NAME, 'user_name')
        id_box.send_keys(user_name)
        password_box = driver.find_element(By.NAME, 'password')
        password_box.send_keys(password)
        login_button = driver.find_element(By.CLASS_NAME, "btn-form-submit")
        driver.execute_script("arguments[0].click();", login_button)
        #login_button.click()
    time.sleep(1)

    token = None

    def parse(self, response):
        if self.password == '':
            self.logger.error('first add a pasword')
            return
        self.token = response.xpath('//meta[@name="csrf_token"]/@content').extract()
        self.log('token {}'.format(self.token))

        return [FormRequest(
                    url = self.mal_login_url,
                    cookies=driver.get_cookies(),
                    callback = self.after_login
                    )]

    def after_login(self, response):
        for i in range(0,len(e)):
            yield Request(
                url=e[i],
                cookies=driver.get_cookies(),
                meta={'Title': friend_names[i]},
                callback=self.action)

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