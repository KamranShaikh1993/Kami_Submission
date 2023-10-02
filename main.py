from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains


import csv
import logging

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

import time
import os
import requests
from io import StringIO

from deep_translator import GoogleTranslator
from datetime import datetime

#=================

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler("China_tenders.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

#=====================

def func_1():

    logger.info("Connecting path to geckodriver.exe")
    d = os.getcwd()
    d
    fname = os.path.join(d,'geckodriver.exe')

    #=====================

    # Load driver
    driver=webdriver.Firefox(executable_path=fname)

    driver_s = webdriver.Firefox(executable_path=fname)

    page_details = webdriver.Firefox(executable_path=fname)

    driver.maximize_window()
    logging.info('Firefox webdriver loaded')

    driver.get('https://www.chinabidding.com/en')
    #driver.get('http://www.censusindia.gov.in/')
    driver.implicitly_wait(5)


    #=====================

    # Loading url
    notice_url = driver.find_element(By.XPATH,'//*[@id="bidding"]/div[2]/div[3]/div/div[1]/div[1]/div/div/span[2]/a').get_attribute('href')  
    driver.implicitly_wait(5)
    driver_s.get(notice_url)  # loading a url
    logger.info("driver_s loaded")

    print('Done')

    #=====================


    name = []
    sector = []
    region_name = []
    state = []

    original_id = []
    aug_id = []
    notice_url = []
    description = []
    budget = []
    country_name = []
    country_code = []
    epublished_date = []
    bid_opening_date = []
    bid_submission_end_date = []

    #=====================

    # No. of pages to be scraped can be changed by changing the range of page.
    for page in range(1,3):

        try:
            for single_record in driver_s.find_elements(By.XPATH,'//*[@id="bidding"]/div[3]/div/div[3]/ul/li/div[1]'):
                title = single_record.find_element(By.XPATH,'a[1]').text
                name.append(title)
                print('title :- ',title)
        except:
            logger.info("Error in name")
            pass

        # sector
        try:
            for single_record in driver_s.find_elements(By.XPATH,'//*[@id="bidding"]/div[3]/div/div[3]/ul/li/div[3]'):
                industry = single_record.find_element(By.XPATH,'span[1]').text
                industry = industry.split('Industry：')[1].strip()
                sector.append(industry)
                print('sector :- ',industry)
        except:
            logger.info("Error in sector")
            pass



        # region_name
        try:
            for single_record in driver_s.find_elements(By.XPATH,'//*[@id="bidding"]/div[3]/div/div[3]/ul/li/div[3]'):
                region = single_record.find_element(By.XPATH,'span[2]').text
                region = translated = GoogleTranslator(source='auto', target='en').translate(region)
                region_name.append(region)

                # State
                state.append(region)

                print('region_name :- ',region)
        except:
            logger.info("Error in region_name ")
            pass

        #=============================


        # Loading url page_details
        try:
            i=1
            for single_record in driver_s.find_elements(By.XPATH,'//*[@id="bidding"]/div[3]/div/div[3]/ul/li/div[1]'):
                url = single_record.find_element(By.XPATH,'a[1]').get_attribute('href')
            #     print(url)
                notice_url.append(url)

                page_details.get(url)
                logger.info("page_details loaded ")
                notice_text = page_details.find_element(By.XPATH,'//*[@id="bidding"]/div[3]/div/div[4]').text

                notice_description = notice_text.split('1、Bidding Conditions')[0]
                description.append(notice_description)

                # original_id
                bid_id = notice_text.split("Bidding No:")[1].split('\n')[0]
                original_id.append(bid_id)

                # bid_id
                aug_id.append(bid_id)

                price = notice_text.split("Price of Bidding Documents:")[1].split('/')[1].split('\n')[0]
                budget.append(price)

                country = 'China'
                country_name.append(country)

                cntry_code = 'CN'
                country_code.append(cntry_code)

                epublished = notice_description.split("\n")[0].split('.com on')[1]

                date_str = epublished
                date_object = datetime.strptime(date_str, '%Y-%m-%d').date()
            #     print(type(date_object))
            #     print(date_object)  # printed in default format

                epublished_date.append(date_object)

                bid_opening_date.append(date_object)

                bid_submission = notice_text.split("Deadline for Submitting Bids/Time of Bid Opening (Beijing Time):")[1].split('\n')[0] 
                bid_submission = datetime.strptime(bid_submission, '%Y-%m-%d %H:%M').date()
                print(bid_submission)
                print(type(bid_submission))
                bid_submission_end_date.append(bid_submission)

            #     print(i)
            #     print(notice_text)
            #     print('\n')
            #     print('======================================')
            #     print('\n')
                i+=1
        except:
            logger.info("Error in loading page_details")
            pass

        #============================

        next_page = driver_s.find_element(By.XPATH,'//*[@id="pagerSubmitForm"]/li[10]/a').click()
        logger.info("Next Page")
        time.sleep(5)

        #============================
        page+=1

    driver.quit()    
    driver_s.quit()
    page_details.quit()

    # Create data frame
    logger.info("Creating DataFrame")
    df = pd.DataFrame({'original_id' : original_id,
                        'aug_id' : aug_id,
                        'name' : name ,
                       'description': description,
                       'notice_url': notice_url,
                       'budget' : budget,
                       'country_name' : country_name,
                       'country_code' : country_code,
                       'sector' : sector,
                       'region_name' : region_name,
                       'state' : state,
                       'epublished_date' : epublished_date,
                       'bid_opening_date' : bid_opening_date,
                       'bid_submission_end_date' : bid_submission_end_date

                      }, 
                        columns=['original_id','aug_id', 'name','description','notice_url','budget','country_name',
                                 'country_code','sector','region_name','state','epublished_date',
                                'bid_opening_date','bid_submission_end_date' ])
    # saving the dataframe
    df.to_csv('file1.csv')

    
if __name__=='__main__':
    func_1()

    