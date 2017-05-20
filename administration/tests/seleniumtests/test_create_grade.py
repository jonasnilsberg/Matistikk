from django.test import LiveServerTestCase
from administration.models import Grade, Person, School
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class CreateGradeTestCase(LiveServerTestCase):
    def setUp(self):
        # DB setup
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()

        schooladminobj = mixer.blend('administration.Person', role=3, username='schooladmin',
                                     first_name='schooladminfirstname')
        schooladminobj.set_password('schooladmin')
        schooladminobj.save()

        schoolobj = mixer.blend('administration.School', school_administrator=schooladminobj, school_name='testSchool')
        schoolobj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(CreateGradeTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(CreateGradeTestCase, self).tearDown()

    # Confirms scenario 7
    def test_admin_can_create_grade(self):
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
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "search")))
        user_list = self.selenium.find_element_by_id('schoolTable')
        for el in user_list.find_elements_by_tag_name('td'):
            if el.text == 'testSchool':
                el.click()
                break
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addNewGradeBtn")))
        self.selenium.find_element_by_id('addNewGradeBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_grade_name")))
        self.selenium.find_element_by_id('id_grade_name').send_keys('testGrade')
        self.selenium.find_element_by_id('addGradeBtn').click()
        time.sleep(0.1)
        self.assertEqual(1, len(Grade.objects.filter(grade_name='testGrade')))

    # Confirms scenario 7
    def test_schooladmin_can_create_grade(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "logout")))
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "schoolOverview")))
        self.selenium.find_element_by_id('schoolOverview').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "search")))
        user_list = self.selenium.find_element_by_id('schoolTable')
        for el in user_list.find_elements_by_tag_name('td'):
            if el.text == 'testSchool':
                el.click()
                break
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addNewGradeBtn")))
        self.selenium.find_element_by_id('addNewGradeBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_grade_name")))
        self.selenium.find_element_by_id('id_grade_name').send_keys('testGrade')
        self.selenium.find_element_by_id('addGradeBtn').click()
        time.sleep(0.1)
        self.assertEqual(1, len(Grade.objects.filter(grade_name='testGrade')))
