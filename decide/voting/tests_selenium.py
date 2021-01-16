import time
import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC

from base.tests import BaseTestCase


class AdminTestCase(StaticLiveServerTestCase):

   
    def setUp(self):

        self.client = APIClient()
        mods.mock_query(self.client)

        voter1 = User(username='voter', id="2")
        voter1.set_password('voter')
        voter1.save()

        admin = User(username='admin', is_staff=True)
        admin.set_password('admin')
        admin.is_superuser = True
        admin.save()

        q = Question(desc='Preferences question', preferences=True)
        q.save()   
        
        for i in range(3):
            optPref = QuestionOption(question=q, option='option {}'.format(i+1))
            optPref.save()

        q2 = Question(desc='yes/no question', si_no=True)
        q2.save()

        v = Voting(name='test voting', id="2")
        v.save()

        v2= Voting(name='test voting yes no', id="3")

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        a.save()

        v.auths.add(a)
        v.question.add(q)
        v2.auths.add(a)
        v2.question.add(q2)
        v.save()
        v2.save()

        census = Census(voting_id=2, voter_id=2)
        census.save()
        census2 = Census(voting_id=3, voter_id=2)
        census2.save()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()  
    
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()

    def start_voting(self):                    
        #self.driver.get(f'{self.live_server_url}/admin')
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        time.sleep(1)
        self.driver.find_element(By.NAME, "_selected_action").click()
        time.sleep(1)
        dropdown = self.driver.find_element(By.NAME, "action")
        time.sleep(1)
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()


        #print(self.driver.current_url)
        #In case of a correct loging, a element with id 'user-tools' is shown in the upper right part
        #self.assertTrue(len(self.driver.find_elements_by_id('user-tools'))==1)

    def login1(self):
        self.driver.get(f'{self.live_server_url}/admin')
        self.driver.find_element_by_id('id_username').send_keys("admin")
        time.sleep(1)
        self.driver.find_element_by_id('id_password').send_keys("admin",Keys.ENTER)
        time.sleep(1)

    def login2(self):
        self.driver.get(f'{self.live_server_url}/booth/2')
        time.sleep(3)
        self.driver.find_element_by_id('id_username').send_keys("voter1")
        time.sleep(3)
        self.driver.find_element_by_id('id_password').send_keys("voter1",Keys.ENTER)
        time.sleep(3) 

    def login3(self):
        self.driver.get(f'{self.live_server_url}/booth/3')
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("WRONG")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("WRONG")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

    def test_yesno_question(self):
        self.driver.get(f'{self.live_server_url}/admin/login/?next=/admin/')
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("admin", Keys.ENTER)
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Prueba")
        self.driver.find_element(By.ID, "id_si_no").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".success"), True)

    def login4(self):
        self.driver.get(f'{self.live_server_url}/booth/3')
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("voter")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("voter")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

    def test_voting_yes_no(self):
        self.login1()
        time.sleep(1)
        self.start_voting()
        self.login4()
        time.sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, ".custom-control:nth-child(1) > .custom-control-label").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        time.sleep(2)
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert"), True)
        self.driver.find_element(By.LINK_TEXT, "logout").click()
    