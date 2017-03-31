from django.test import LiveServerTestCase
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

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
        self.selenium = webdriver.Firefox()
        self.selenium.maximize_window()
        super(MyPageDetailViewTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(MyPageDetailViewTestCase, self).tearDown()

    def test_change_password(self):
        """Checks that a user can view their page and change their password through it"""
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
