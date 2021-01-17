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

        q1 = Question(desc='Simple question')
        q1.save()
        for i in range(3):
            optPref = QuestionOption(question=q1, option='option {}'.format(i+1))
            optPref.save()

        q2 = Question(desc='yes/no question', si_no=True)
        q2.save()

        v = Voting(name='test voting', id="2")
        v.save()

        v2= Voting(name='test voting yes no', id="3")
        v2.save()

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
        time.sleep(1)
        self.driver.find_element(By.ID, "action-toggle").click()
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

    def login4(self):
        self.driver.get(f'{self.live_server_url}/booth/3')
        self.driver.find_element(By.ID, "username").click()
        self.driver.find_element(By.ID, "username").send_keys("voter")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("voter")
        self.driver.find_element(By.CSS_SELECTOR, ".btn").click()

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
    
    #Tests por Marta
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
    #Fin de tests por Marta

    #Tests por Jose
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
    #Fin de tests por Jose

    #Tests de Antonio
    def test_crearyesnomal(self):
        self.login1()
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        time.sleep(1)
        self.driver.find_element(By.ID, "id_desc").click()
        time.sleep(1)
        self.driver.find_element(By.ID, "id_desc").send_keys("crear pregunta si/no mal - selenium")
        self.driver.find_element(By.CSS_SELECTOR, ".field-si_no .vCheckboxLabel").click()
        self.driver.find_element(By.ID, "id_options-0-option").click()
        time.sleep(1)
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("bad")
        self.driver.find_element(By.NAME, "_save").click()
        time.sleep(1)
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".errornote"), True)

    def test_crearyborraryesno(self):
        self.login1()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        time.sleep(2)
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("question de prueba de selenium")
        self.driver.find_element(By.ID, "id_si_no").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.CSS_SELECTOR, ".success").click()
        self.driver.find_element(By.CSS_SELECTOR, ".row1:nth-child(1) a").click()
        self.driver.find_element(By.LINK_TEXT, "Delete").click()
        self.driver.find_element(By.CSS_SELECTOR, "input:nth-child(2)").click()
        time.sleep(2)
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".success"), True)

    def test_crearyupdatearyesno(self):
        self.login1()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        self.driver.find_element(By.ID, "id_si_no").click()
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("pregunta si/no para probar modificaciones selenium")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.CSS_SELECTOR, ".row1:nth-child(1) a").click()
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("pregunta si/no para probar modificaciones selenium -> se ha modificado")
        self.driver.find_element(By.NAME, "_save").click()
        time.sleep(1)
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".success"), True)
    #Fin tests de Antonio

    #Tests por David
    def test_create_question_pref(self):
        self.login1()
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        self.driver.find_element(By.ID, "id_desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Prueba selenium")
        self.driver.find_element(By.ID, "id_preferences").click()
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("c")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("f")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-2-option").click()
        self.driver.find_element(By.ID, "id_options-2-option").send_keys("a")
        self.driver.find_element(By.ID, "id_options-2-number").click()
        self.driver.find_element(By.ID, "id_options-2-number").send_keys("3")
        self.driver.find_element(By.NAME, "_save").click()
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".success"),True)
    #Fin tests de David