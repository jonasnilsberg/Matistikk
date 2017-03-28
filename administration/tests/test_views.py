from django.test import LiveServerTestCase
from ..models import Person
import time
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class PersonDetailViewTestCase(LiveServerTestCase):
    def setUp(self):

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
        self.selenium = webdriver.Firefox()
        self.selenium.maximize_window()
        super(PersonDetailViewTestCase, self).setUp()

    def tearDown(self):
        # Call tearDown to close the web browser
        self.selenium.quit()
        super(PersonDetailViewTestCase, self).tearDown()

    def test_edit_user_information(self):
        """ Edits a students surname from their teachers account."""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )

        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("teacher")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("teacher")
        self.selenium.find_element_by_id('logInBtn').click()
        time.sleep(0.5)
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
        )
        time.sleep(0.5)
        self.selenium.find_element_by_id('editUserBtn').click()
        time.sleep(0.5)
        self.selenium.find_element_by_id('id_last_name').clear()
        self.selenium.find_element_by_id('id_last_name').send_keys('studentetternavn')
        self.selenium.find_element_by_id('saveNewInfoBtn').click()
        time.sleep(0.5)
        self.selenium.refresh()
        self.assertEqual('studentetternavn', Person.objects.filter(role=1)[0].last_name)

    def test_change_password(self):
        """Checks that a teacher can change the password of a student in their class"""
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )

        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("teacher")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("teacher")
        # Locate Login button and click it
        self.selenium.find_element_by_id('logInBtn').click()
        time.sleep(0.5)  # vente på at innloggingen registreres
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/administrasjon/brukere/student")
        )
        time.sleep(0.5)  # vente på at urlen lastes
        self.selenium.find_element_by_id('updatePasswordModalBtn').click()
        time.sleep(0.5)  # Vente på at modalen skal åpnes
        self.selenium.find_element_by_id('id_password').send_keys('studentpassword')
        self.selenium.find_element_by_id('id_password2').send_keys('studentpassword')
        self.selenium.find_element_by_id('updatePasswordBtn').click()
        time.sleep(0.5)   # vente på at modalen lukkes
        self.selenium.find_element_by_id('logout').click()
        time.sleep(0.5)  # Vente på at innloggingsiden lastes

        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("student")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("studentpassword")
        self.selenium.find_element_by_id('logInBtn').click()
        time.sleep(0.5)  # Vente på at urlen lastes
        self.assertNotIn('login', self.selenium.current_url)


