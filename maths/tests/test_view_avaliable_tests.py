from django.test import LiveServerTestCase
from maths.models import Test
from mixer.backend.django import mixer
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ViewAvaliableTestsTestCase(LiveServerTestCase):
    def setUp(self):

        catObj = mixer.blend('maths.Category', category_title='matte')
        catObj.save()

        taskObj = mixer.blend('maths.Task', title='testOppgave', category=catObj, id=1)
        taskObj.save()

        taskObj2 = mixer.blend('maths.Task', title='testOppgave2', category=catObj, id=2)
        taskObj2.save()

        taskcollectionobj = mixer.blend('maths.TaskCollection', test_name='test', tasks=[taskObj, taskObj2])
        taskcollectionobj.save()

        testobj = mixer.blend('maths.Test', task_collection=taskcollectionobj)
        testobj.save()

        gradeobj = mixer.blend('administration.Grade', gradename='testGrade', tests=testobj)
        gradeobj.save()

        obj = mixer.blend('administration.Person', role=2, username='teacher', grades=gradeobj)
        obj.set_password('teacher')  # Password has to be set like this because of the hash-function
        obj.save()

        studentobj = mixer.blend('administration.Person', role=1, username='student')
        studentobj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(ViewAvaliableTestsTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(ViewAvaliableTestsTestCase, self).tearDown()

    # Confirms scenario 2.16
    def test_teacher_can_view_avaliable_tests(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("teacher")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("teacher")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "testOverview")))
        self.selenium.find_element_by_id('testOverview').click()
        test_list = self.selenium.find_element_by_id('publishedtable')
        eval = False
        time.sleep(10)
        for el in test_list.find_elements_by_tag_name('td'):
            if el.text == 'test':
                eval = True
                break
        self.assertTrue(eval)
