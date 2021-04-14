from IMDBscraper import IMDBScraper

if __name__ == '__main__':
    scraper = IMDBScraper()
    scraper.scrape()
    scraper.writeData()

