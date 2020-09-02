from selenium import webdriver
import lxml.html
import requests
from selenium.webdriver.chrome.options import Options
import time
from ast import literal_eval
import PIL.Image
from pathlib import Path
import sys

# this class is designed to be used as a subprocess within the controller mother_scaper
# this object will initialize a connection to a test getchu page using selenium and accept the age verification dialog
# this object will then copy the cookies from selenium and store them for using direct requests avoiding the age verifcation proccess

class SubScraper:

    def __init__(self, url_gen=None, df_urls=None, img_url_gen=None):
        self.url_gen = url_gen
        self.df_urls = df_urls
        self.img_url_gen = img_url_gen
        options = Options()
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')

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
        # this method will continue iterating until it receives a StopIteration exception from the generator

        complete = False


        while not complete:

            try:
                url = next(self.url_gen)
                attempts = 1

                # will repeat the request 5 times if the request times out

                while attempts < 5:

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
                            self.df_urls.loc[url, "response"] = 200
                            self.df_urls.loc[url, "found_char_imgs"] = True
                            self.df_urls.loc[url, "img_urls"] = str(full_urls)
                            attempts = 5
                            full_urls = None

                        else:
                            print(f'response ok, characters not found, url {url}')
                            self.df_urls.loc[url, "response"] = 200
                            self.df_urls.loc[url, "found_char_imgs"] = False
                            attempts = 5

                    # if the request timed out will try again in 200ms

                    elif r.status_code == 408 or r.status_code == 503 or r.status_code == 504 or r.status_code == 500:
                        self.df_urls.loc[url, "response"] = r.status_code
                        self.df_urls.loc[url, "found_char_imgs"] = False
                        print(f'response {r.status_code} attempt {attempts} , sleeping for 200ms , url {url}')
                        time.sleep(0.2)
                        attempts += 1

                    # if a bad status code then will skip retrying and move onto next url
                    else:
                        self.df_urls.loc[url, "response"] = r.status_code
                        print(f'bad status code {r.status_code}, ending request, url {url}')
                        attempts = 5

            except StopIteration:
                print("end of urls")
                complete = True

            except ValueError:
                time.sleep(0.0005)

    def download_images(self):

        # creating directory to save images to
        Path.mkdir(Path("./images"), exist_ok=True)

        complete = False

        while not complete:

            try:
                url_df = next(self.img_url_gen)

                # setting referral url, important or else server will reject direct request to image
                # this url must be a url that has the requested image embedded in

                ref_url = url_df["url"]

                img_urls = literal_eval(url_df["img_urls"])

                for img_url in img_urls:

                    attempts = 1

                    # will repeat the request 5 times if the request times out

                    while attempts < 5:

                        r = requests.get(img_url, cookies=self.cookies, headers={'referer': ref_url}, stream=True)

                        if r.status_code == 200:

                            try:
                                with PIL.Image.open(r.raw) as img:
                                    img.save(f'./images/{img_url.split("/")[-1]}')

                                print(f'img {img_url} saved successfully')
                                attempts = 5
                            except:
                                print(f'error {sys.exc_info()[0]} saving image {img_url}')

                        elif r.status_code == 408 or r.status_code == 503 or r.status_code == 504 or r.status_code == 500:
                            print(f'response {r.status_code} attempt {attempts} , sleeping for 200ms , url {img_url}')
                            time.sleep(0.2)
                            attempts += 1

                        else:
                            print(f'bad status code {r.status_code}, abandoning, url {img_url}')
                            attempts = 5

            except StopIteration:
                print("end of urls")
                complete = True

            except ValueError:
                time.sleep(0.0005)
