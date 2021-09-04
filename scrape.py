from app.scrapeuniswap import scrapeUrl
from app.scrapeLogic import scrapeData
from time import sleep
import pandas as pd

url='https://info.uniswap.org/#/pools'


while True:
    scrapeUrl(url)
    scrapeData(url)
    sleepTime=3600
    print(f'Sleeping for {sleepTime} seconds')
    sleep(sleepTime)
    print('Done sleeping. Restarting scraping.')
