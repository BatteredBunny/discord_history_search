from selenium import webdriver

from datetime import timedelta
from datetime import datetime
from dateutil import relativedelta

import numpy as np
import pandas as pd

import time
import os
import calendar

from dotenv import load_dotenv

load_dotenv()

def progressBar(current, total, barLength = 20):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))

    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')

def raw_search(search_term, browser):

    # Opens search box
    i = 0
    while i == 0:
        try:
            browser.find_element_by_css_selector('.search-36MZv-').click()
            i = 1
        except:
            continue

    search_box = browser.find_element_by_css_selector('.notranslate')
    
    # Types search term in search box
    search_box.send_keys(search_term)
    search_box.send_keys('\ue007')

    search_fin = 'Searching…'

    while search_fin == 'Searching…':
        try:
            search_fin = browser.find_element_by_xpath("/html/body/div/div[2]/div/div[2]/div/div/div/div[2]/div[2]/div[2]/section/div[1]/div[1]/div").text
        except:
            time.sleep(float(os.environ.get("RATELIMIT")))

    result = search_fin

    # Closes search box for next command
    close_search_box = browser.find_element_by_css_selector('.icon-38sknP')
    close_search_box.click()

    if result == 'No Results':
        result = 0
    elif ' Results' in result:
        result = result.replace(' Results', '').replace(',','')
    elif ' Result' in result:
        result = result.replace(' Result', '').replace(',','')

    return result

def search_months(search_term, start_date, end_date, browser):
    timer_start = time.perf_counter()

    results_array = []

    print("Searching '" + search_term + "'")

    month_dates = get_month_dates(start_date, end_date)
    showcase_dates = []
    progress_bar_index = 0
    for months in month_dates:

        fixed = datetime.strptime(months[0], "%Y-%m-%d") + relativedelta.relativedelta(days=1)
        showcase_dates.append(str(fixed.year) + "-" + str(fixed.month))
    
        result = raw_search('after: ' + months[0] + ' before: ' + months[1] + ' ' + search_term, browser)

        results_array.append(result)

        progressBar(progress_bar_index, len(month_dates))
        progress_bar_index += 1

    results_data = np.array(results_array)
    month_data = np.array(showcase_dates)

    if search_term == '':
        data = {
            "months": month_data,
            "messages": results_data
        }
    else:
        data = {
            "months": month_data,
            search_term: results_data
        }

    dataframe = pd.DataFrame(data)

    dataframe.to_csv('results/month_results_' + search_term + '.csv', index=False)

    print("Finished searching '" + search_term + "'               ")
    print("Took " + str(int(time.perf_counter() - timer_start)) + " seconds to complete.\n")

def search_days(search_term, start_date, end_date, browser):
    timer_start = time.perf_counter()

    results_array = []

    print("Searching '" + search_term + "'")

    day_dates = get_day_dates(start_date, end_date)

    progress_bar_index = 0
    for certain_date in day_dates:
        result = raw_search('during:' + certain_date + ' ' + search_term, browser)

        results_array.append(result)

        progressBar(progress_bar_index, len(day_dates))
        progress_bar_index += 1

    results_data = np.array(results_array)
    day_data = np.array(day_dates)

    if search_term == '':
        data = {
            "messages": results_data,
            "date": day_data
        }
        
    else:
        data = {
            search_term: results_data,
            "days": day_data
        }

    dataframe = pd.DataFrame(data)

    dataframe.to_csv('results/day_results_' + search_term + '.csv', index=False)

    print("Finished searching '" + search_term + "'               ")
    print("Took " + str(int(time.perf_counter() - timer_start)) + " seconds to complete.\n")

def get_month_dates(start_date, end_date):
    startdate = datetime.strptime(start_date, "%Y-%m-%d")
    enddate = datetime.strptime(end_date, "%Y-%m-%d")

    return_dates = []

    while startdate.year != enddate.year or startdate.month != enddate.month:
        last_day = calendar.monthrange(startdate.year, startdate.month)

        startdate = datetime(startdate.year, startdate.month, last_day[1])
        secondstartdate = startdate + relativedelta.relativedelta(day=1, months=2)

        finaldate1 = str(startdate.year) + "-" + str(startdate.month) + "-" + str(startdate.day)
        finaldate2 = str(secondstartdate.year) + "-" + str(secondstartdate.month) + "-" + str(secondstartdate.day)

        return_dates.append([finaldate1, finaldate2])

        startdate = startdate + relativedelta.relativedelta(months=1)
    return return_dates

def get_day_dates(start_date, end_date):
    startdate = datetime.strptime(start_date, "%Y-%m-%d")
    enddate = datetime.strptime(end_date, "%Y-%m-%d")

    day_dates = []

    while startdate.year != enddate.year or startdate.month != enddate.month or startdate.day != enddate.day:
        finaldate = str(startdate.year) + "-" + str(startdate.month) + "-" + str(startdate.day)
        day_dates.append(finaldate)

        startdate = startdate + relativedelta.relativedelta(days=1)
    return day_dates

def search(serverID, search_term, search_type, start_date, end_date):
    browser = webdriver.Firefox()
    browser.get('https://discord.com/channels/' + str(serverID) + '/')

    EMAIL_FIELD = browser.find_element_by_css_selector('.inputField-4g7rSQ')
    PASSWORD_FIELD = browser.find_element_by_css_selector('.block-egJnc0 > div:nth-child(2) > div:nth-child(2) > input:nth-child(1)')
    SUBMIT_BUTTON = browser.find_element_by_css_selector('button.marginBottom8-AtZOdT')

    EMAIL_FIELD.send_keys(os.environ.get("LOGIN"))
    PASSWORD_FIELD.send_keys(os.environ.get("PASSWORD"))
    SUBMIT_BUTTON.click()

    if search_type == 'days':
        search_days(search_term, start_date, end_date, browser)

    elif search_type == 'months':
        search_months(search_term, start_date, end_date, browser)

    else:
        print("Wrong search type, you can choose from \"days\" and \"months\"")

    browser.close()
