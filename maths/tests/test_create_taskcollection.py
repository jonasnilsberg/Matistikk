from django.test import LiveServerTestCase
from administration.models import Person
from maths.models import TaskCollection
from mixer.backend.django import mixer
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CreateTaskCollectionTestCase(LiveServerTestCase):
    def setUp(self):
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()

        catObj = mixer.blend('maths.Category', category_title='matte')
        catObj.save()

        taskObj = mixer.blend('maths.Task', title='testOppgave', category=catObj, id=1)
        taskObj.save()

        taskObj2 = mixer.blend('maths.Task', title='testOppgave2', category=catObj, id=2)
        taskObj2.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(CreateTaskCollectionTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(CreateTaskCollectionTestCase, self).tearDown()

    # Confirms scenario 2.16
    def test_admin_can_create_taskcollection(self):
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
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "createTest")))
        self.selenium.find_element_by_id('createTest').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_test_name")))
        self.selenium.find_element_by_id('id_test_name').send_keys('testCollection')
        task_list = self.selenium.find_element_by_id('table')
        for el in task_list.find_elements_by_tag_name('td'):
            if el.text == 'testOppgave':
                el.click()
                break
        for el in task_list.find_elements_by_tag_name('td'):
            if el.text == 'testOppgave2':
                el.click()
                break
        self.selenium.find_element_by_id('saveTaskCollectionBtn').click()
        time.sleep(0.2)
        self.assertEqual(1, len(TaskCollection.objects.all()))
