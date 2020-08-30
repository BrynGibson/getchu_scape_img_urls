from selenium import webdriver
import lxml.html
import requests
from selenium.webdriver.chrome.options import Options
import time

# this class is designed to be used as a subprocess within the controller mother_scaper
# this object will initialize a connection to a test getchu page using selenium and accept the age verification dialog
# this object will then copy the cookies from selenium and store them for using direct requests avoiding the age verifcation proccess

class SubScraper:

    def __init__(self, url_gen, df):
        self.url_gen = url_gen
        self.df = df
        options = Options()
        options.add_argument("--headless")

        # webdriver location for desktop

        print("setting up driver")
        self.driver = webdriver.Chrome(r"C:\Users\sloth\Desktop\int app dev\intermediate-app-dev-concepts\05-python-5-exceptions-automation-testing\chromedriver.exe", options=options)

        # do age verification for getchu

        print("loading test page for age verify")
        self.driver.get("http://www.getchu.com/soft.phtml?id=1077034")

        age_verify_link = self.driver.find_element_by_link_text("[は い]")
        print("clicking link")
        age_verify_link.click()

        # creating cookies to use with requests library
        cookies_list = self.driver.get_cookies()
        cookies_dict = []
        for cookie in cookies_list:
            cookies_dict.append([cookie['name'], cookie['value']])

        self.cookies = dict(cookies_dict)
        self.driver.close()

    def scrape(self):

        # this method will run as a loop making get requests to the url provided by the url provided by the generator created in the controller
        # this method will continue iterating untill it receives a StopIteration exception from the generator

        complete = False

        while not complete:

            try:
                url = next(self.url_gen)
                attempts = 1

                # will repeat the request 5 times if the request times out

                while attempts < 6:

                    r = requests.get(url, cookies=self.cookies)

                    if r.status_code == 200:

                        # converting request into lxml etree

                        doc = lxml.html.fromstring(r.content)

                        # getting the relative path for all character images on the page

                        img_rel_urls = doc.xpath('//img[contains(@alt, "キャラ")]/@src')

                        # checking if characters were found, not all pages contain character images so this may be empty

                        if img_rel_urls:

                            print(f'response ok, img urls found, url {url}')

                            # expanding relative urls into full urls

                            full_urls = list(map(lambda o: "http://www.getchu.com" + o.replace(".", "", 1), img_rel_urls))
                            self.df.loc[url, "response"] = 200
                            self.df.loc[url, "found_char_imgs"] = True
                            self.df.loc[url, "img_urls"] = str(full_urls)
                            attempts = 5
                            full_urls = None

                        else:
                            print(f'response ok, characters not found, url {url}')
                            self.df.loc[url, "response"] = 200
                            self.df.loc[url, "found_char_imgs"] = False
                            attempts = 5

                    # if the request timed out will try again in 200ms

                    elif r.status_code == 408 or r.status_code == 503 or r.status_code == 504 or r.status_code == 500:
                        self.df.loc[url, "response"] = r.status_code
                        self.df.loc[url, "found_char_imgs"] = False
                        print(f'response {r.status_code} attempt {attempts} , sleeping for 200ms , url {url}')
                        time.sleep(0.2)
                        attempts += 1

                    # if a bad status code then will skip retrying and move onto next url
                    else:
                        self.df.loc[url, "response"] = r.status_code
                        print(f'bad status code {r.status_code}, ending request, url {url}')
                        attempts = 5

            except StopIteration:
                print("end of urls")
                complete = True
