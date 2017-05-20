from django.test import LiveServerTestCase
from administration.models import Person
from maths.models import Task
from mixer.backend.django import mixer
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TaskOverviewTestCase(LiveServerTestCase):
    def setUp(self):
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()

        taskObj = mixer.blend('maths.Task', title='testOppgave')
        taskObj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(TaskOverviewTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(TaskOverviewTestCase, self).tearDown()

    # Confirms scenario 17
    def test_admin_can_view_taskOverview(self):
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
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "overviewDropdown")))
        self.selenium.find_element_by_id('overviewDropdown').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "taskOverview")))
        self.selenium.find_element_by_id('taskOverview').click()

        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "search")))
        self.selenium.find_element_by_id('search').send_keys('testOpp')
        task_list = self.selenium.find_element_by_id('tasktable')
        eval = False
        for el in task_list.find_elements_by_tag_name('td'):
            if el.text == 'testOppgave':
                eval = True
                break
        self.assertTrue(eval)
