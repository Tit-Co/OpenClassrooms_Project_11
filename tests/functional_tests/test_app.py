import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


class TestFunctionalApp:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, get_clubs, get_competitions):
        mocker.patch('server.clubs', get_clubs)
        mocker.patch('server.competitions', get_competitions)

        mocker.patch('server.save_clubs')
        mocker.patch('server.save_competitions')

    def test_signup(self, live_server):
        options = Options()
        options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

        gecko_service = Service(executable_path="tests/functional_tests/geckodriver.exe")

        browser = webdriver.Firefox(service=gecko_service, options=options)
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

        assert browser.find_element("tag name", "h2").text == "Welcome, doe@testclub.com"

        browser.quit()

    def test_login(self, live_server, get_credentials):
        options = Options()
        options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

        gecko_service = Service(executable_path="tests/functional_tests/geckodriver.exe")

        browser = webdriver.Firefox(service=gecko_service, options=options)
        browser.get(f"{live_server}/")

        email = browser.find_element(By.ID, "email")
        email.send_keys(get_credentials["email"])
        password = browser.find_element(By.ID, "password")
        password.send_keys(get_credentials["password"])
        login = browser.find_element(By.ID, "login")
        login.click()

        assert browser.find_element("tag name", "h2").text == "Welcome, kate@shelifts.co.uk"

        browser.quit()
