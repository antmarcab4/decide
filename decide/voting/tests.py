import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption

class VotingQuestionTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

#Tests añadidos por Antonio y Jose:
    def test_create_yes_no_question(self):
        q = Question(desc='si/no question', si_no=True)
        q.save()
        a = q.options.count()==2
        opt1 = q.options.all()[0]
        opt2 = q.options.all()[1]
        b = (opt1.number==1 and opt1.option=="Si")
        c = (opt2.number==2 and opt2.option=="No")
        self.assertTrue(a and b and c)

    def test_create_yes_no_question_wrong(self):
        #TODO       Buscar como chequear que salte una excepción, en este caso,
        #           la de validación que sala al intentar incluir más opciones con la marca de yes/no
        q = Question(desc='si/no question', si_no=True)
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            self.assertRaises(ValidationError, opt.clean)
            
        


    
#Fin de tests añadidos por Antonio y Jose


#Tests añadidor por Marta
    def create_onequestion_voting(self):
        q, _  = Question.objects.get_or_create()
        q1 = Question(desc='question1')
        q1.save()
        
#Tests añadidos por Alonso y David:
     def test_create_preferences_question(self):
        q = Question(desc='Preferences question', preferences=True)
        q.save()
        self.assertTrue(q.preferences = True)


        
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting')
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q1)

        return v

    def test_create_onequestion_voting(self):
        v = self.create_onequestion_voting()
        self.assertEqual(v.question.all().count(), 1)

    def create_multiquestion_voting(self):
        q, _  = Question.objects.get_or_create()
        q1 = Question(desc='question1')
        q2 = Question(desc='question2')
        q1.save()
        q2.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting')
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.question.add(q1)
        v.question.add(q2)

        return v

    def test_create_multiquestion_voting(self):
        v = self.create_multiquestion_voting()
        self.assertEqual(v.question.all().count(), 2)


#Test añadidos por Manuel
class VotingModelTC(BaseTestCase):

    def setUp(self):
        q1 = Question(desc="test question1")
        q1.save()
        q2 = Question(desc="test question2")
        q2.save()
        q3 = Question(desc="test question3")
        q3.save()

        opt1 = QuestionOption(question=q1,option="option1")
        opt2 = QuestionOption(question=q1,option="option2")
        opt3 = QuestionOption(question=q2,option="option3")
        opt4 = QuestionOption(question=q2,option="option4")
        opt5 = QuestionOption(question=q3,option="option5")
        opt6 = QuestionOption(question=q3,option="option6")


        v=Voting(name="Votacion")
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        
        v.auths.add(a)
        v.question.add(q1)
        v.question.add(q2)
        v.question.add(q3)
        
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.v=None

    def test_create_multi(self):
        v = Voting.objects.get(name="Votacion")
        self.assertEquals(v.name,"Votacion")
    
    def test_questions_multi(self):
        v = Voting.objects.get(name="Votacion")
        self.assertEquals(v.question.all().count(),3)

'''     
class VotingTestCase(BaseTestCase):

    def setUp(self):
U        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_question(self):
        q = Question(desc='test question', si_no='False', preferences='False')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        
        return q

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def test_create_voting_from_api(self):
        q = self.create_question
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Example',
            'desc': 'Description example',
            'ques': '1',
            'question_opt': ['cat', 'dog', 'horse', 'tiger', 'frog']
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)
"""
    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}
        #response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        #self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')

        # STATUS VOTING: tallied
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already tallied')'''
