from IMDBscraper import IMDBScraper

# Entry point for the application
if __name__ == '__main__':
    scraper = IMDBScraper("https://www.imdb.com/chart/top/?ref_=nv_mv_250")
    scraper.scrape()
    scraper.writeData("data/movies.csv")

