# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_SNavigate.ipynb.

# %% auto 0
__all__ = ['path_to_browsermobproxy', 'url', 'username', 'passw', 'Navigator']

# %% ../nbs/00_SNavigate.ipynb 4
from fastcore.all import *
from selenium import webdriver    
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException, ElementNotSelectableException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup     
from browsermobproxy import Server
import pandas as pd
from retry import retry
from requests.exceptions import RequestException

import random
import time
import os
from dotenv import load_dotenv

# %% ../nbs/00_SNavigate.ipynb 5
from .parser import *

# %% ../nbs/00_SNavigate.ipynb 7
load_dotenv('/Volumes/Users/matu/pass.env')
path_to_browsermobproxy = "/Volumes/Users/matu/Documents/Xcode/browsermob-proxy-2.1.4/bin/"
url = 'https://www.linkedin.com/sales/login'
username = os.environ.get('SN_USER')
passw = os.environ.get('SN_PASS')

# %% ../nbs/00_SNavigate.ipynb 8
class Navigator():
    def __init__(self
                 ,headless=False, #Make the Chromium Headless or not
                 login = True #If should login inmediatly
                ) -> None:
        super().__init__( )
        self.server = Server(path_to_browsermobproxy
            + "browsermob-proxy", options={'port': 8090})
        self.server.start()
        self.proxy = self.server.create_proxy(params={"trustAllServers": "true"})
        chrome_options = Options()
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.headless=headless
        chrome_options.add_argument(f"--proxy-server={self.proxy.proxy}")
        self.driver = webdriver.Chrome('/Volumes/Users/matu/Documents/Xcode/chromedriver',options=chrome_options )
        if login:
            self.login()

# %% ../nbs/00_SNavigate.ipynb 9
@patch
def login(self:Navigator)->None:
        """
        Method to loging to Sales NAvigator from the webrDriver created
        """
        self.driver.get(url)
        time.sleep(random.randint(5,10))
        frame = self.driver.find_element(By.TAG_NAME, 'iframe')
        self.driver.switch_to.frame(frame)       # entering the username and password
        user = self.driver.find_element(By.ID, 'username')
        user.send_keys(username)
        password = self.driver.find_element(By.ID, 'password')
        password.send_keys(passw)
        singin = self.driver.find_element(By.TAG_NAME, 'button')
        singin.click()
        wait = WebDriverWait(self.driver, timeout=30, poll_frequency=2, ignored_exceptions=[ElementNotVisibleException, ElementNotSelectableException])
        wait.until(lambda d: d.find_element(By.CLASS_NAME,"homepage__right-column"))        

# %% ../nbs/00_SNavigate.ipynb 10
@patch
def close(self:Navigator)->None:
        """
        Close the Webdriver
        """
        self.server.stop()
        self.driver.close()

# %% ../nbs/00_SNavigate.ipynb 11
@patch    
def scroll_bottom(self:Navigator,
                      t_time: int=50, #Total time to spend in hte webpage
                      pause: int=1,#Time pause to scroll one more step
                      # total_steps:int = 10, #Number of steps to go down
                      move = True
                     )->None:
        """
        Method to scroll on the website
        """
        if not move:
            time.sleep(t_time)
            return
        total_steps = round(t_time/pause)
        # Get scroll height
        initial_height = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        stepsize = last_height/total_steps 
        while True:
            # Wait to load page
            time.sleep(pause)
            # Calculate new scroll height and compare with last scroll height
            self.driver.execute_script(f"window.scrollTo({0}, {initial_height});")
            initial_height += stepsize  # Scroll down to bottom
            if stepsize == 0:
                break
            elif initial_height >= last_height:
                break

