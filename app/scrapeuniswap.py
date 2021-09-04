from selenium import webdriver
from time import sleep, perf_counter
import pandas as pd
import re
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
import datetime

driverPath = 'app/webdriver/chromedriver'
pool_address=[]

def createFile():
    tokenFile = f"app/assets/tokenData_test06.csv"
    dict = {
        'pool_address': [],
        'token0': [],
        'token1': [],
        'token0Price': [],
        'token1Price': [],
        'totalValueLockedToken0': [],
        'totalValueLockedToken1': [],
        'date':[],
    }
    df = pd.DataFrame(dict)
    df.to_csv(tokenFile, index=False)
    return tokenFile

def scrapeUrl(url):
    csvfile = createFile()
    driver = webdriver.Chrome(driverPath)
    driver.get(url)
    sleep(3)
    try:
        getPages = driver.find_element_by_xpath(
            '//*[@id="root"]/div/div[2]/div[3]/div/div[4]/div/div[13]')
        pagination = getPages.find_elements_by_tag_name('div')
        pages = len(pagination)
        print('Page ready for extracting!!')
        alltokens = []
        for _ in range(pages):
            getAllpools = driver.find_element_by_xpath(
                '//*[@id="root"]/div/div[2]/div[3]/div/div[4]/div')
            anchors = getAllpools.find_elements_by_tag_name('a')
            for anchor in anchors:
                sNo = anchor.text.split('\n')[0]
                href = anchor.get_attribute('href')
                alltokens.append(f'{sNo},{href}')
            pagination[-1].click()

        # print(alltokens)
        print(len(alltokens))

        df = pd.read_csv(csvfile)
        for i in alltokens:
            splitdata = i.split(',')
            sNo = splitdata[0]
            url = splitdata[1]
            text=re.findall('https://info.uniswap.org/#/pools/(.+)', url)
            pool_address.append(text[0])

        print(pool_address)

    except Exception as e:
        print(e)
    finally:
        driver.quit()
    count = 0
    for m in range(len(pool_address)):
        sample_transport=RequestsHTTPTransport(
            url='https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
            verify=True,
            retries=5,
        )
        client = Client(
            transport=sample_transport
        )
        query = gql('''
        query {	 ticks(
              first: 1000
              skip: 0
              where: {poolAddress: '''+"\""+pool_address[m]+"\""+''' 
                }
            ) {
            pool
          {
                id,
            token0{
              symbol
            },
            token1{
              symbol
            },
            token0Price,
            token1Price,
            totalValueLockedToken0,
            totalValueLockedToken1,
          }
            }
          }
        ''')
        response = client.execute(query)
        for i in range(len(response['ticks'])):
            df.loc[count,'pool_address']=response['ticks'][i]['pool']['id']
            df.loc[count,'token0']=response['ticks'][i]['pool']['token0']['symbol']
            df.loc[count,'token1']=response['ticks'][i]['pool']['token1']['symbol']
            df.loc[count,'token0Price']=response['ticks'][i]['pool']['token0Price']
            df.loc[count,'token1Price']=response['ticks'][i]['pool']['token1Price']
            df.loc[count,'totalValueLockedToken0']=response['ticks'][i]['pool']['totalValueLockedToken0']
            df.loc[count,'totalValueLockedToken1']=response['ticks'][i]['pool']['totalValueLockedToken1']
            df.loc[count,'date']=datetime.datetime.now()
            count=count+1

    print(df)
    df.to_csv(csvfile, index=False)