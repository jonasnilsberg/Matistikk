from django.test import LiveServerTestCase
from administration.models import Person
from mixer.backend.django import mixer
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DeleteUserTestCase(LiveServerTestCase):
    def setUp(self):
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()

        teacherobj = mixer.blend('administration.Person', role=2, username='teacher', first_name='teacherfirstname')
        teacherobj.set_password('teacher')
        teacherobj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(DeleteUserTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(DeleteUserTestCase, self).tearDown()

    # Confirms scenario 13
    def test_admin_can_create_student_teacher_and_schooladmin_without_school(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("admin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("admin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "overviewDropdown")))
        self.selenium.find_element_by_id('overviewDropdown').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "userOverview")))
        self.selenium.find_element_by_id('userOverview').click()
        user_list = self.selenium.find_element_by_id('usertable')
        for el in user_list.find_elements_by_tag_name('td'):
            if el.text == 'teacherfirstname':
                el.click()
                break
        self.selenium.find_element_by_id('deleteUserBtn').click()
        time.sleep(0.4)  # Wait for modal to open
        self.selenium.find_element_by_id('deleteUserModalBtn').click()
        time.sleep(0.2)
        self.assertEqual(0, len(Person.objects.filter(first_name='teacherfirstname')))