# %% ../nbs/00_SNavigate.ipynb 12
@patch    
def next_page(self:Navigator, url=None)->bool:
        """
        Method to select button for next page, if exist
        """
        _ = self.proxy.new_har(f"list.har", options={'captureHeaders': False,'captureContent': True, 'captureBinaryContent': True})
        time.sleep(5)
        # First webpage will have url, so a HAR will be started and then url will be loaded
        if url:
            self.driver.get(url)
            time.sleep(5)
            next_b = self.driver.find_element(By.CLASS_NAME, 'artdeco-pagination__button--next')
            self.driver.execute_script(f"window.scrollTo({0}, {next_b.location_once_scrolled_into_view['y']});")    
            time.sleep(2)
            return True
        else:
            next_b = self.driver.find_element(By.CLASS_NAME, 'artdeco-pagination__button--next')
            self.driver.execute_script(f"window.scrollTo({0}, {next_b.location_once_scrolled_into_view['y']});")    
            time.sleep(2)
            
        if next_b.is_enabled():
            next_b.click()
            time.sleep(7)
            return True
        else:
            return False

# %% ../nbs/00_SNavigate.ipynb 13
@patch
def get_companies_ids(self:Navigator)->list:
        """
        Method to get companies Ids from a website
        """
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        companies = soup.find_all('a', attrs={'class':'lists-detail__view-company-name-link'})
        ids = [f"{company.get('href').split('/')[-1]}" for company in companies]
        return ids

# %% ../nbs/00_SNavigate.ipynb 14
@patch
def scrap_ids(self:Navigator,
                  url=None
                 )->list:
        """
        Methods to visit a url and get all companies ids from there
        """
        if url:
            self.driver.get(url)
        time.sleep(random.randint(5,15))            
        self.scroll_bottom(15)
        ids = self.get_companies_ids()
        if self.next_page():
            ids.extend(self.scrap_ids())
        return ids
    
    

# %% ../nbs/00_SNavigate.ipynb 15
@patch
def get_url(self:Navigator,
                url:str #Url string to visit and return the address
               )->str:
        """
        Method that return the url it is loading
        """
        self.driver.get(url)

# %% ../nbs/00_SNavigate.ipynb 16
@patch
def parse_search(self:Navigator,
                     url:str =None, #Url address for the search result
                     results:str ='leads' #Kind of record to scrap, it can be 'leads', 'accounts', 'skills', 'data'. Default 'leads'
                    )->pd.DataFrame:
        """
        Method that load the url and scrap the records present on it. It returns only the kind of record selected
        """
        reload = True

        #IF reload True (default is True)
        while reload :            
            leads, accounts, skills, data = parse_HAR(har = self.proxy.har)
            if leads.shape[0] == 0 or leads.loc[leads.lastName.isnull()].shape[0] > 0 or leads.loc[leads.lastName == ''].shape[0] > 0:
                print(f"Reloading with number of leads {leads.shape[0]}")
                self.driver.refresh()
                time.sleep(5)
            else:
                reload = False
        if results == 'leads':
            return leads
        elif results == 'accounts':
            return accounts
        elif results == 'skills':
            return skills
        elif results == 'data':
            return data
        else:
            return

# %% ../nbs/00_SNavigate.ipynb 17
@patch
def get_data(self:Navigator,
                 url:str = None, #Url to visit, 
                 results:str = 'leads', #Kind of record to return, it can be 'leads', 'accounts', 'skills' ,'data'. Default: leads
                 scrol_time:int=60, #Time that will take to scroll to the bottom. Default 60 seconds
                 scrol:bool = True #If its going to scroll at all. Defalt:True
                ):
        self.proxy.new_har(f"list.har", options={'captureHeaders': False,'captureContent': True, 'captureBinaryContent': True})
        if url:
            self.driver.get(url)
        else:
            self.driver.refresh()
        time.sleep(random.randint(4,5))
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        if soup.find_all(text='Too Many Requests') or soup.find_all(text='Sorry something went wrong'):
            print(f"Error to many Requests")
            self.close()
            raise RequestException()
        if soup.find_all(text='Page Not Found'):
            return None
        self.scroll_bottom(t_time=scrol_time) if scrol else time.sleep(scrol_time)
        leads, accounts, skills, data = parse_HAR(har = self.proxy.har)
        if results == 'leads':
            leads = leads.merge(skills, on='entityUrn', how='left') if skills.shape[0]>0 else leads
            if leads.shape[0] == 0:
                return None
            return leads
        elif results == 'accounts':
            return accounts
        elif results == 'skills':
            return skills
        elif results == 'data':
            return data
        else:
            return leads, accounts, skills, data
