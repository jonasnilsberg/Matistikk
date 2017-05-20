from django.test import LiveServerTestCase
from administration.models import Person
from mixer.backend.django import mixer
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class EditOtherUsersPasswordTestCase(LiveServerTestCase):
    def setUp(self):
        gradeobj = mixer.blend('administration.Grade')
        gradeobj.save()

        studentobj = mixer.blend('administration.Person', role=1, username='student', first_name='studentfirstname',
                               grades=gradeobj)
        studentobj.set_password('student')
        studentobj.save()

        teacherobj = mixer.blend('administration.Person', role=2, username='teacher', first_name='teacherfirstname',
                                 grades=gradeobj)
        teacherobj.set_password('teacher')
        teacherobj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(EditOtherUsersPasswordTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(EditOtherUsersPasswordTestCase, self).tearDown()

    # Confirms scenario 15
    def test_teacher_can_set_students_password(self):
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
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "userOverview")))
        self.selenium.find_element_by_id('userOverview').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "search")))
        user_list = self.selenium.find_element_by_id('usertable')
        for el in user_list.find_elements_by_tag_name('td'):
            if el.text == 'studentfirstname':
                el.click()
                break
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "updatePasswordModalBtn")))
        self.selenium.find_element_by_id('updatePasswordModalBtn').click()
        time.sleep(0.2)  # wait for modal to open
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_password")))
        self.selenium.find_element_by_id('id_password').send_keys('ntnu1234')
        self.selenium.find_element_by_id('id_password2').send_keys('ntnu1234')
        self.selenium.find_element_by_id('updatePasswordBtn').click()
        time.sleep(0.2)
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "logout")))
        self.selenium.find_element_by_id('logout').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("student")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("ntnu1234")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "logout")))
        self.assertNotIn('login', self.selenium.current_url)
