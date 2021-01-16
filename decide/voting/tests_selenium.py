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
        v = Voting(name='test voting', id="2")
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q)
        v.save()

        q1 = Question(desc='Simple question')
        q1.save()   
        for i in range(3):
            opt = QuestionOption(question=q1, option='option {}'.format(i+1))
            opt.save()
       

        census = Census(voting_id=2, voter_id=2)
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

    def login1(self):
        self.driver.get(f'{self.live_server_url}/admin')
        self.driver.find_element_by_id('id_username').send_keys("admin")
        self.driver.find_element_by_id('id_password').send_keys("admin",Keys.ENTER)

    def create_simple_question1(self):
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("testQuestion2")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("testOption1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("testOption2")
        self.driver.find_element(By.ID, "id_options-2-number").click()
        self.driver.find_element(By.ID, "id_options-2-number").send_keys("3")
        self.driver.find_element(By.ID, "id_options-2-option").click()
        self.driver.find_element(By.ID, "id_options-2-option").send_keys("testOption3")
        self.driver.find_element(By.NAME, "_save").click()


    def create_multiquestion_voting(self):
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting .addlink").click()
        self.driver.find_element(By.ID, "id_name").send_keys("testVoting")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("testVotingDesc")
        dropdown = self.driver.find_element(By.ID, "id_question")   
        dropdown.find_element(By.XPATH, "//option[. = 'Simple question']").click()
        dropdown = self.driver.find_element(By.ID, "id_question")   
        dropdown.find_element(By.XPATH, "//option[. = 'Preferences question']").click()
        dropdown = self.driver.find_element(By.ID, "id_auths")
        dropdown.find_element(By.XPATH, "//option[. = 'http://localhost:8000']").click()
        self.driver.find_element(By.NAME, "_save").click()

    def create_singlequestion_voting(self):
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("testQuestion2")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("testOption1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("testOption2")
        self.driver.find_element(By.ID, "id_options-2-number").click()
        self.driver.find_element(By.ID, "id_options-2-number").send_keys("3")
        self.driver.find_element(By.ID, "id_options-2-option").click()
        self.driver.find_element(By.ID, "id_options-2-option").send_keys("testOption3")
        self.driver.find_element(By.NAME, "_save").click()
        
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()

        self.driver.find_element(By.CSS_SELECTOR, ".model-voting .addlink").click()
        self.driver.find_element(By.ID, "id_name").send_keys("testVoting")
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("testVotingDesc")
        dropdown = self.driver.find_element(By.ID, "id_question")   
        dropdown.find_element(By.XPATH, "//option[. = 'testQuestion2']").click()
        dropdown = self.driver.find_element(By.ID, "id_auths")
        dropdown.find_element(By.XPATH, "//option[. = 'http://localhost:8000']").click()
        self.driver.find_element(By.NAME, "_save").click()

    
    #Pruebas por Marta
    def test_create_simple_question(self):
        self.login1()
        self.create_simple_question1()
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".success"), True)

    
    def test_create_multiquestion_voting(self):
        self.login1()
        self.create_multiquestion_voting()
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".success"), True)
        

    def test_create_singlequesstion_voting(self):
        self.login1()
        self.create_singlequestion_voting()
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".success"), True)


    def test_yesno_question(self):
        self.driver.get(f'{self.live_server_url}/admin/login/?next=/admin/')
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("admin")
        time.sleep(5)
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Prueba")
        self.driver.find_element(By.ID, "id_si_no").click()
        self.driver.find_element(By.NAME, "_save").click()







   
        



  
