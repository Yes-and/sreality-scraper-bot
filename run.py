from scraper import ScrapeBot

my_url = "https://www.sreality.cz/hledani/pronajem/byty/praha?velikost=pokoj,1%2Bkk,1%2B1,2%2Bkk,2%2B1,3%2Bkk,3%2B1,4%2Bkk,4%2B1,5%2Bkk,5%2B1,6-a-vice,atypicky"
newBot = ScrapeBot(my_url)
newBot.startDriver(False)
newBot.scrape(1,1)
