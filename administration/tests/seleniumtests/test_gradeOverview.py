from django.test import LiveServerTestCase
from administration.models import Person
from mixer.backend.django import mixer
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GradeOverviewTestCase(LiveServerTestCase):
    def setUp(self):
        adminobj = mixer.blend('administration.Person', role=4, username='admin')
        adminobj.set_password('admin')  # Password has to be set like this because of the hash-function
        adminobj.save()

        schooladminobj = mixer.blend('administration.Person', role=3, username='schooladmin', first_name='schooladminfirstname')
        schooladminobj.set_password('schooladmin')
        schooladminobj.save()

        schoolobj = mixer.blend('administration.School', school_administrator=schooladminobj, school_name='testSchool')
        schoolobj.save()

        gradeobj = mixer.blend('administration.Grade', grade_name='testGrade', school=schoolobj)
        gradeobj.save()

        teacherobj = mixer.blend('administration.Person', role=2, username='teacher', grades=gradeobj,
                                 first_name='teacherfirstname')
        teacherobj.set_password('teacher')
        teacherobj.save()

        studentobj = mixer.blend('administration.Person', role=1, username='student', first_name='studfirstname',
                                 grades=gradeobj)
        studentobj.save()

        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(GradeOverviewTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(GradeOverviewTestCase, self).tearDown()

        #Confirms scenario 2.9
    def test_teacher_can_view_grade_information(self):
        # student
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
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "gradeOverview")))
        self.selenium.find_element_by_id('gradeOverview').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "search")))
        grade_list = self.selenium.find_element_by_id('gradetable')
        for el in grade_list.find_elements_by_tag_name('td'):
            if el.text == 'testGrade':
                el.click()
                break
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "alltable")))
        user_list = self.selenium.find_element_by_id('alltable')
        assrt = False
        for el in user_list.find_elements_by_tag_name('td'):
            if el.text == 'studfirstname':
                el.click()
                break
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "usernameField")))
        username = self.selenium.find_element_by_id('usernameField').text
        self.assertEqual(username, 'Brukernavn - student')
        'Teacher should be able to view information about a student'
