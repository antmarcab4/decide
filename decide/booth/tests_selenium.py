from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User

from rest_framework.test import APIClient

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from base import mods
from census.models import Census
from voting.models import Question
from voting.models import QuestionOption
from voting.models import Voting
from mixnet.models import Auth
from django.conf import settings

import time

class AdminTestCase(StaticLiveServerTestCase):

    def setUp(self):

        self.client = APIClient()
        mods.mock_query(self.client)

        voter1 = User(username='voter', id="9")
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
        q1 = Question(desc='Simple question1')
        q1.save()
        for i in range(3):
            optPref = QuestionOption(question=q1, option='option {}'.format(i+1))
            optPref.save()
        q2 = Question(desc='Simple question1')
        q2.save()
        for i in range(3):
            optPref = QuestionOption(question=q2, option='option {}'.format(i+1))
            optPref.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        a.save()
        a2, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        a2.save()

        v1 = Voting(name='test voting', id="4")
        v1.save()
        v1.auths.add(a)
        v1.question.add(q)
        v1.save()

        v = Voting(name='test voting', id="2")
        v.save()
        v.auths.add(a)
        v.question.add(q1)
        v.question.add(q2)
        v.save()

        v2 = Voting(name='test voting 2', id='3')
        v2.save()
        v2.auths.add(a2)
        v2.question.add(q1)
        v2.question.add(q2)

        census = Census(voting_id=2, voter_id=9)
        census = Census(voting_id=4, voter_id=9)
        census = Census(voting_id=1, voter_id=9)
        census.save()

        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.client = None
        self.v=None
        self.q=None
    #Métodos usados en los tests
    def start_voting(self):
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.ID, "action-toggle").click()
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

    def login3(self):
        self.driver.get(f'{self.live_server_url}/booth/3')
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("WRONG")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("WRONG")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

    def login4(self):
        self.driver.get(f'{self.live_server_url}/booth/4')
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("voter")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("voter")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

    def login5(self):
        self.driver.get(f'{self.live_server_url}/booth/3')
        time.sleep(1)
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("voter")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("voter")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

    def stop_voting(self):
        self.driver.find_element(By.NAME, "_selected_action").click()
        time.sleep(1)
        dropdown = self.driver.find_element(By.NAME, "action")
        time.sleep(1)
        dropdown.find_element(By.XPATH, "//option[. = 'Stop']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()

    #Tests por Marta
    def test_vote_in_multiquestion_voting(self):
        self.login1()
        time.sleep(1)
        self.start_voting()
        self.login2()
        time.sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, "#\\__BVID__11 > .custom-control:nth-child(1) > .custom-control-label").click()
        time.sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, "#\\__BVID__16 > .custom-control:nth-child(2) > .custom-control-label").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        time.sleep(2)
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert"),True)
        self.driver.find_element(By.LINK_TEXT, "logout").click()
        time.sleep(1)

    def test_unauthorized_voter(self):
        self.login1()
        time.sleep(1)
        self.start_voting()
        self.login3()
        time.sleep(1)
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert"),True)
    #Fin de tests por Marta

    #Tests por Alonso y David
    def test_vote_pref(self):
        self.login1()
        self.start_voting()
        self.login4()
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
        self.login4()
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
        self.login4()
        time.sleep(1)
        dropdown = self.driver.find_element(By.ID, "__BVID__11")
        dropdown.find_element(By.ID, "q1").click()
        dropdown = self.driver.find_element(By.ID, "__BVID__12")
        dropdown.find_element(By.ID, "q1").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        self.assertEquals(len(self.driver.find_elements(By.CSS_SELECTOR, "div > ul > li")), 1)

    def test_votacionCerrada(self):
        self.login1()
        self.start_voting()
        self.stop_voting()
        self.login4()
        time.sleep(1)
        dropdown = self.driver.find_element(By.ID, "__BVID__11")
        dropdown.find_element(By.ID, "q1").click()
        dropdown = self.driver.find_element(By.ID, "__BVID__12")
        dropdown.find_element(By.ID, "q2").click()
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()
        time.sleep(1)
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert"),True)

    def test_update_asignar_pregunta(self):
        self.login1()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting > th > a").click()
        self.driver.find_element(By.CSS_SELECTOR, ".row2 a").click()
        dropdown = self.driver.find_element(By.ID, "id_question")
        time.sleep(1)
        dropdown.find_element(By.XPATH, "//option[. = 'Preferences question']").click()
        time.sleep(1)
        self.driver.find_element(By.NAME, "_save").click()
        time.sleep(1)
        self.driver.get(f'{self.live_server_url}/admin')
        self.start_voting()
        self.login5()
        time.sleep(1)
        self.assertTrue(self.driver.find_element(By.ID, "__BVID__11"), True)
        self.assertTrue(self.driver.find_element(By.ID, "__BVID__12"), True)
    #Fin tests Alonso y David