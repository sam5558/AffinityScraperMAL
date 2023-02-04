

# python class that uses scrapy to login to a website using the csrf token
# test that portion afterwards :

import scrapy
from scrapy.http import FormRequest

class LoginSpider(scrapy.Spider):
    name = 'login'

    start_urls = ['https://example.com/login']

    def parse(self, response):
        token = response.xpath('//input[@name="csrf_token"]/@value').extract_first()

        return FormRequest.from_response(response, formdata={
            'csrf_token': token,
            'username': 'your_username',
            'password': 'your_password'
        }, callback=self.after_login)

    def after_login(self, response):
        # do whatever you need here
        pass


### i found this code here ( interesting to notice if login is successful or no)
## https://www.youtube.com/watch?v=VySakHZi6HI

    def start_scrapping(self,response):
        imgdata = base64.b64decode(response.data['png'])
        filename = 'after_login.png'
        with open(filename, 'wb') as f:
            f.write(imgdata)

