from django.test import LiveServerTestCase
from administration.models import Grade, Person, School, Gruppe
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class CreateGroupTestCase(LiveServerTestCase):
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

        studentobj = mixer.blend('administration.Person', username='student', first_name='studentfirstname')
        studentobj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(CreateGroupTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(CreateGroupTestCase, self).tearDown()

    # Confirms scenario 2.11
    def test_admin_can_create_group(self):
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
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "groupOverview")))
        self.selenium.find_element_by_id('groupOverview').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addNewGroupBtn")))
        self.selenium.find_element_by_id('addNewGroupBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_group_name")))
        self.selenium.find_element_by_id('id_group_name').send_keys('testGroup')
        self.selenium.find_element_by_id('addStudentsBtn').click()
        person = Person.objects.get(username='student')
        time.sleep(0.4)  # Wait for modal open
        self.selenium.find_element_by_id('btn'+ str(person.id)).click()
        self.selenium.find_element_by_id('closeModalBtn').click()
        time.sleep(0.5)  # Wait for modal close
        self.selenium.find_element_by_id('addGroupBtn').click()
        time.sleep(0.2)
        self.assertEqual(1, len(Gruppe.objects.all()))
