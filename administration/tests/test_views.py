from django.test import LiveServerTestCase
from ..models import Person, School, Grade
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class PersonDetailViewTestCase(LiveServerTestCase):
    def setUp(self):
        # DB setup
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')  # Password has to be set like this because of the hash-function
        obj.save()

        schooladminobj = mixer.blend('administration.Person', role=3, username='schooladmin')
        schooladminobj.set_password('schooladmin')
        schooladminobj.save()

        schoolobj = mixer.blend('administration.School', school_administrator=schooladminobj)
        schoolobj.save()

        gradeobj = mixer.blend('administration.Grade', school=schoolobj)
        gradeobj.save()

        teacherobj = mixer.blend('administration.Person', role=2, grades=gradeobj, username='teacher')
        teacherobj.set_password('teacher')
        teacherobj.save()

        studentobj = mixer.blend('administration.Person', role=1, grades=gradeobj, username='student')
        studentobj.set_password('student')
        studentobj.save()

        schooladminobj2 = mixer.blend('administration.Person', role=3, username='schooladmin2')
        schooladminobj2.set_password('schooladmin2')
        schooladminobj2.save()

        teacherobj2 = mixer.blend('administration.Person', role=2, username='teacher2')
        teacherobj2.set_password('teacher2')
        teacherobj2.save()

        #  Webdriver setup
        server_url = "http://%s:%s/wd/hub" % ('127.0.0.1', '4444')  # ip address and port
        dc = DesiredCapabilities.HTMLUNITWITHJS
        self.selenium = webdriver.Remote(server_url, dc)
        super(PersonDetailViewTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(PersonDetailViewTestCase, self).tearDown()

    def test_teacher_can_edit_student_information(self):
        """ Checks that a teacher can edit the surname of a student in one of their classes"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )

        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("teacher")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("teacher")
        self.selenium.find_element_by_id('logInBtn').click()
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
        )
        self.selenium.find_element_by_id('editUserBtn').click()
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('studentsurname')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        self.assertEqual('studentsurname', Person.objects.filter(role=1)[0].last_name),\
            'Teacher should be able to edit information about a student in on of their classes'

    def test_schooladmin_can_edit_student_and_teacher_information(self):
        """ Checks that a schooladministrator can edit the surname of a student or a teacher at their school"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )

        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        self.selenium.find_element_by_id('logInBtn').click()
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
        )
        self.selenium.find_element_by_id('editUserBtn').click()
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('student')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        self.assertEqual('student', Person.objects.filter(role=1)[0].last_name), \
            'Schooladministrator should be able to change the information of a student in a class at their school'

        #teacher
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/teacher")
        )
        self.selenium.find_element_by_id('editUserBtn').click()
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('teacher')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        self.assertEqual('teacher', Person.objects.filter(role=2)[0].last_name), \
            'Schooladministrator should be able to change the information of a teacher in a class at their school'

    def test_admin_can_edit_schooladmin_teacher_student_information(self):
        """ Checks that a administrator can edit the surname of a schooladministrator, student or a teacher at 
        their school"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )

        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("admin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("admin")
        self.selenium.find_element_by_id('logInBtn').click()
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
        )
        self.selenium.find_element_by_id('editUserBtn').click()
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('studsurname')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        self.assertEqual('studsurname', Person.objects.filter(role=1)[0].last_name),\
            'Admin should be able to change the information about a student'

        # teacher
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/teacher")
        )
        self.selenium.find_element_by_id('editUserBtn').click()
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('teachersurname')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        self.assertEqual('teachersurname', Person.objects.filter(role=2)[0].last_name),\
            'Admin should be able to change the information about a teacher'

        # Schooladmin
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/schooladmin")
        )
        self.selenium.find_element_by_id('editUserBtn').click()
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('schooladmin')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        self.assertEqual('schooladmin', Person.objects.filter(role=3)[0].last_name),\
            'Admin should be able to change the information about a schooladmin'

    def test_teacher_can_not_edit_student_information(self):
        """ Checks that a teacher can't edit information about a student not in one of their classes"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("teacher2")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("teacher2")
        try:
            self.selenium.find_element_by_id('logInBtn').click()
            self.selenium.get(
                '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
            )
            self.selenium.find_element_by_id('editUserBtn').click()
            self.selenium.find_element_by_id('id_last_name').clear()
            self.selenium.find_element_by_id('id_last_name').send_keys('studsur')
            self.selenium.find_element_by_id('saveNewInfoBtn').click()
        except NoSuchElementException:
            None
        self.assertNotEqual('studsur', Person.objects.filter(role=1)[0].last_name), \
            'Teacher should not be able to change password of a student not in their class'

    def test_schooladmin_can_not_edit_student_and_teacher_information(self):
        """ Checks that a schooladministrator can't edit information about a teacher or a student not in their school"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin2")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin2")
        self.selenium.find_element_by_id('logInBtn').click()
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
        )
        try:
            self.selenium.find_element_by_id('editUserBtn').click()
            self.selenium.find_element_by_id('id_last_name').clear()
            self.selenium.find_element_by_id('id_last_name').send_keys('studsurn')
            self.selenium.find_element_by_id('saveNewInfoBtn').click()
        except NoSuchElementException:
            None
        self.assertNotEqual('studsurn', Person.objects.filter(role=1)[0].last_name),\
            'Schooladmin should not be able to edit information about a student at a different school'

        #teacher
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/teacher")
        )
        try:
            self.selenium.find_element_by_id('editUserBtn').click()
            self.selenium.find_element_by_id('id_last_name').clear()
            self.selenium.find_element_by_id('id_last_name').send_keys('teachersurn')
            self.selenium.find_element_by_id('saveNewInfoBtn').click()
        except NoSuchElementException:
            None
        self.assertNotEqual('teachersurn', Person.objects.filter(role=2)[0].last_name), \
            'Schooladmin should not be able to change password of a teacher not in their school'

    def test_change_password(self):
        """Checks that a teacher can change the password of a student in their class"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("teacher")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("teacher")
        self.selenium.find_element_by_id('logInBtn').click()
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
        )
        self.selenium.find_element_by_id('updatePasswordModalBtn').click()
        self.selenium.implicitly_wait(2)
        self.selenium.find_element_by_id('id_password').send_keys('studentpassword')
        self.selenium.find_element_by_id('id_password2').send_keys('studentpassword')
        self.selenium.find_element_by_id('updatePasswordBtn').click()
        self.selenium.find_element_by_id('logout').click()
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("student")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("studentpassword")
        self.selenium.find_element_by_id('logInBtn').click()
        self.assertNotIn('login', self.selenium.current_url),\
            'Login should not be in the url if the user was logged in successfully using the new password'


