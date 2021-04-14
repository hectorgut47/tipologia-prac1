import pandas as pd
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager

# Class to encapsulate the data for a movie
class Movie:

    def __init__(self, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15, a16, a17, a18):
        self.name = a1
        self.score = a2
        self.genre1 = a3
        self.genre2 = a4
        self.genre3 = a5
        self.duration = a6
        self.release = a7
        self.rating = a8
        self.country = a9
        self.language = a10
        self.sound = a11
        self.color = a12
        self.ratio = a13
        self.budget = a14
        self.gross = a15
        self.badReviews = a16
        self.neutralReviews = a17
        self.goodReviews = a18

    def to_dict(self):
        return {
            'name': self.name,
            'score': self.score,
            'genre1': self.genre1,
            'genre2': self.genre2,
            'genre3': self.genre3,
            'duration': self.duration,
            'release': self.release,
            'rating': self.rating,
            'country': self.country,
            'language': self.language,
            'sound': self.sound,
            'color': self.color,
            'ratio': self.ratio,
            'budget': self.budget,
            'gross': self.gross,
            'badReviews': self.badReviews,
            'neutralReviews': self.neutralReviews,
            'goodReviews': self.goodReviews
        }


# Class implementing the Scraper that connects to IMDB and retrieves information
# about the Top 250 movies
class IMDBScraper:

    def __init__(self):

        # The URL should always be the same
        self.url = "https://www.imdb.com/chart/top/?ref_=nv_mv_250"

        # Empty dataframe to fill in each run
        self.data = None

        # Parameters to be set in each run
        self.initTime = None
        self.endTime = None

    # Given a link, this function returns the corresponding Movie object
    @staticmethod
    def _getMovieFromLink(link):

        r = requests.get(link)
        if r.status_code != 200:
            exit(-1)
        soup = BeautifulSoup(r.content, "html.parser")

        name = soup.find("div", {"class": "title_wrapper"}).h1.get_text(strip=True).partition('(')[0]
        score = soup.find("span", {"itemprop": "ratingValue"}).get_text(strip=True)

        subtext = soup.find("div", {"class": "subtext"}).get_text(strip=True).split('|')

        # Rating not always present
        if len(subtext) == 4:
            rating = subtext[0]
            subtext.pop(0)
        else:
            rating = '#N/A'

        # Normally all movies have 3 genres, but not always
        genres = subtext[1].split(',')
        genre1 = genres[0]
        if len(genres) > 1:
            genre2 = genres[1]
        else:
            genre2 = '#N/A'
        if len(genres) > 2:
            genre3 = genres[2]
        else:
            genre3 = '#N/A'

        release = subtext[2].partition('(')[0].strip()

        # Duration information might only be available in the subtext. In that case, it needs conversion
        if soup.find('h4', string="Runtime:") is not None:
            duration = soup \
                .find('h4', string="Runtime:") \
                .find_next('time') \
                .get_text(strip=True).partition(' ')[0]
        else:
            durationText = re.sub('[^0-9 ]', '', subtext[0]).partition(' ')
            duration = int(durationText[0]) * 60 + int(durationText[2])

        # Some films do not provide Sound information
        if soup.find('h4', string="Sound Mix:") is not None:
            sound = soup\
                .find('h4', string="Sound Mix:")\
                .parent.find_all('a')
            sound = '|'.join([s.get_text(strip=True) for s in sound])
        else:
            sound = '#N/A'

        color = soup\
            .find('h4', string="Color:")\
            .find_next('a')\
            .get_text(strip=True)

        # Some films do not provide Aspect Ratio information
        if soup.find('h4', string="Aspect Ratio:") is not None:
            ratio = soup\
                .find('h4', string="Aspect Ratio:")\
                .next_sibling\
                .strip()
        else:
            ratio = '#N/A'

        country = soup\
            .find('h4', string="Country:") \
            .find_next('a') \
            .get_text(strip=True)

        language = soup\
            .find('h4', string="Language:") \
            .find_next('a') \
            .get_text(strip=True)

        # Some films do not provide Budget information
        if soup.find('h4', string="Budget:") is not None:
            budget = soup\
                .find('h4', string="Budget:")\
                .next_sibling\
                .strip().partition(' ')[0]
        else:
            budget = '#N/A'

        # Some films do not provide Gross Revenue information
        if soup.find('h4', string="Cumulative Worldwide Gross:") is not None:
            gross = soup\
                .find('h4', string="Cumulative Worldwide Gross:")\
                .next_sibling\
                .strip()
        else:
            gross = '#N/A'

        badReviews, neutralReviews, goodReviews = IMDBScraper._getMovieReviews(link + "reviews")

        return Movie(name, score, genre1, genre2, genre3, duration, release, rating,
                     country, language, sound, color, ratio, budget, gross, badReviews, neutralReviews, goodReviews)

    @staticmethod
    def _getMovieReviews(link):

        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(link)

        badReviews = 0
        neutralReviews = 0
        goodReviews = 0

        dropDown = Select(driver.find_element_by_name("ratingFilter"))

        for i in list(range(1, 11)):

            dropDown.select_by_value(str(i))

            soup = BeautifulSoup(driver.page_source, "html.parser")
            nReviews = soup.find("div", {"class": "header"}).div.span.getText(strip=True).partition(" ")[0]

            if i < 5:
                badReviews += int(nReviews.replace('.', ''))
            elif i < 8:
                neutralReviews += int(nReviews.replace('.', ''))
            else:
                goodReviews += int(nReviews.replace('.', ''))

            dropDown = Select(driver.find_element_by_name("ratingFilter")) # Needs to be re-selected, Javascript removes it

        driver.quit()

        return badReviews, neutralReviews, goodReviews

    # This function actually does the scraping job
    def scrape(self):

        self.initTime = datetime.now()
        print("Beginning scraping of IMDB's Top 250 Movies.")
        print("Start time:", self.initTime.strftime("%d %b %Y, %H:%M:%S"))

        r = requests.get(self.url)
        if r.status_code != 200:
            exit(-1)

        soup = BeautifulSoup(r.content, "html.parser")

        links = [link.get('href') for link in soup.find_all('a')]
        topShowLinks = ['https://www.imdb.com' + link for link in links
                        if link is not None and link.startswith('/title/tt')]
        topShowLinks = list(dict.fromkeys(topShowLinks))  # All links are gotten duplicated, we need to remove them
        if len(topShowLinks) != 250:
            exit(-2)

        topShowObjects = [IMDBScraper._getMovieFromLink(link) for link in topShowLinks]
        self.data = pd.DataFrame.from_records([show.to_dict() for show in topShowObjects])

        self.endTime = datetime.now()
        print("Finished scraping of IMDB's Top 250 Movies.")
        print("Finish time:", self.endTime.strftime("%d %b %Y, %H:%M:%S"))
        print("Elapsed time:", self.endTime - self.initTime)

    def writeData(self):

        print("Beginning data dump to file data/movies.csv.")
        self.data.to_csv('data/movies.csv', index=False)
        print("Data dump finished.")

