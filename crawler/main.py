import urllib.request
import urllib.robotparser
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from typing import List
import time
import sqlite3
from datetime import datetime
import urllib3
import xmltodict
import requests
import argparse
import hashlib
import re

class Crawler:
    """
    Crawler implementation.
    """

    def __init__(self, 
                 seed : str, 
                 max_crawled_url : int,
                 politeness_criterion : float,
                 max_url_by_pages : int,
                 explore_sitemaps : bool,
                 max_url_by_sitemaps : int) -> None:
        """
        seed : str :: Seed url
        max_crawled_url : int :: Maximum number of crawled pages.
        politeness_criterion : float :: Politeness criterion.
        max_url_by_pages : int :: Maximum links to add in frontier for each webpages.
        explore_sitemaps : bool :: True if you want to explore sitemaps, False otherwise.
        max_url_by_sitemaps : int :: Maximum urls to add in frontier for urls in sitemaps.
        """
        self.seed = seed
        self.crawled = set([seed])
        self.frontier = [] 
        self.max_crawled_url = max_crawled_url
        self.politeness_criterion = politeness_criterion
        self.max_url_by_pages = max_url_by_pages
        self.explore_sitemaps = explore_sitemaps
        self.max_url_by_sitemaps = max_url_by_sitemaps


    def parse_html(self, url : str) -> List[str]:
        """ Given an url, get all the links on a webpage. """
        links = []
        try:
            response = urllib.request.urlopen(url)
            html = response.read()
            parsed_html = BeautifulSoup(html, 'html.parser')
            anchor_tags = parsed_html.find_all('a')
            for tag in anchor_tags:
                href = tag.get('href')
                if href and href.startswith("http"):
                    links.append(href)
        except:
            links = []

        return links
    
    def get_robots_path(self, url : str) -> List[str]:
        """ Given an url, give the robots.txt path. """
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        return robots_url

    def is_url_allowed_by_robots(self, url : str, url_robot : str) -> bool:
        """ Check if an url is crawlable. Need to specify robots.txt path. """ 
        rp = urllib.robotparser.RobotFileParser(url_robot)
        rp.set_url(url_robot)
        rp.read()
        return rp.can_fetch("*", url)

    def get_n_allowed_url_in_border(self,
                                    main_url : str,
                                    main_url_robot : str) -> List[str]:
        """ Get self.max_url_by_pages (or less) UNIQUE links founded on the webpage with url (main_url) that are not in self.crawled or 
            in self.frontier. Need to specify the main url robot (main_url_robot) to check if links founded on the webpage are 
            crawlable.
        """
        url_to_return = set([])
        # Politeness criterion : wait politeness_criterion secs before crawling the page
        time.sleep(self.politeness_criterion)
        url_in_border = self.parse_html(main_url)

        for url in url_in_border:
            if ((url not in self.crawled) and (url not in self.frontier) and self.is_url_allowed_by_robots(url=url, url_robot=main_url_robot)):    
                url_to_return.add(url)  
                if len(url_to_return) >= self.max_url_by_pages:
                    return url_to_return
        return url_to_return


    def get_sitemaps_url(self, url_robots : str) -> List[str]:
        """ Given the path of a robots.txt, get all xml links (sitemaps). """
        try:
            # Make an HTTP request to get the robots.txt content
            response = requests.get(url_robots)
            response.raise_for_status()  # Raise an exception for bad responses
            # Extract sitemap links using a regular expression
            sitemap_links = re.findall(r'Sitemap:\s*(.*?)(?:\r?\n|$)', response.text, re.IGNORECASE)
            return sitemap_links
        except Exception as e:
            return []

    def get_links_in_sitemaps_from_url(self, url : str) -> List[str]:
        """ Given an url (.xml), get all the links on a sitemap by parsing the xml. """
        try:
            https = urllib3.PoolManager()
            response = https.request('GET', url)
            sitemap = xmltodict.parse(response.data)
            links = [link['loc'] for link in sitemap['urlset']['url']]
            return links
        except Exception as e:
            return [] 

    def get_m_allowed_url_in_sitemaps(self, main_url_robot : str) -> List[str]:
        """ Get self.max_url_by_sitemaps (or less) UNIQUE links founded in the sitemaps indicated on robot.txt (at address main_url_robot) 
            that are not in self.crawled or self.frontier. Need to specify the main url robot (main_url_robot). 
        """
        url_to_return = set([])
        # Politeness criterion : wait politeness_criterion secs before crawling the page
        time.sleep(self.politeness_criterion)
        xml_urls = self.get_sitemaps_url(main_url_robot)

        for xml_url in xml_urls:
            urls_sitemap = self.get_links_in_sitemaps_from_url(xml_url)
            for url_sitemap in urls_sitemap:
                if (url_sitemap not in self.crawled) and (url_sitemap not in self.frontier):    
                    url_to_return.add(url_sitemap)  
                    if len(url_to_return) >= self.max_url_by_sitemaps:
                        return url_to_return
        return url_to_return
    

    def run(self) -> List[str]:
        """ 
        Implementation of a crawler. The (self.seed) is the url of the first webpage, (self.max_crawled_url) is the
        maximum number of crawled url to return, (self.politeness_criterion) is the politeness time and (self.max_url_by_pages)
        is the maximum links by pages that we are allow to crawl. If (self.explore_sitemaps) is True, get (self.max_url_by_sitemaps) urls
        from the sitemaps.
        """
    
        # Get robot.txt path on the seed website
        robots_txt_path = self.get_robots_path(self.seed)
        
        # Here, we parse the current url, i.e, the seed (check the function docs) to get n links inside the page 
        # (or less if so)
        self.frontier += self.get_n_allowed_url_in_border(main_url=self.seed, 
                                                          main_url_robot=robots_txt_path)

        self.display_info()

        # Conditions : we keep running the program if the lenght of the current crawled url is <= max_crawled_url
        # Or if the frontier is not empty
        while (len(self.crawled) < self.max_crawled_url) and (len(self.frontier) > 0):

            temp_frontier = self.frontier.copy()         
            # we go throught the urls that are waiting int the frontier
            for url in temp_frontier:
                
                # Get robot.txt path on the current website
                robots_txt_path = self.get_robots_path(url)

                # If we decided to explore sitemaps
                if self.explore_sitemaps:
                    urls_to_add_in_frontier = self.get_m_allowed_url_in_sitemaps(main_url_robot=robots_txt_path)
                    self.frontier += list(urls_to_add_in_frontier)
                  
                # Here, we parse the current url website (check the function docs) to get n links inside the page (or less if so)
                urls_to_add_in_frontier = self.get_n_allowed_url_in_border(main_url=url,
                                                                           main_url_robot=robots_txt_path)

                # Add to frontier
                self.frontier += list(urls_to_add_in_frontier)
                
                # Move from frontier to crawled
                self.frontier.remove(url)
                self.crawled.add(url)

                # Update age of the pages (in an SQL database)
                update_age("age_db", url)

                self.display_info()

                if (len(self.crawled) >= self.max_crawled_url) or (len(self.frontier) == 0):
                    break

        return self.crawled

    def display_info(self) -> None:
        """ Display infos. """
        print(f'%%% {len(self.crawled)} / {self.max_crawled_url} crawled %%%')



