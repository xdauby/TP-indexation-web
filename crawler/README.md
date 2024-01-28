
# Project Title
Author : Antoine De Paepe

## Brief description of ```Crawler```'s methods :

* ```parse_html``` : Given an url, get all the links on a webpage. 

* ```get_robots_path``` : Given an url, give the robots.txt path.

* ```is_url_allowed_by_robots``` : Check if an url is crawlable. Need to specify robots.txt path.

* ```get_n_allowed_url_in_border``` : Get self.max_url_by_pages (or less) UNIQUE links founded on the webpage with url (main_url) that are not in self.crawled or 
            in self.frontier.
            Need to specify the main url robot (main_url_robot) to check if links founded on the webpage are 
            crawlable.

* ```get_sitemaps_url``` : Given the path of a robots.txt, get all xml links (sitemaps).

* ```get_links_in_sitemaps_from_url``` : Given an url (.xml), get all the links on a sitemap by parsing the xml.

* ```get_m_allowed_url_in_sitemaps``` : Get self.max_url_by_sitemaps (or less) UNIQUE links founded on the sitemaps indicated on robot.txt (at address main_url_robot) 
            that are not in self.crawled or self.frontier. Need to specify the main url robot (main_url_robot). 

* ```run``` : Implementation of a crawler. The (self.seed) is the url of the first webpage, (self.max_crawled_url) is the
        maximum number of crawled url to return, (self.politeness_criterion) is the politeness time and (self.max_links_by_pages) is the maximum links by pages that we are allow to crawl. This function is extremely well commented, please check it.

## Brief description of functions :

* ```create_database_and_table``` : Create the needed database. 

* ```update_age``` : Set the current date as age for a given url, and save it in the database (the url is hashed before saved). 

* ```save``` : Save a list in .txt file. 

## What has been implemented

```Basics``` have been implemented, as well as ```Bonus 1``` and ```Bonus 3```.

## How to use :


To run the program :


`pip install requirements.txt`

Default args :

`seed` : "https://ensai.fr"

`max_crawled_url` : 50

`politeness_criterion` : 3 

`max_url_by_pages` : 5

`explore_sitemaps` : False

`max_url_by_sitemaps` : 0

run python code

`python3 main.py`

with different parameters

`python3 main.py --seed "https://ensai.fr" --max_crawled_url 100 --politeness_criterion 1.5 --max_url_by_pages 5 --explore_sitemaps True --max_url_by_sitemaps 5`




