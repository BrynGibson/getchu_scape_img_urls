import pandas as pd
from sub_scraper import SubScraper
import threading


def url_gen(urls_df):

    # this url generator is used to yield urls to sub_scrapers so they request different urls in parallel

    index = 0

    while index < urls_df.index.size:

        yield urls_df.iloc[[index]].index.values[0]
        print(index)
        index += 1

    # for testing without using full dataset

    # while index < 100:
    #
    #     index += 1


class MotherScraper:

    # This class is used as a controller for the sub_scraper class
    # This class oversees the feeding of urls and dataframes to the sub_scraper class
    # This class then executes the scrape method on all sub_scraper instances in parallel

    def __init__(self, urls_loc):
        self.urls_df = pd.read_csv(urls_loc, index_col=["url"])

        self.urls_df["response"] = None
        self.urls_df["found_char_imgs"] = None
        self.urls_df["img_urls"] = None

        self.url_gen = url_gen(self.urls_df)

        # initializing sub scrapers, this may take a few mins

        self.sub_scrapers = [SubScraper(self.url_gen, self.urls_df) for i in range(0, 20)]

    def scrape(self):

        # this method is will execute the scrape methods of all sub_scrapers in parallel
        for scraper in self.sub_scrapers:
            threading.Thread(target=scraper.scrape()).start()

        # writing the results to csv
        self.urls_df.to_csv("img_urls.csv", index="url")