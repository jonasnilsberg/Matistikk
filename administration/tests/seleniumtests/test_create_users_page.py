from django.test import LiveServerTestCase
from administration.models import Person
from mixer.backend.django import mixer
from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class PersonCreateViewTestCase(LiveServerTestCase):

    def setUp(self):
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()

        schooladminobj = mixer.blend('administration.Person', role=3, username='schooladmin')
        schooladminobj.set_password('schooladmin')
        schooladminobj.save()

        schoolobj = mixer.blend('administration.School', school_administrator=schooladminobj, school_name='testSchool')
        schoolobj.save()

        gradeobj = mixer.blend('administration.Grade', grade_name='testGrade', school=schoolobj)
        gradeobj.save()
        #  Webdriver setup
        #  This view uses jquery that can't be ran in htmlunit
        self.selenium = webdriver.Firefox()
        self.selenium.maximize_window()
        super(PersonCreateViewTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(PersonCreateViewTestCase, self).tearDown()

    def test_admin_can_create_student_teacher_and_schooladmin_without_school(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("admin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("admin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addNewUserBtn")))
        self.selenium.find_element_by_id('addNewUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_first_name")))
        self.selenium.find_element_by_id('id_first_name').send_keys('testName')
        self.selenium.find_element_by_id('id_last_name').send_keys('testSurname')
        self.selenium.find_element_by_id('id_email').send_keys('test@test.com')
        self.selenium.find_element_by_id('id_date_of_birth').send_keys('10.10.1997')
        sex = self.selenium.find_element_by_id('id_sex')
        for option in sex.find_elements_by_tag_name('option'):
            if option.text == 'Gutt':
                break
            else:
                ARROW_DOWN = u'\ue015'
                sex.send_keys(ARROW_DOWN)
        role = self.selenium.find_element_by_id('id_role')
        for option in role.find_elements_by_tag_name('option'):
            if option.text == 'Elev':
                break
            else:
                ARROW_DOWN = u'\ue015'
                role.send_keys(ARROW_DOWN)
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        self.assertEqual(1, len(Person.objects.filter(role=1, first_name='testName'))), \
            'Should be a student object saved in the database'
        # Teacher
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/nybruker")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_first_name")))
        self.selenium.find_element_by_id('id_first_name').send_keys('testNameTeacher')
        self.selenium.find_element_by_id('id_last_name').send_keys('testSurnameTeacher')
        self.selenium.find_element_by_id('id_email').send_keys('testTeacher@email.com')
        self.selenium.find_element_by_id('id_date_of_birth').send_keys('10.10.1982')
        sex = self.selenium.find_element_by_id('id_sex')
        for option in sex.find_elements_by_tag_name('option'):
            if option.text == 'Jente':
                break
            else:
                ARROW_DOWN = u'\ue015'
                sex.send_keys(ARROW_DOWN)
        role = self.selenium.find_element_by_id('id_role')
        for option in role.find_elements_by_tag_name('option'):
            if option.text == 'Lærer':
                break
            else:
                ARROW_DOWN = u'\ue015'
                role.send_keys(ARROW_DOWN)
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        self.assertEqual(1, len(Person.objects.filter(role=2, first_name='testNameTeacher'))), \
            'Should be a Teacher object saved in the database'

        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/nybruker")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_first_name")))
        # Schooladmin
        self.selenium.find_element_by_id('id_first_name').send_keys('testNameSAdmin')
        self.selenium.find_element_by_id('id_last_name').send_keys('testSurnameSAdmin')
        self.selenium.find_element_by_id('id_email').send_keys('testSAdmin@email.com')
        self.selenium.find_element_by_id('id_date_of_birth').send_keys('10.10.1973')
        sex = self.selenium.find_element_by_id('id_sex')
        for option in sex.find_elements_by_tag_name('option'):
            if option.text == 'Jente':
                break
            else:
                ARROW_DOWN = u'\ue015'
                sex.send_keys(ARROW_DOWN)
        role = self.selenium.find_element_by_id('id_role')
        for option in role.find_elements_by_tag_name('option'):
            if option.text == 'Skoleadministrator':
                break
            else:
                ARROW_DOWN = u'\ue015'
                role.send_keys(ARROW_DOWN)
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        self.assertEqual(1, len(Person.objects.filter(role=3, first_name='testNameSAdmin'))), \
            'Should be a schooladministrator object saved in the database'

    def test_schooladmin_can_create_teacher_student_without_school(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        self.selenium.find_element_by_id('logInBtn').click()
        # Student
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addNewUserBtn")))
        self.selenium.find_element_by_id('addNewUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_first_name")))
        self.selenium.find_element_by_id('id_first_name').send_keys('testName')
        self.selenium.find_element_by_id('id_last_name').send_keys('testSurname')
        self.selenium.find_element_by_id('id_email').send_keys('test@test.com')
        self.selenium.find_element_by_id('id_date_of_birth').send_keys('10.10.1997')
        sex = self.selenium.find_element_by_id('id_sex')
        for option in sex.find_elements_by_tag_name('option'):
            if option.text == 'Gutt':
                break
            else:
                ARROW_DOWN = u'\ue015'
                sex.send_keys(ARROW_DOWN)
        role = self.selenium.find_element_by_id('id_role')
        for option in role.find_elements_by_tag_name('option'):
            if option.text == 'Elev':
                break
            else:
                ARROW_DOWN = u'\ue015'
                role.send_keys(ARROW_DOWN)
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        self.assertEqual(1, len(Person.objects.filter(role=1, first_name='testName'))), \
            'Should be a student object saved in the database'
        # Teacher
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/nybruker")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_first_name")))
        self.selenium.find_element_by_id('id_first_name').send_keys('testTeacher')
        self.selenium.find_element_by_id('id_last_name').send_keys('testTeacherSurname')
        self.selenium.find_element_by_id('id_email').send_keys('test@test.com')
        self.selenium.find_element_by_id('id_date_of_birth').send_keys('10.10.1997')
        sex = self.selenium.find_element_by_id('id_sex')
        for option in sex.find_elements_by_tag_name('option'):
            if option.text == 'Gutt':
                break
            else:
                ARROW_DOWN = u'\ue015'
                sex.send_keys(ARROW_DOWN)
        role = self.selenium.find_element_by_id('id_role')
        for option in role.find_elements_by_tag_name('option'):
            if option.text == 'Lærer':
                break
            else:
                ARROW_DOWN = u'\ue015'
                role.send_keys(ARROW_DOWN)
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        self.assertEqual(1, len(Person.objects.filter(role=2, first_name='testTeacher'))), \
            'Should be a teacher object saved in the database'

    def test_admin_can_create_teacher_student_in_grade(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("admin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("admin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addNewUserBtn")))
        self.selenium.find_element_by_id('addNewUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_first_name")))
        self.selenium.find_element_by_id('id_first_name').send_keys('testNameGrade')
        self.selenium.find_element_by_id('id_last_name').send_keys('testSurnameGrade')
        self.selenium.find_element_by_id('id_email').send_keys('test@test.com')
        self.selenium.find_element_by_id('id_date_of_birth').send_keys('10.10.1997')
        sex = self.selenium.find_element_by_id('id_sex')
        for option in sex.find_elements_by_tag_name('option'):
            if option.text == 'Gutt':
                break
            else:
                ARROW_DOWN = u'\ue015'
                sex.send_keys(ARROW_DOWN)
        role = self.selenium.find_element_by_id('id_role')
        for option in role.find_elements_by_tag_name('option'):
            if option.text == 'Elev':
                break
            else:
                ARROW_DOWN = u'\ue015'
                role.send_keys(ARROW_DOWN)

        schools = self.selenium.find_element_by_id('schools')
        for option in schools.find_elements_by_tag_name('option'):
            if option.text == 'testSchool':
                break
            else:
                ARROW_DOWN = u'\ue015'
                schools.send_keys(ARROW_DOWN)
        grades = self.selenium.find_element_by_id('grades')
        for option in grades.find_elements_by_tag_name('option'):
            if option.text == 'testGrade':
                break
            else:
                ARROW_DOWN = u'\ue015'
                grades.send_keys(ARROW_DOWN)
        self.selenium.find_element_by_id('selectClassButton').click()
        time.sleep(0.1)
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        temp = Person.objects.get(first_name='testNameGrade')
        gradelist = temp.grades.all()
        self.assertEqual('testGrade', gradelist[0].grade_name), \
            'Should be a student object saved in the database'

        # Teacher
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addNewUserBtn")))
        self.selenium.find_element_by_id('addNewUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_first_name")))
        self.selenium.find_element_by_id('id_first_name').send_keys('testTeacher')
        self.selenium.find_element_by_id('id_last_name').send_keys('testTeacherSurname')
        self.selenium.find_element_by_id('id_email').send_keys('test@test.com')
        self.selenium.find_element_by_id('id_date_of_birth').send_keys('10.10.1997')
        sex = self.selenium.find_element_by_id('id_sex')
        for option in sex.find_elements_by_tag_name('option'):
            if option.text == 'Gutt':
                break
            else:
                ARROW_DOWN = u'\ue015'
                sex.send_keys(ARROW_DOWN)
        role = self.selenium.find_element_by_id('id_role')
        for option in role.find_elements_by_tag_name('option'):
            if option.text == 'Lærer':
                break
            else:
                ARROW_DOWN = u'\ue015'
                role.send_keys(ARROW_DOWN)

        schools = self.selenium.find_element_by_id('schools')
        for option in schools.find_elements_by_tag_name('option'):
            if option.text == 'testSchool':
                break
            else:
                ARROW_DOWN = u'\ue015'
                schools.send_keys(ARROW_DOWN)
        grades = self.selenium.find_element_by_id('grades')
        for option in grades.find_elements_by_tag_name('option'):
            if option.text == 'testGrade':
                break
            else:
                ARROW_DOWN = u'\ue015'
                grades.send_keys(ARROW_DOWN)
        self.selenium.find_element_by_id('selectClassButton').click()
        time.sleep(0.1)
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        temp2 = Person.objects.get(first_name='testTeacher')
        gradelist2 = temp2.grades.all()
        self.assertEqual('testGrade', gradelist2[0].grade_name), \
            'Should be a teacher object saved in the database'

    def test_schooladmin_can_create_teacher_student_with_school(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_username")))
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        self.selenium.find_element_by_id('logInBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addNewUserBtn")))
        self.selenium.find_element_by_id('addNewUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_first_name")))
        self.selenium.find_element_by_id('id_first_name').send_keys('testNameGrade')
        self.selenium.find_element_by_id('id_last_name').send_keys('testSurnameGrade')
        self.selenium.find_element_by_id('id_email').send_keys('test@test.com')
        self.selenium.find_element_by_id('id_date_of_birth').send_keys('10.10.1997')
        sex = self.selenium.find_element_by_id('id_sex')
        for option in sex.find_elements_by_tag_name('option'):
            if option.text == 'Gutt':
                break
            else:
                ARROW_DOWN = u'\ue015'
                sex.send_keys(ARROW_DOWN)
        role = self.selenium.find_element_by_id('id_role')
        for option in role.find_elements_by_tag_name('option'):
            if option.text == 'Elev':
                break
            else:
                ARROW_DOWN = u'\ue015'
                role.send_keys(ARROW_DOWN)

        schools = self.selenium.find_element_by_id('schools')
        for option in schools.find_elements_by_tag_name('option'):
            if option.text == 'testSchool':
                break
            else:
                ARROW_DOWN = u'\ue015'
                schools.send_keys(ARROW_DOWN)
        grades = self.selenium.find_element_by_id('grades')
        for option in grades.find_elements_by_tag_name('option'):
            if option.text == 'testGrade':
                break
            else:
                ARROW_DOWN = u'\ue015'
                grades.send_keys(ARROW_DOWN)
        self.selenium.find_element_by_id('selectClassButton').click()
        time.sleep(0.1)
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)
        temp = Person.objects.get(first_name='testNameGrade')
        gradelist = temp.grades.all()
        self.assertEqual('testGrade', gradelist[0].grade_name), \
            'Should be a student object saved in the database'

        # Teacher
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "addNewUserBtn")))
        self.selenium.find_element_by_id('addNewUserBtn').click()
        WebDriverWait(self.selenium, 10).until(EC.presence_of_element_located((By.ID, "id_first_name")))
        self.selenium.find_element_by_id('id_first_name').send_keys('testTeacher')
        self.selenium.find_element_by_id('id_last_name').send_keys('testTeacherSurname')
        self.selenium.find_element_by_id('id_email').send_keys('test@test.com')
        self.selenium.find_element_by_id('id_date_of_birth').send_keys('10.10.1997')
        sex = self.selenium.find_element_by_id('id_sex')
        for option in sex.find_elements_by_tag_name('option'):
            if option.text == 'Gutt':
                break
            else:
                ARROW_DOWN = u'\ue015'
                sex.send_keys(ARROW_DOWN)
        role = self.selenium.find_element_by_id('id_role')
        for option in role.find_elements_by_tag_name('option'):
            if option.text == 'Lærer':
                break
            else:
                ARROW_DOWN = u'\ue015'
                role.send_keys(ARROW_DOWN)
        schools = self.selenium.find_element_by_id('schools')
        for option in schools.find_elements_by_tag_name('option'):
            if option.text == 'testSchool':
                break
            else:
                ARROW_DOWN = u'\ue015'
                schools.send_keys(ARROW_DOWN)
        grades = self.selenium.find_element_by_id('grades')
        for option in grades.find_elements_by_tag_name('option'):
            if option.text == 'testGrade':
                break
            else:
                ARROW_DOWN = u'\ue015'
                grades.send_keys(ARROW_DOWN)
        self.selenium.find_element_by_id('selectClassButton').click()
        time.sleep(0.1)
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.1)

        temp2 = Person.objects.get(first_name='testTeacher')
        gradelist2 = temp2.grades.all()
        self.assertEqual('testGrade', gradelist2[0].grade_name), \
            'Should be a teacher object saved in the database'
