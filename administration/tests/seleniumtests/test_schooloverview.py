from django.test import LiveServerTestCase
from administration.models import Person
from mixer.backend.django import mixer
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SchoolOverViewTestCase(LiveServerTestCase):
    def setUp(self):
        adminobj = mixer.blend('administration.Person', role=4, username='admin')
        adminobj.set_password('admin')  # Password has to be set like this because of the hash-function
        adminobj.save()

        schooladminobj = mixer.blend('administration.Person', role=3, username='schooladmin', first_name='schooladminfirstname')
        schooladminobj.set_password('schooladmin')
        schooladminobj.save()

        schoolobj = mixer.blend('administration.School', school_administrator=schooladminobj, school_name='testSchool')
        schoolobj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(SchoolOverViewTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(SchoolOverViewTestCase, self).tearDown()

        #Confirms scenario 6
    def test_admin_can_view_school_information(self):

        # student
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
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "schoolOverview")))
        self.selenium.find_element_by_id('schoolOverview').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "search")))
        user_list = self.selenium.find_element_by_id('schoolTable')
        for el in user_list.find_elements_by_tag_name('td'):
            if el.text == 'testSchool':
                el.click()
                break
        username = self.selenium.find_element_by_id('schoolNameField').text
        self.assertEqual(username, 'testSchool')
        'admin should be able to view information about a school'

    # Confirms scenario 6
    def test_schooladmin_can_view_school_information(self):

        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "schoolOverview")))
        self.selenium.find_element_by_id('schoolOverview').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "search")))
        user_list = self.selenium.find_element_by_id('schoolTable')
        for el in user_list.find_elements_by_tag_name('td'):
            if el.text == 'testSchool':
                el.click()
                break
        username = self.selenium.find_element_by_id('schoolNameField').text
        self.assertEqual(username, 'testSchool')
        'admin should be able to view information about a school'

