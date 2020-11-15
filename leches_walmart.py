# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 13:41:16 2020

@author: DARRI002
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.keys import Keys
import os
import csv
import time


PROJECT_ROOT = os.path.abspath(os.path.dirname('__file__'))
DRIVER_BIN = os.path.join(PROJECT_ROOT, 'geckodriver')

driver = webdriver.Firefox(executable_path=DRIVER_BIN)
driver.get("https://super.walmart.com.mx/lacteos/leche/cat120096")

time.sleep(5)
driver.find_element_by_class_name('icon_icon__2ewVW').click()
driver.find_element_by_css_selector('[alt="Leche Saborizada "]').click()
time.sleep(5)
driver.find_element_by_class_name('header_headerDesktop__ZdGAa').click()

found = False
while found == False:
    try:
        driver.find_element_by_class_name("grid_loader__2VUr8")
    except Exception:
        driver.find_element_by_class_name('scroll-to-top_container__3vGV6').send_keys(Keys.PAGE_DOWN)
        time.sleep(5)
        found = False
    else:
        try:
            if driver.find_element_by_class_name("grid_loader__2VUr8").get_attribute('textContent') == 'No hay más productos':
                found = True
        except Exception:
            driver.find_element_by_class_name('scroll-to-top_container__3vGV6').send_keys(Keys.PAGE_DOWN)
            time.sleep(5)
            found = False
soup = bs(driver.page_source, "html.parser")


#This method stores specific information of a html code of a website in a list.
def code(extraction, tag:str, atrib:str, atribname:str):
    dynamic_text = extraction.find_all(tag, {atrib:atribname})
    article = []
    for i in dynamic_text:
        article.append(i.text.strip())
    return article

def excel (form):
    #The user is asked to name the csv file.
    name = input("Ingrese el nombre al que llamará a su archvivo: ")
    #A csv file is created.
    with open(name + '.csv','w+') as csvfile:
        #The headers of the csv file are pre-defined with the following lines
        writer = csv.DictWriter(
            csvfile, fieldnames=['ID', 'Productos', 'Precios', 'Promociones', 'UPC_Link'])
        writer.writeheader()
        '''
        Every row from the scraped dataframe is added to the
        csv file with the following loop.
        '''
        for p in form:
            writer.writerow(p)

items = code(soup, tag='div', atrib='class', atribname='product_name__1669g')
prices = code(soup, tag='p', atrib='class', atribname='price-and-promotions_currentPrice__XT_Iz text_text__1DYNl text_inline__2pX2N text_bold__1nsB7')
promotions = code(soup, tag='div', atrib='class', atribname='price-and-promotions_promotionsContainer__3XvPF')

#Extract upc
links = soup.find_all('div','product_name__1669g')
url = []
for div in links:
    anchors = div.find_all('a')
    url.extend(anchors)
upc_link = [l.get('href') for l in url]
    
#A list with a dictionary inside is created, which then will be saved in a csv file.
listed = [{'ID':index, 'Productos': items[index], 'Precios':prices[index], 'Promociones':promotions[index], 'UPC_Link':upc_link[index]} for index in range(len(items))]
excel(listed)

driver.quit()