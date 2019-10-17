import logging
import re
import requests
import urllib.robotparser
from urllib.parse import urlparse, urljoin
from corpus import Corpus

logger = logging.getLogger(__name__)

class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """

    def __init__(self, frontier):
        self.frontier = frontier
        self.corpus = Corpus()
        self.fetchedLinks = []
        self.foundTraps = []
        self.mostValidLinks = 0
        self.mostValidLinksURL

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """
        while self.frontier.has_next_url():
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched, len(self.frontier))
            url_data = self.fetch_url(url)
            validLinks = 0
            for next_link in self.extract_next_links(url_data):
                if self.corpus.get_file_name(next_link) is not None:
                    if self.is_valid(next_link):
                        validLinks += 1
                        self.frontier.add_url(next_link)
            if validLinks >= self.mostValidLinks:
                self.mostValidLinks = validLinks
                self.mostValidLinksURL = url_data["url"]
        self.generateAnalytics()

    def fetch_url(self, url):
        """
        This method, using the given url, should find the corresponding file in the corpus and return a dictionary
        containing the url, content of the file in binary format and the content size in bytes
        :param url: the url to be fetched
        :return: a dictionary containing the url, content and the size of the content. If the url does not
        exist in the corpus, a dictionary with content set to None and size set to 0 can be returned.
        """
        response = requests.get(url)
        url_data = {
            "url": url,
            "content": None,
            "size": 0
        }
        if requests.status_code == 200:
            size = len(response.content)
            url_data["content"] = response
            self.fetchedLink.append(url)

        return url_data

    def extract_next_links(self, url_data):
        # https://stackoverflow.com/questions/1080411/retrieve-links-from-web-page-using-python-and-beautifulsoup
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.

        Suggested library: lxml
        """
        outputLinks = []
        print("Base URL: ", url_data["url"])
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url((url_data["url"]))
        rp.read()
        dom = html.fromstring(url_data["content"])
        base_url = url_data["url"]
        #         print(url_data["url"])
        for link in dom.xpath('//a/@href'):
            if "http" in link:
                if rp.can_fetch("*", link):
                    outputLinks.append(link)
            else:
                print("Extra: ", link)
                if rp.can_fetch("*", urljoin(base_url, link)):
                    outputLinks.append(urljoin(base_url, link))
            print(outputLinks[-1])
        return outputLinks

    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
        """
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        try:
            return ".ics.uci.edu" in parsed.hostname \
                   and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                    + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                    + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                    + "|thmx|mso|arff|rtf|jar|csv" \
                                    + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

        except TypeError:
            print("TypeError for ", parsed)
            return False

    def generateAnalytics(self):
        countfile = open("analytics.txt", 'w')
        countfile.write(" The page with the most valid out links: " + str(self.mostValidLinksURL))
        countfile.write("\nThe number of out links: " + str(self.mostValidLinks))
        fetchedList = ""
        for x in range(len(self.fetchedLinks)):
            fetchedList += "\n" + self.fetchedLinks[x]
        countfile.write("\nDownloaded URLs: " + fetchedList)
        trapList = ""
        for x in range(len(self.foundTraps)):
            fetchedList += "\n" + self.foundTraps[x]
        countfile.write("\nIdentified traps: " + trapList)