class MyPageDetailViewTestCase(LiveServerTestCase):
    def setUp(self):
        # DB setup
        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')
        obj.save()

        schooladminobj = mixer.blend('administration.Person', role=3, username='schooladmin')
        schooladminobj.set_password('schooladmin')
        schooladminobj.save()

        #  Webdriver setup
        server_url = "http://%s:%s/wd/hub" % ('127.0.0.1', '4444')  # ip address and port
        dc = DesiredCapabilities.HTMLUNITWITHJS
        self.selenium = webdriver.Remote(server_url, dc)
        self.selenium.maximize_window()
        super(MyPageDetailViewTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(MyPageDetailViewTestCase  , self).tearDown()

    def test_change_password(self):
        """Checks that a user can view their page and change their password through it"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        self.selenium.find_element_by_id('logInBtn').click()
        self.selenium.find_element_by_id('myPageBtn').click()
        self.selenium.find_element_by_id('changePasswordModalBtn').click()
        self.selenium.implicitly_wait(2)
        self.selenium.find_element_by_id('id_old_password').send_keys('schooladmin')
        self.selenium.find_element_by_id('id_new_password1').send_keys('ntnu1234')
        self.selenium.find_element_by_id('id_new_password2').send_keys('ntnu1234')
        self.selenium.find_element_by_id('changePasswordBtn').click()
        self.selenium.find_element_by_id('logout').click()
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("ntnu1234")
        self.selenium.find_element_by_id('logInBtn').click()
        self.assertNotIn('login', self.selenium.current_url),\
            'Login should not be in the url if the user was logged in successfully using the new password'


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
        """server_url = "http://%s:%s/wd/hub" % ('127.0.0.1', '4444')  # ip address and port
        dc = DesiredCapabilities.HTMLUNITWITHJS
        self.selenium = webdriver.Remote(server_url, dc)"""
        self.selenium = webdriver.PhantomJS()
        self.selenium.maximize_window()
        super(PersonCreateViewTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(PersonCreateViewTestCase, self).tearDown()

    def test_admin_can_create_all_usertypes_without_school(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("admin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("admin")
        self.selenium.find_element_by_id('logInBtn').click()
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/nybruker")
        )

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

        self.assertEqual(1, len(Person.objects.filter(role=1, first_name='testName'))),\
            'Should be a student object saved in the database'
        # Teacher
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/nybruker")
        )
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

        self.assertEqual(1, len(Person.objects.filter(role=2, first_name='testNameTeacher'))),\
            'Should be a Teacher object saved in the database'

        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/nybruker")
        )
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
        self.assertEqual(1, len(Person.objects.filter(role=3, first_name='testNameSAdmin'))), \
        'Should be a schooladministrator object saved in the database'

    def test_schooladmin_can_create_teacher_student_without_school(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        self.selenium.find_element_by_id('logInBtn').click()
        # Student
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/nybruker")
        )
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
        self.assertEqual(1, len(Person.objects.filter(role=1, first_name='testName'))),\
            'Should be a student object saved in the database'
        # Teacher
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/nybruker")
        )
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
        self.assertEqual(1, len(Person.objects.filter(role=2, first_name='testTeacher'))),\
            'Should be a teacher object saved in the database'
"""
    def test_schooladmin_can_create_teacher_student_with_school(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        self.selenium.find_element_by_id('logInBtn').click()
        # Student
        import time
        time.sleep(0.5)
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/nybruker")
        )
        time.sleep(0.5)
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
        import time
        time.sleep(2)
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        import pdb;pdb.set_trace()
        self.assertEqual(1, len(Person.objects.filter(role=1, first_name='testNameGrade'))), \
        'Should be a student object saved in the database'
        
        # Teacher
        
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/nybruker")
        )
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
        import pdb;
        pdb.set_trace()
        self.assertEqual(1, len(Person.objects.filter(role=2, first_name='testTeacher'))), \
        'Should be a teacher object saved in the database'
        """