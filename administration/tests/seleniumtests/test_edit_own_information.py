from django.test import LiveServerTestCase
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from ...models import Person
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class EditOwnInformationTestCase(LiveServerTestCase):
    def setUp(self):
        # DB setup
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')
        obj.save()

        schooladminobj = mixer.blend('administration.Person', role=3, username='schooladmin')
        schooladminobj.set_password('schooladmin')
        schooladminobj.save()

        studentobj = mixer.blend('administration.Person', role=1, username='student')
        studentobj.set_password('student')
        studentobj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(EditOwnInformationTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(EditOwnInformationTestCase, self).tearDown()

    # Confirms scenario 2.10.1
    def test_schooladmin_can_change_own_password(self):
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

    # Confirms scenario 2.10.1
    def test_schooladmin_can_edit_own_information(self):
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
        Person.objects.filter(first_name='newName', last_name='newSurname', email='new@email.test',
                              date_of_birth='1995-10-13')

    # Confirms 2.10.2
    def test_student_can_edit_password(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("student")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("student")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "myPageBtn")))
        self.selenium.find_element_by_id('myPageBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "changePasswordModalBtn")))
        self.selenium.find_element_by_id('changePasswordModalBtn').click()
        time.sleep(0.2)  # wait for modal to open
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_old_password")))
        self.selenium.find_element_by_id('id_old_password').send_keys('student')
        self.selenium.find_element_by_id('id_new_password1').send_keys('ntnu1234')
        self.selenium.find_element_by_id('id_new_password2').send_keys('ntnu1234')
        self.selenium.find_element_by_id('changePasswordBtn').click()
        time.sleep(0.3)  # wait for modal to close
        self.selenium.find_element_by_id('logout').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("student")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("ntnu1234")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "logout")))
        self.assertNotIn('login', self.selenium.current_url), \
            'Login should not be in the url if the user was logged in successfully using the new password'

    # Confirms 2.10.2
    def test_student_can_edit_email(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("student")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("student")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "myPageBtn")))
        self.selenium.find_element_by_id('myPageBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "updateEmailBtn")))
        self.selenium.find_element_by_id('updateEmailBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.visibility_of_element_located((By.ID, "newEmail")))
        self.selenium.find_element_by_id('newEmail').send_keys('new@email.com')
        self.selenium.find_element_by_id('updateBtn').click()
        time.sleep(0.2)
        self.assertEqual(1, len(Person.objects.filter(email='new@email.com')))
