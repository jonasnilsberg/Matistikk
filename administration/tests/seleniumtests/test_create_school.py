from django.test import LiveServerTestCase
from administration.models import School, Person
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class CreateSchoolTestCase(LiveServerTestCase):
    def setUp(self):
        # DB setup
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(CreateSchoolTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(CreateSchoolTestCase, self).tearDown()

    # Confirms scenario 2.5
    def test_admin_can_create_school_without_schooladministrator(self):
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
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "schoolOverview")))
        self.selenium.find_element_by_id('schoolOverview').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addSchoolBtn")))
        self.selenium.find_element_by_id('addSchoolBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_school_name")))
        self.selenium.find_element_by_id('id_school_name').send_keys('testSchool')
        self.selenium.find_element_by_id('id_school_address').send_keys('testAddress')
        self.selenium.find_element_by_id('saveNewSchoolBtnVisible').click()
        time.sleep(0.1)
        self.assertEqual(1, len(School.objects.filter(school_name='testSchool')))

    # Confirms scenario 2.5
    def test_admin_can_create_school_with_new_schooladministrator(self):
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
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "schoolOverview")))
        self.selenium.find_element_by_id('schoolOverview').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addSchoolBtn")))
        self.selenium.find_element_by_id('addSchoolBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_school_name")))
        self.selenium.find_element_by_id('id_school_name').send_keys('testSchool')
        self.selenium.find_element_by_id('id_school_address').send_keys('testAddress')
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "createPerson")))
        self.selenium.find_element_by_id('createPerson').click()
        time.sleep(0.2)  # waiting for modal to open
        self.selenium.find_element_by_id('id_first_name').send_keys('testSchoolAdministrator')
        self.selenium.find_element_by_id('id_last_name').send_keys('testSchoolAdministratorsurname')
        time.sleep(0.2)  # Waiting because of change in field type, seems to be a weakness in chrome
        # when given fast input
        self.selenium.find_element_by_id('id_email').send_keys('test@test.com')
        self.selenium.find_element_by_id('id_date_of_birth').send_keys('13.10.1995')
        sex = self.selenium.find_element_by_id('id_sex')
        for option in sex.find_elements_by_tag_name('option'):
            if option.text == 'Gutt':
                break
            else:
                ARROW_DOWN = u'\ue015'
                sex.send_keys(ARROW_DOWN)
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "administratorCreateVisible")))
        self.selenium.find_element_by_id('administratorCreateVisible').click()
        time.sleep(0.5)  # waiting for modal close
        self.selenium.find_element_by_id('saveNewSchoolBtnVisible').click()
        time.sleep(0.2)  # waiting for db to be updated
        self.assertEqual(1, len(School.objects.filter(school_name='testSchool')))