class LoginAndMyPageDetailViewTestCase(LiveServerTestCase):
    def setUp(self):

        obj = mixer.blend('administration.Person', role=4, username='admin')
        obj.set_password('admin')
        obj.save()
        schooladminobj = mixer.blend('administration.Person', role=3, username='schooladmin')
        schooladminobj.set_password('schooladmin')
        schooladminobj.save()
        self.selenium = webdriver.Firefox()
        self.selenium.maximize_window()
        super(LoginAndMyPageDetailViewTestCase, self).setUp()

    def tearDown(self):
        # Call tearDown to close the web browser
        self.selenium.quit()
        super(LoginAndMyPageDetailViewTestCase, self).tearDown()

    def test_login_and_navigate(self):
        """
        Logs in as an admin and navigates to the admins mypage site through the main menu.
        """
        # Open the django admin page.
        # DjangoLiveServerTestCase provides a live server url attribute
        # to access the base url in tests
        self.selenium.get(
            '%s%s' % (self.live_server_url,  "/")
        )

        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("admin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("admin")
        # Locate Login button and click it
        self.selenium.find_element_by_id('logInBtn').click()
        self.selenium.implicitly_wait(5)
        my_page_button = self.selenium.find_element_by_id('myPageBtn')
        time.sleep(0.5)  # wait for python to make myPageBtn clickable, can't use implicitly wait here
        my_page_button.click()
        time.sleep(0.5)  # wait for selenium to change window therefore url, can't use implicitly wait here
        self.assertIn('minside', self.selenium.current_url)

    def test_change_password(self):
        self.selenium.get(
            '%s%s' % (self.live_server_url, "/")
        )

        # Fill login information of admin
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("schooladmin")
        # Locate Login button and click it
        self.selenium.find_element_by_id('logInBtn').click()
        time.sleep(0.5)
        self.selenium.implicitly_wait(5)
        my_page_button = self.selenium.find_element_by_id('myPageBtn')
        time.sleep(0.5)  # wait for python to make myPageBtn clickable, can't use implicitly wait here
        my_page_button.click()
        time.sleep(0.5)
        self.selenium.find_element_by_id('changePasswordModalBtn').click()
        time.sleep(0.5)
        self.selenium.find_element_by_id('id_old_password').send_keys('schooladmin')
        self.selenium.find_element_by_id('id_new_password1').send_keys('ntnu1234')
        self.selenium.find_element_by_id('id_new_password2').send_keys('ntnu1234')
        self.selenium.find_element_by_id('changePasswordBtn').click()
        time.sleep(0.5)  # vente på at modalen lukkes
        self.selenium.find_element_by_id('logout').click()
        time.sleep(0.5)  # Vente på at innloggingsiden lastes
        username = self.selenium.find_element_by_id('id_username')
        username.send_keys("schooladmin")
        password = self.selenium.find_element_by_id('id_password')
        password.send_keys("ntnu1234")
        self.selenium.find_element_by_id('logInBtn').click()
        time.sleep(0.5)  # Vente på at urlen lastes
        self.assertNotIn('login', self.selenium.current_url)

"""from django_webtest import WebTest
from ..models import Person
from .. import views, forms
from mixer.backend.django import mixer
class MyTestCase(WebTest):
    # optional: we want some initial data to be able to login
    # optional: default extra_environ for this TestCase
    extra_environ = {'HTTP_ACCEPT_LANGUAGE': 'no'}
    def testLogin(self):
        obj = mixer.blend('administration.Person', role=1)
        index = self.app.get('/', user=obj.username)
        import pdb; pdb.set_trace()
        # All the webtest API is available. For example, we click
        # on a <a href='/tech-blog/'>Blog</a> link, check that it
        # works (result page doesn't raise exceptions and returns 200 http
        # code) and test if result page have 'My Article' text in
        # its body.
from django.test import TestCase, Client
from ..models import Person
from .. import views, forms
from mixer.backend.django import mixer
from django.core.urlresolvers import reverse
class TestPersonDetailView(TestCase):
    @classmethod
    def setUpTestData(cls):
        #Create new student-user
        obj = mixer.blend('administration.Person', role=1)
        obj.createusername()
        obj.set_password('passord')
        obj.save()
        #creates an administrator
        obj2 = mixer.blend('administration.Person', role=4)
        obj2.set_password('passord')
        obj2.save()
    def test_personDisplayView(self):
        obj = Person.objects.filter(role=1)[0]
        client = Client()
        logged_in = client.login(username=obj.username, password='passord')
        self.assertEqual(logged_in, True)
        kwargs = {'slug': obj.username}
        response = client.get(reverse('administration:personDetail', kwargs=kwargs))
        self.assertIn('/' + obj.username + '/', response.url)
    def test_changePasswordView(self):
        client = Client()
        obj = Person.objects.filter(role=1)[0]
        obj2 = Person.objects.filter(role=4)[0]
        c = client.login(username=obj2.username, password='passord')
        self.assertEqual(c, True)
        data = {'password': 'passord2', 'password2': 'passord2'}
        kwargs = {'slug': obj.username}
        client.post(reverse('administration:personDetail', kwargs=kwargs), data=data)
        c = client.login(username=obj.username, password='passord2')
        self.assertEqual(c, True)
class TestPersonUpdateView(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create new student-user
        obj = mixer.blend('administration.Person', role=1)
        obj.createusername()
        obj.set_password('passord')
        obj.save()
        # creates an administrator
        obj2 = mixer.blend('administration.Person', role=4)
        obj2.set_password('passord')
        obj2.save()
    def test_getPersonUpdateView(self):
        obj = Person.objects.filter(role=1)[0]
        obj2 = Person.objects.filter(role=4)[0]
        client = Client()
        logged_in = client.login(username=obj2.username, password='passord')
        self.assertTrue(logged_in)
        kwargs = {'slug': obj.username}
        response = client.get(reverse('administration:personUpdate', kwargs=kwargs))
        self.assertEqual(response.status_code, 200)
    def test_postAll(self):
        obj = Person.objects.filter(role=1)[0]
        obj2 = Person.objects.filter(role=4)[0]
        client = Client()
        logged_in = client.login(username=obj2.username, password='passord')
        self.assertTrue(logged_in)
        kwargs = {'slug': obj.username}
        data = {'first_name': 'jani'}
        response = client.get(reverse('administration:personUpdate', kwargs=kwargs))
        client.post(reverse('administration:personUpdate', kwargs=kwargs), data={'first_name': 'jani'})
        import pdb; pdb.set_trace()
"""
