from kivy.graphics import svg
from selenium import webdriver
from time import sleep, perf_counter
import pandas as pd

driverPath = 'app/webdriver/chromedriver'


def createFile():
    tokenFile = f"app/assets/tokenData_test03.csv"
    dict = {
        'S.No.': [],
        'Token': [],
        'Total Tokens Locked': [],
        'TVL': [],
        'Volume 24h': [],
        '24h Fees': [],
        'equation1': [],
        'equation2': [],
    }
    df = pd.DataFrame(dict)
    df.to_csv(tokenFile, index=False)
    return tokenFile





def scrapeData(url):
    csvfile = createFile()
    driver = webdriver.Chrome(driverPath)
    driver.get(url)
    sleep(3)
    try:
        getPages = driver.find_element_by_xpath(
            '//*[@id="root"]/div/div[2]/div[3]/div/div[4]/div/div[13]')
        pagination = getPages.find_elements_by_tag_name('div')
        pages = len(pagination)
        # print(pagination[3].text)
        #print(pages)
        print('Page ready for extracting!!')

        alltokens = []
        for _ in range(pages):

            getAllpools = driver.find_element_by_xpath(
                '//*[@id="root"]/div/div[2]/div[3]/div/div[4]/div')

            anchors = getAllpools.find_elements_by_tag_name('a')
        #    print(anchors[0].text)
            for anchor in anchors:
                sNo = anchor.text.split('\n')[0]
                href = anchor.get_attribute('href')
                alltokens.append(f'{sNo},{href}')
        #        print(href)
        #         alltokens.append(href)
        #        print(alltokens)
            pagination[-1].click()

        # print(alltokens)
        print(len(alltokens))

        df = pd.read_csv(csvfile)
        for i in alltokens:
            splitdata = i.split(',')
            sNo = splitdata[0]
            url = splitdata[1]

            print(f'{sNo} : {url}')
            driver.get(url)
            sleep(2)

            upBlock = driver.find_element_by_xpath(
                '//*[@id="root"]/div/div[2]/div[3]/div[2]/div[2]/div[1]/div[2]'
            )
            pairs = upBlock.find_elements_by_tag_name('a')
            # print(pairs[1].text)

            leftBlock = driver.find_element_by_xpath(
                '//*[@id="root"]/div/div[2]/div[3]/div[2]/div[3]/div[1]/div')
            # print(leftBlock.text)
            # print(len(allDivs))
            lockedTokens = leftBlock.find_elements_by_class_name('sc-brqgnP')
            totalToken = lockedTokens[0].text.split('\n')
            first = lockedTokens[1].text.split('\n')
            second = lockedTokens[2].text.split('\n')
            third = lockedTokens[3].text.split('\n')
            print('Writing Data in CSV...')
            df.loc[sNo, 'S.No.'] = sNo,
            df.loc[sNo, 'Token'] = f'{totalToken[1]}-{totalToken[3]}',
            df.loc[sNo,
                   'Total Tokens Locked'] = f'{totalToken[2]}/{totalToken[4]}',
            df.loc[sNo, 'TVL'] = f'{first[1]}',
            df.loc[sNo, 'Volume 24h'] = f'{second[1]}',
            df.loc[sNo, '24h Fees'] = f'{third[1]}',
            df.loc[sNo, 'equation1']= f'{pairs[0].text}',
            df.loc[sNo, 'equation2'] = f'{pairs[1].text}',
            df.to_csv(csvfile, index=False)
            print(f'Data successfully written in CSV file!')
            print(
                f'{totalToken[0]}\n{totalToken[1]}:{totalToken[2]},{totalToken[3]}:{totalToken[4]}')
            print(f'First: {first}')
            print(f'Second: {second}')
            print(f'Third: {third}')

    except Exception as e:
        print(e)
    finally:
        driver.quit()

