from django.test import LiveServerTestCase
from maths.models import Test
from mixer.backend.django import mixer
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PublishTestTestCase(LiveServerTestCase):
    def setUp(self):
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()

        studentobj = mixer.blend('administration.Person', role=1, username='student')
        studentobj.save()

        catObj = mixer.blend('maths.Category', category_title='matte')
        catObj.save()

        taskObj = mixer.blend('maths.Task', title='testOppgave', category=catObj, id=1)
        taskObj.save()

        taskObj2 = mixer.blend('maths.Task', title='testOppgave2', category=catObj, id=2)
        taskObj2.save()

        taskcollectionobj = mixer.blend('maths.TaskCollection', test_name='test', tasks=[taskObj, taskObj2], author=obj)
        taskcollectionobj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(PublishTestTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(PublishTestTestCase, self).tearDown()

    # Confirms scenario 2.16
    def test_admin_can_create_publish_test(self):
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
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "testOverview")))
        self.selenium.find_element_by_id('testOverview').click()
        test_list = self.selenium.find_element_by_id('testtable')
        for el in test_list.find_elements_by_tag_name('td'):
            if el.text == 'test':
                el.click()
                break
        self.selenium.find_element_by_xpath('/html/body/div[1]/div[3]/a[1]').click()
        stud_list = self.selenium.find_element_by_id('studenttable')
        for el in stud_list.find_elements_by_tag_name('td'):
            if el.text == 'student':
                el.click()
                break
        self.selenium.find_element_by_id('overviewBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "submitBtn")))
        self.selenium.find_element_by_id('submitBtn').click()
        time.sleep(10)
        self.assertEqual(1, len(Test.objects.all()))

