from django.test import LiveServerTestCase
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from ...models import Person
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class MyPageDetailViewTestCase(LiveServerTestCase):
    def setUp(self):
        # DB setup
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')
        obj.save()

        schooladminobj = mixer.blend('administration.Person', role=3, username='schooladmin')
        schooladminobj.set_password('schooladmin')
        schooladminobj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(MyPageDetailViewTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(MyPageDetailViewTestCase, self).tearDown()

    def test_change_password(self):
        """Checks that a user can view their page and change their password"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "myPageBtn")))
        self.selenium.find_element_by_id('myPageBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "changePasswordModalBtn")))
        self.selenium.find_element_by_id('changePasswordModalBtn').click()
        time.sleep(0.2)  # wait for modal to open
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_old_password")))
        self.selenium.find_element_by_id('id_old_password').send_keys('schooladmin')
        self.selenium.find_element_by_id('id_new_password1').send_keys('ntnu1234')
        self.selenium.find_element_by_id('id_new_password2').send_keys('ntnu1234')
        self.selenium.find_element_by_id('changePasswordBtn').click()
        time.sleep(0.3)  # wait for modal to close
        self.selenium.find_element_by_id('logout').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("ntnu1234")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "logout")))
        self.assertNotIn('login', self.selenium.current_url), \
            'Login should not be in the url if the user was logged in successfully using the new password'

    def test_edit_information(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "myPageBtn")))
        self.selenium.find_element_by_id('myPageBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "updateInformationBtn")))
        self.selenium.find_element_by_id('updateInformationBtn').click()
        time.sleep(0.2)  # waiting for modal to open
        self.selenium.find_element_by_id('id_first_name').clear()
        self.selenium.find_element_by_id('id_first_name').send_keys('newName')
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('newSurname')
        self.selenium.find_element_by_id('id_email').clear()
        self.selenium.find_element_by_id('id_email').send_keys('new@email.test')
        self.selenium.find_element_by_id('id_date_of_birth').clear()
        self.selenium.find_element_by_id('id_date_of_birth').send_keys('1995-10-13')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.2)
        Person.objects.filter(first_name='newName', last_name='newSurname', email='new@email.test', date_of_birth='1995-10-13')
