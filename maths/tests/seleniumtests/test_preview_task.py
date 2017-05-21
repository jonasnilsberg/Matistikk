from django.test import LiveServerTestCase
from administration.models import Grade, Person, School, Gruppe
from maths.models import Task
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
import time


class PreviewTaskTestCase(LiveServerTestCase):
    def setUp(self):
        # DB setup
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()

        catObj = mixer.blend('maths.Category', category_title='matte')
        catObj.save()

        taskObj = mixer.blend('maths.Task', title='testOppgave', category=catObj, id=1, text='testText', extra=False)
        taskObj.save()
        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(PreviewTaskTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(PreviewTaskTestCase, self).tearDown()

    # Enables scenario 19
    def test_admin_can_view_task_preview(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("admin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("admin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "overviewDropdown")))
        self.selenium.find_element_by_id('overviewDropdown').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "taskOverview")))
        self.selenium.find_element_by_id('taskOverview').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "tasktable")))
        task_list = self.selenium.find_element_by_id('tasktable')
        for el in task_list.find_elements_by_tag_name('td'):
            if el.text == 'testOppgave':
                el.click()
                break
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "preview1")))
        self.selenium.find_element_by_id('preview1').click()
        eval = False
        if self.selenium.find_element_by_id('previewTaskModal').is_displayed:
            eval = True
        self.assertTrue(eval)