### SLQ and backup related ### 

def create_database_and_table(database_name : str) -> None:
    conn = sqlite3.connect(f'{database_name}.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS track_ages (
    hash_url TEXT PRIMARY KEY,
    age DATETIME
    );
    """)
    conn.commit()
    return

def update_age(database_name:str, url:str) -> None:
    """ Set the current date as age for url (url) """
    
    data = {"hash_url" : hashlib.sha256(url.encode()).hexdigest(), 
            "age" : datetime.now()}
    conn = sqlite3.connect(f'{database_name}.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO track_ages (hash_url, age)
    VALUES (:hash_url, :age)
    ON CONFLICT (hash_url) DO UPDATE SET age = :age;
    """, data)
    conn.commit()
    return

def save(urls : List[str], file : str = 'crawled_webpages.txt') -> None:
    ''' Save a list in a .txt file. '''
    with open(file, 'w') as fp:
        for item in urls:
            fp.write("%s\n" % item)
    return 

### --- ###


def main() -> None:
    
    # creat SQL database
    create_database_and_table(database_name="age_db")

    #  Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', '-s', default="https://ensai.fr")
    parser.add_argument('--max_crawled_url', '-mcu', default=50)
    parser.add_argument('--politeness_criterion', '-pc', default=3)
    parser.add_argument('--max_url_by_pages', '-mbp', default=5)
    parser.add_argument('--explore_sitemaps', '-es', default="False")
    parser.add_argument('--max_url_by_sitemaps', '-mbs', default=0)
    args = parser.parse_args()

    # Retrieve args
    seed = args.seed
    max_crawled_url = int(args.max_crawled_url)
    politeness_criterion = float(args.politeness_criterion)
    max_url_by_pages = int(args.max_url_by_pages)
    explore_sitemaps = eval(args.explore_sitemaps)
    max_url_by_sitemaps = int(args.max_url_by_sitemaps)
    
    print(" --------------------- ")
    print(" Parameters: ")
    print(f"seed : {seed}")
    print(f"max_crawled_url : {max_crawled_url}")
    print(f"politeness_criterion : {politeness_criterion}")    
    print(f"max_url_by_pages : {max_url_by_pages}")
    print(f"explore_sitemaps : {explore_sitemaps}")  
    print(f"max_url_by_sitemaps : {max_url_by_sitemaps}")  
    print(" --------------------- ")
    
    print("Crawler is setting up ...")

    # init the crawler
    crawler = Crawler(seed = seed, 
                      max_crawled_url = max_crawled_url,
                      politeness_criterion = politeness_criterion,
                      max_url_by_pages = max_url_by_pages,
                      explore_sitemaps = explore_sitemaps,
                      max_url_by_sitemaps = max_url_by_sitemaps)

    # Crawl
    crawled = crawler.run()
    
    # save the result in crawled_webpages.txt
    save(crawled)

if __name__ == "__main__":
    main()