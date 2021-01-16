from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from base import mods
from census.models import Census
from voting.models import Question
from voting.models import QuestionOption
from voting.models import Voting
from mixnet.models import Auth
from django.conf import settings

from base.tests import BaseTestCase
import time

class AdminTestCase(StaticLiveServerTestCase):


    def setUp(self):

        self.client = APIClient()
        mods.mock_query(self.client)

        voter1 = User(username='voter', id="4")
        voter1.set_password('voter')
        voter1.save()

        admin = User(username='admin', is_staff=True)
        admin.set_password('admin')
        admin.is_superuser = True
        admin.save()

        q = Question(desc='Preferences question', preferences=True)
        q.save()   
        
        for i in range(2):
            optPref = QuestionOption(question=q, option='option {}'.format(i+1), number='{}'.format(i+1))
            optPref.save()
        v = Voting(name='test voting', id="2")
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q)
        v.save()

        census = Census(voting_id=2, voter_id=4)

        census.save()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.client = None
        self.v=None
        self.q=None

    def start_voting(self):                    
        self.driver.get(f'{self.live_server_url}/admin/voting/voting')
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()

    def login1(self):
        self.driver.get(f'{self.live_server_url}/admin')
        self.driver.find_element_by_id('id_username').send_keys("admin")
        self.driver.find_element_by_id('id_password').send_keys("admin",Keys.ENTER)

    def login2(self):
        self.driver.get(f'{self.live_server_url}/booth/2')
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("voter")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("voter")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
  
    def test_vote_pref(self):
        self.login1()
        self.start_voting()
        self.login2()
        time.sleep(1)
        dropdown = self.driver.find_element(By.ID, "__BVID__11")
        dropdown.find_element(By.ID, "q1").click()
        dropdown = self.driver.find_element(By.ID, "__BVID__12")
        dropdown.find_element(By.ID, "q2").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.assertEquals(len(self.driver.find_elements(By.CSS_SELECTOR, "div > ul > li")), 0)

    def test_vote_pref_mod_wrong(self):
        self.login1()
        self.start_voting()
        self.login2()
        time.sleep(1)
        dropdown = self.driver.find_element(By.ID, "__BVID__11")
        dropdown.find_element(By.ID, "q1").click()
        dropdown = self.driver.find_element(By.ID, "__BVID__12")
        dropdown.find_element(By.ID, "q1").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.assertEquals(len(self.driver.find_elements(By.CSS_SELECTOR, "div > ul > li")), 1)
        
        dropdown = self.driver.find_element(By.ID, "__BVID__11")
        dropdown.find_element(By.ID, "q1").click()
        dropdown = self.driver.find_element(By.ID, "__BVID__12")
        dropdown.find_element(By.ID, "q2").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.assertEquals(len(self.driver.find_elements(By.CSS_SELECTOR, "div > ul > li")), 0)
    
    def test_vote_pref_wrong(self):
        self.login1()
        self.start_voting()
        self.login2()
        time.sleep(1)
        dropdown = self.driver.find_element(By.ID, "__BVID__11")
        dropdown.find_element(By.ID, "q1").click()
        dropdown = self.driver.find_element(By.ID, "__BVID__12")
        dropdown.find_element(By.ID, "q1").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.assertEquals(len(self.driver.find_elements(By.CSS_SELECTOR, "div > ul > li")), 1)   
    
 
