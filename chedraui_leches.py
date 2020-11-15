# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 00:51:50 2020

@author: DARRI002
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 00:35:50 2020

@author: DARRI002
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.keys import Keys
import os
from urllib.parse import urljoin
import time
import csv
import pandas as pd



PROJECT_ROOT = os.path.abspath(os.path.dirname('__file__'))
DRIVER_BIN = os.path.join(PROJECT_ROOT, 'geckodriver.exe')

driver = webdriver.Firefox(executable_path=DRIVER_BIN)
#driver.get("https://www.chedraui.com.mx/Departamentos/S%C3%BAper/Despensa/Dulces-y-Chocolates/c/MC210509?sort=relevance&pageSize=48&q=%3Arelevance%3Acategory_l_4%3AMC21050902&show=Page&toggleView=grid#")
driver.get("https://www.chedraui.com.mx/Departamentos/S%C3%BAper/L%C3%A1cteos-y-Huevos/Leche/c/MC210401?q=%3Arelevance%3Acategory_l_4%3AMC21040106&page=0&toggleView=grid&pageSize=24")
elemento_busqueda = "product__list--price-panel"

element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, elemento_busqueda)))

item =[]
found = False
base_site = "https://www.chedraui.com.mx"

while found == False:
    
    try:
        #el= WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[class="arrow-icon"][rel="next"]')))
        boton = driver.find_element_by_css_selector('a[class="arrow-icon"][rel="next"]')
    except Exception:
        html = driver.page_source
        soup = bs(html, "html.parser")
        time.sleep(5)
        wait = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'name')))
        it = []
        items= soup.find_all('a', class_='name')
        items2=[it.append(urljoin(base_site,items[i]['href'].strip())) for i in range (0, len(items))]
        item.extend(it)
        break
    else:
        html = driver.page_source
        soup = bs(html, "html.parser")
        time.sleep(5)
        wait = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'name')))
        it = []
        items= soup.find_all('a', class_='name')
        items2=[it.append(urljoin(base_site,items[i]['href'].strip())) for i in range (0, len(items))]
        item.extend(it)
        found2 = False
        driver.find_element_by_class_name("pagination-bar-results").click()
        while found2 == False:
            try:
                boton = driver.find_element_by_css_selector('a[class="arrow-icon"][rel="next"]')
                boton.click()
                
            except Exception:
                try:
                    el2= WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'body-container')))
                    driver.find_element_by_class_name('body-container').send_keys(Keys.PAGE_DOWN)
                    found2 = False
                except:
                    try:
                        boton.click()
                        found2 = True
                    except:
                        break

        found = False
    print(items)
    print(len(item))

df = pd.read_excel('Links_leches.xlsx')
df['numero']=[int(df['Links'][x].split("/")[-1]) for x in range(0, len(df['Links']))]

df2 = pd.DataFrame(item, columns=['Links'])
df2['numero']=[int(df2['Links'][x].split("/")[-1]) for x in range(0, len(df2['Links']))]

dbf = df.append(df2,ignore_index=True)

unique_values = {dbf['numero'][x]:dbf['Links'][x] for x in range(0,len(dbf['Links']))}

item2 = list(unique_values.values())


upc = []
name =[]
price = []
promo = []
old_price = []

for i in range(len(item2)):
    driver.get(item2[i])
    html = driver.page_source
    soup = bs(html, "html.parser")
    try:
        upcs = soup.find('span', class_ = 'code').text
    except:
        upc.append(" ")
    else:
        upc.append(upcs)
        
    try:
        names = soup.find('div', class_ = 'product-details-name name').text
    except:
        name.append(" ")
    else:
        name.append(names)
    
    try:
        prices = soup.find('p', class_ = 'price price-colour-final-pdp').text.strip()
    except:
        price.append(" ")
    else:
        price.append(prices)
        
    try:
        promos = soup.find('p', class_ = 'promotion').text
    except:
        promo.append(" ")
    else:
        promo.append(promos)

    try:
        olds = soup.find('p', class_ = 'price price-colour-strike-pdp').text.strip()
    except:
        old_price.append(" ")
    else:
        old_price.append(olds)


def excel (form):
    #The user is asked to name the csv file.
    name = input("Ingrese el nombre al que llamará a su archvivo: ")
    #A csv file is created.
    with open(name + '.csv','w+') as csvfile:
        #The headers of the csv file are pre-defined with the following lines
        writer = csv.DictWriter(
            csvfile, fieldnames=['ID', 'Productos', 'Precios', 'Promociones', 'Old_Prices', 'UPC_Link', 'UPC'])
        writer.writeheader()
        '''
        Every row from the scraped dataframe is added to the
        csv file with the following loop.
        '''
        for p in form:
            writer.writerow(p)

listed = [{'ID':index, 'Productos': name[index], 'Precios':price[index], 'Promociones':promo[index], 'Old_Prices':old_price[index], 'UPC_Link':item2[index], 'UPC':upc[index]} for index in range(len(item2))]
excel(listed)
driver.quit()