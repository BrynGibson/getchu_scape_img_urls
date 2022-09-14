# getchu_scape_img_urls

Multi-threaded web scraper built using a combination of Selenium, Requests and LXML.

Selenium was used to intially open up a connection to getchu and click on an age verfication prompt, once age verification prompt had been accepted
the temporary verifcation cookies were serialized and passed into a Python program to be added into the headers of get requests used by Requests library. This allowed much faster scraping than using Selenium, and allowed for easier use of concurrency. 

Code is able to scrape image urls and download images from http://www.getchu.com

imgs_urls.csv contains 51916 character image urls collected from 9438 games / visual novels on getchu.com

A pretrained OpenCV Cascading classifier model was then used to indentify the face from the images and crop the images down to just the faces.
