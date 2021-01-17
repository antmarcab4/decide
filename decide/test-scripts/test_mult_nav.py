'''
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from base.tests import BaseTestCase


class AdminTestCase(StaticLiveServerTestCase):

   
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
    
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
        
    
    def test_simpleCreateVoting(self):                    
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_elements_by_class_name('voting').send_keys('keys',Keys.ENTER)

        self.assertTrue(len(self.driver.find_elements_by_class_name('voting'))==1) 

    def test_simpleErrorCreateVoting(self):

        self.driver.get(f'{self.live_server_url}/admin/')      
        self.driver.find_element_by_id('voting-form').submit()
        self.driver.find_elements_by_class_name('voting').send_keys('keys',Keys.ENTER)

        self.assertTrue(len(self.driver.find_elements_by_class_name('errornote'))==1)'''
        
        
        
