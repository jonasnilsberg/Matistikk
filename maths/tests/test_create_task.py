from django.test import LiveServerTestCase
from administration.models import Person
from maths.models import Task
from mixer.backend.django import mixer
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CreateTaskTestCase(LiveServerTestCase):
    def setUp(self):
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()


        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(CreateTaskTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(CreateTaskTestCase, self).tearDown()

    # Confirms scenario 2.16
    def test_admin_can_create_task(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("admin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("admin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "createTask")))
        self.selenium.find_element_by_id('createTask').click()
        self.selenium.find_element_by_id('taskname').send_keys('testoppgave')
        self.selenium.find_element_by_id('addCategoryBtn').click()
        time.sleep(0.5)  # wait for modal open
        self.selenium.find_element_by_id('id_category_title').send_keys('testKategori')
        self.selenium.find_element_by_id('saveCategoryBtn').click()
        time.sleep(0.5)  # wait for modal close
        self.selenium.execute_script("tinyMCE.get('tasktext').setContent('<h1>New task text</h1>')")
        self.selenium.find_element_by_id('textAnswerRadio').click()
        self.selenium.find_element_by_id('extraField').click()
        self.selenium.find_element_by_id('saveTaskBtn').click()
        time.sleep(0.2)
        self.assertEqual(1, len(Task.objects.all()))
