import pandas as pd
from sub_scraper import SubScraper
import threading


def img_url_gen(img_urls_df):

    # this geneator is used to yield a single row from the img_url dataframe to each subscraper

    index = 0

    while index < img_urls_df.index.size:
        yield img_urls_df.iloc[index]
        index +=1


def url_gen(urls_df):

    # this url generator is used to yield urls to sub_scrapers so they request different urls in parallel

    index = 0

    while index < urls_df.index.size:

        yield urls_df.iloc[[index]].index.values[0]
        index += 1

class MotherScraper:

    # This class is used as a controller for the sub_scraper class
    # This class oversees the feeding of urls and dataframes to the sub_scraper class
    # This class then executes the scrape method on all sub_scraper instances in parallel

    def __init__(self, urls_loc=None, img_urls_loc=None, workers=10):

        self.img_url_gen = None
        self.url_gen = None

        # number of subscrapers
        self.workers= workers

        if urls_loc:
            self.urls_df = pd.read_csv(urls_loc, index_col=["url"])

            self.urls_df["response"] = None
            self.urls_df["found_char_imgs"] = None
            self.urls_df["img_urls"] = None

            # creating url generator
            self.url_gen = url_gen(self.urls_df)

        if img_urls_loc:
            self.img_urls_df = pd.read_csv(img_urls_loc)

            # creating image url generator
            self.img_url_gen = img_url_gen(img_urls_df=self.img_urls_df)

        # initializing sub scrapers, this may take a few mins

        print("initializing sub scrapers, this may take a few mins")
        self.sub_scrapers = [SubScraper(url_gen=self.url_gen, df_urls=self.urls_df, img_url_gen=self.img_url_gen) for _ in range(0, self.workers)]

    def scrape(self):

        # this method is will execute the scrape methods of all sub_scrapers in parallel
        for scraper in self.sub_scrapers:
            threading.Thread(target=scraper.scrape).start()

        # writing the results to csv
        self.urls_df.to_csv("img_urls.csv", index="url")

    def download_images(self):

        # this method is will execute the download images methods of all sub_scrapers in parallel
        # images will be saved to ./images/
        for scraper in self.sub_scrapers:
            threading.Thread(target=scraper.download_images).start()

