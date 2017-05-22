from django.test import LiveServerTestCase
from mixer.backend.django import mixer
from selenium import webdriver
import time
from maths.models import Answer

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ViewAvaliableTstsTestCase(LiveServerTestCase):
    def setUp(self):

        catObj = mixer.blend('maths.Category', category_title='matte')
        catObj.save()

        taskObj = mixer.blend('maths.Task', title='testOppgave', category=catObj, id=1, extra=0, answertype=1,
                              reasoning=0)
        taskObj.save()

        taskcollectionobj = mixer.blend('maths.TaskCollection', test_name='testen', tasks=taskObj, id=1)
        taskcollectionobj.save()

        testobj = mixer.blend('maths.Test', task_collection=taskcollectionobj, id=1, randomOrder=True)
        testobj.save()

        obj = mixer.blend('administration.Person', role=1, username='student', tests=testobj)
        obj.set_password('student')  # Password has to be set like this because of the hash-function
        obj.save()

        answerobj = mixer.blend('maths.Answer', task=taskObj, test=testobj, user=obj, reasoning=None, text='answer')
        answerobj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(ViewAvaliableTstsTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(ViewAvaliableTstsTestCase, self).tearDown()

    # Confirms scenario 23
    def test_teacher_can_view_avaliable_tsts(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("student")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("student")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "accordion2")))
        self.selenium.find_element_by_id('testen').click()
        WebDriverWait(self.selenium, 10).until(EC.visibility_of_element_located((By.ID, "seetestbutton1")))
        self.selenium.find_element_by_id('seetestbutton1').click()
        eval = False
        if (EC.presence_of_element_located((By.ID, "nextTaskBtn"))):
            eval = True
        self.assertTrue(eval)
