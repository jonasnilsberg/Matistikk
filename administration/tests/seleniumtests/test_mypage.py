from django.test import LiveServerTestCase
from mixer.backend.django import mixer
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities



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
        super(MyPageDetailViewTestCase, self).tearDown()

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
        self.assertNotIn('login', self.selenium.current_url), \
            'Login should not be in the url if the user was logged in successfully using the new password'
