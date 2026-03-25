import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


class TestFunctionalApp:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, get_clubs, get_competitions):
        mocker.patch('utils.clubs', get_clubs)
        mocker.patch('utils.competitions', get_competitions)

        mocker.patch('utils.save_clubs')
        mocker.patch('utils.save_competitions')

    def test_signup(self, live_server):
        """
        Test that the signup process is correctly done with given details.
        Args:
            live_server (threading.Thread): A live server fixture.
        """
        browser = webdriver.Chrome()
        browser.get(f"{live_server}/signUp")

        name = browser.find_element(By.ID, "name")
        name.send_keys("Test Club")
        email = browser.find_element(By.ID, "email")
        email.send_keys("doe@testclub.com")
        password1 = browser.find_element(By.ID, "password")
        password1.send_keys("tgl_Prn_C6")
        password2 = browser.find_element(By.ID, "confirm-password")
        password2.send_keys("tgl_Prn_C6")
        signup = browser.find_element(By.ID, "signup")
        signup.click()

        time.sleep(1)

        assert browser.find_element("tag name", "h2").text == "Welcome, doe@testclub.com"

        browser.quit()

    def test_login(self, live_server, get_credentials):
        """
        Test that the login process is correctly done with given credentials.
        Args:
            live_server (threading.Thread): A live server fixture.
            get_credentials (dict): The credentials.
        """
        browser = webdriver.Chrome()
        browser.get(f"{live_server}/")

        email = browser.find_element(By.ID, "email")
        email.send_keys(get_credentials["email"])
        password = browser.find_element(By.ID, "password")
        password.send_keys(get_credentials["password"])
        login = browser.find_element(By.ID, "login")
        login.click()

        time.sleep(1)

        assert browser.find_element("tag name", "h2").text == "Welcome, kate@shelifts.co.uk"

        browser.quit()
