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


class AddExistingUsersInGradeTestCase(LiveServerTestCase):

    def setUp(self):
        # DB setup
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()

        schooladminobj = mixer.blend('administration.Person', role=3, username='schooladmin',
                                     first_name='schooladminfirstname')
        schooladminobj.set_password('schooladmin')
        schooladminobj.save()

        teacherobj = mixer.blend('administration.Person', role=2, username='teacher', first_name='teacherfirstname')
        teacherobj.set_password('teacher')
        teacherobj.save()

        schoolobj = mixer.blend('administration.School', school_administrator=schooladminobj, school_name='testSchool')
        schoolobj.save()

        gradeobj = mixer.blend('administration.Grade', grade_name='testGrade', school=schoolobj)
        gradeobj.save()

        teacherobj2 = mixer.blend('administration.Person', role=2, username='teacher2', first_name='teacher2firstname')
        teacherobj2.save()

        studentobj = mixer.blend('administration.Person', role=1, first_name='studentfirstname', username='student')
        studentobj.save()
        #  Webdriver setup
        self.selenium = webdriver.Chrome()
        self.selenium.maximize_window()
        super(AddExistingUsersInGradeTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(AddExistingUsersInGradeTestCase, self).tearDown()

    # Confirms scenario 2.8.1
    def test_admin_can_add_existing_teacher_in_grade(self):
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
        school_list = self.selenium.find_element_by_id('schoolTable')
        for el in school_list.find_elements_by_tag_name('td'):
            if el.text == 'testSchool':
                el.click()
                break
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "gradetable")))
        grade_list = self.selenium.find_element_by_id('gradetable')
        for el in grade_list.find_elements_by_tag_name('td'):
            if el.text == 'testGrade':
                el.click()
                break
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addTeacherDropdown")))
        self.selenium.find_element_by_id('addTeacherDropdown').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addExistingTeacherBtn")))
        self.selenium.find_element_by_id('addExistingTeacherBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.visibility_of_element_located((By.ID, "teacher")))
        self.selenium.find_element_by_id('teacher').click()
        person = Person.objects.get(username='teacher')
        time.sleep(0.2)
        self.assertEqual(1, len(person.grades.filter(grade_name='testGrade')))

    # Confirms scenario 2.8.1
    def test_schooladmin_can_add_existing_student_in_grade(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "schoolOverview")))
        self.selenium.find_element_by_id('schoolOverview').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "search")))
        school_list = self.selenium.find_element_by_id('schoolTable')
        for el in school_list.find_elements_by_tag_name('td'):
            if el.text == 'testSchool':
                el.click()
                break
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "gradetable")))
        grade_list = self.selenium.find_element_by_id('gradetable')
        for el in grade_list.find_elements_by_tag_name('td'):
            if el.text == 'testGrade':
                el.click()
                break
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addStudentDropdown")))
        self.selenium.find_element_by_id('addStudentDropdown').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addExistingStudent")))
        self.selenium.find_element_by_id('addExistingStudent').click()
        WebDriverWait(self.selenium, 10).until(EC.visibility_of_element_located((By.ID, "student")))
        self.selenium.find_element_by_id('student').click()
        person = Person.objects.get(username='student')
        time.sleep(0.2)
        self.assertEqual(1, len(person.grades.filter(grade_name='testGrade')))



