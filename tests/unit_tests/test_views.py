import time
import pytest
import utils

from flask import url_for


class TestUnitViews:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, get_clubs, get_competitions):
        mocker.patch('utils.clubs', get_clubs)
        mocker.patch('utils.competitions', get_competitions)
        mocker.patch('utils.save_clubs')
        mocker.patch('utils.save_competitions')

    @staticmethod
    def test_index_status_code_ok(client):
        """
        Test that the index page status code is 200
        Args:
            client (FlaskClient): A Flask client
        """
        client_response = client.get('/')
        assert client_response.status_code == 200

    @staticmethod
    def test_index_return_welcome(client):
        """
        Test that the index page is correctly return with appropriate information
        Args:
            client (FlaskClient): A Flask client
        """
        client_response = client.get('/')
        data = client_response.data.decode('utf-8')

        assert "Welcome to the GÜDLFT Portal!" in data
        assert ('Please enter your secretary email and your password to continue '
                'or <a href="/signUp">sign up</a>') in data
        assert "Email:" in data
        assert "Password:" in data

    @staticmethod
    def test_index_without_authentication_fails(client, get_credentials):
        """
        Test that the index page is returned with an error message and with 403 status code in case
         of non authentication
        Args:
            client (FlaskClient): A Flask client
            get_credentials (dict): The credentials
        """
        club = next((c for c in utils.clubs if c['email'] == get_credentials["email"]), None)
        client_response = client.get(f'/showSummary/{club["name"]}')
        assert client_response.status_code == 403
        assert "Not allow" in client_response.data.decode('utf-8')

    @staticmethod
    def test_index_mail_authentication_ok(client, get_credentials):
        """
        Test that the summary page is returned with a 200 status code in case of fine
        authentication
        Args:
            get_credentials (dict): The credentials
            client (FlaskClient): A Flask client
        """
        client_response = client.post('/showSummary', data=get_credentials)
        assert client_response.status_code == 200

    @staticmethod
    def test_index_mail_authentication_fails(client, get_bad_credentials):
        """
        Test that the summary page is returned with a 200 status code in case of fine
        authentication
        Args:
            get_credentials (dict): The credentials
            client (FlaskClient): A Flask client
        """
        client_response = client.post('/showSummary', data=get_bad_credentials)
        data = client_response.data.decode('utf-8')
        assert client_response.status_code == 403
        assert "Sorry, the password is incorrect." in data

    @staticmethod
    def test_index_mail_authentication_returns_summary(client, get_credentials):
        """
        Test that the summary page is returned with appropriate information from the club when
        authenticated
        Args:
            client (FlaskClient): A Flask client
            get_credentials (dict): The credentials
        """
        client_response = client.post('/showSummary', data=get_credentials)
        data = client_response.data.decode('utf-8')

        assert "Welcome, kate@shelifts.co.uk" in data
        assert "Spring Festival" in data
        assert "Fall Classic" in data
        assert "Points available: 12" in data

    @staticmethod
    def test_index_mail_authentication_not_found(client, get_unexisting_credentials):
        """
        Test that the index page is returned with an error message and with 302 status code in case
         of authentication with unknown mail.
        Args:
            client (FlaskClient): A Flask client
            get_unexisting_credentials (dict): The credentials
        """
        client_response = client.post('/showSummary', data=get_unexisting_credentials)
        data = client_response.data.decode('utf-8')
        assert client_response.status_code == 404
        assert "Sorry, that email was not found." in data

    @staticmethod
    def test_summary_logout_redirect_status_code_ok(client, get_credentials):
        """
        Test that the redirect (302) status code is returned in case of logging out.
        Args:
            client (FlaskClient): A Flask client
            get_credentials (dict): The credentials
        """
        client.post('/showSummary', data=get_credentials)
        logout_response = client.get('/logout')
        assert logout_response.status_code == 302

    @staticmethod
    def test_booking_status_code_ok(client,
                                    get_credentials,
                                    get_existing_competition_and_club):
        """
        Test that the 200 status code is returned in case of booking.
        Args:
            client (FlaskClient): A Flask client
            get_credentials (dict): The credentials
            get_existing_competition_and_club (dict): The competition and club
        """
        client.post('/showSummary', data=get_credentials)

        client_response = client.get(url_for(endpoint='book',
                                             competition=get_existing_competition_and_club['competition'],
                                             club=get_existing_competition_and_club['club']))

        assert client_response.status_code == 200

    @staticmethod
    def test_get_signup_status_code_ok(client):
        """
        Test that the 200 status code is returned in case of signup.
        Args:
            client (FlaskClient): A Flask client
        """
        client_response = client.get('/signUp')
        assert client_response.status_code == 200

    @staticmethod
    def test_get_signup_returns_welcome(client):
        """
        Test that the profile page is returned with appropriate information from the club when
        signing up
        Args:
            client (FlaskClient): A Flask client
        """
        client_response = client.get('/signUp')
        data = client_response.data.decode('utf-8')
        assert "Welcome to the GÜDLFT Portal!" in data
        assert "Registration" in data
        assert ("Club name:" in data)
        assert ("Email:" in data)
        assert ("Password:" in data)
        assert ("Confirm Password:" in data)

    @staticmethod
    def test_change_password_status_code_ok(client):
        """
        Test that the 200 status code is returned in case of changing password
        Args:
            client (FlaskClient): A Flask client
        """
        with client.session_transaction() as session:
            session["club"] = "She Lifts"

        client_response = client.get('/changePassword/She Lifts')
        assert client_response.status_code == 200

    @staticmethod
    def test_profile_ok(client):
        """
        Test that the 200 status code is returned in case of displaying profile by the connected
         club.
        Args:
            client (FlaskClient): A Flask client
        """
        with client.session_transaction() as session:
            session["club"] = "She Lifts"

        client_response = client.get('/profile/She Lifts')
        assert client_response.status_code == 200

    @staticmethod
    def test_profile_without_authentication_fails(client):
        """
        Test that the profile page is not accessible in case of non authentication.
        403 status code and an error message are returned.
        Args:
            client (FlaskClient): A Flask client
        """
        client_response = client.get('/profile/Simply Lift')
        assert client_response.status_code == 403
        assert "Not allow" in client_response.data.decode('utf-8')

    @staticmethod
    def test_profile_returns_welcome(client):
        """
        Test that the profile page is returned with appropriate information from the club when
        authenticated.
        Args:
            client (FlaskClient): A Flask client
        """
        with client.session_transaction() as session:
            session["club"] = "She Lifts"

        client_response = client.get('/profile/She Lifts')
        data = client_response.data.decode('utf-8')
        assert "Welcome, kate@shelifts.co.uk" in data
        assert "Profile" in data
        assert "Name : She Lifts" in data
        assert "Email : kate@shelifts.co.uk" in data
        assert "Points available: 12" in data

    @staticmethod
    def test_points_board_status_code_ok(client):
        """
        Test that the 200 status code and appropriate information are returned in case of
        displaying points board.
        Args:
            client ():
        """
        client_response = client.get('/pointsBoard')
        data = client_response.data.decode('utf-8')
        assert client_response.status_code == 200
        assert "Welcome to the GÜDLFT Portal!" in data
        assert "⯈ Here is the board for all the clubs and their points." in data

    @staticmethod
    def test_post_signup_status_code_ok(client, get_details_2):
        client_response = client.post('/profile', data=get_details_2, follow_redirects=True)

        assert client_response.status_code == 200

    @staticmethod
    def test_post_signup_returns_welcome(client, get_details_2):
        client_response = client.post('/profile', data=get_details_2, follow_redirects=True)

        data = client_response.data.decode('utf-8')

        assert "Welcome, admin@test.com" in data
        assert "Profile" in data
        assert "Name : Name Test" in data
        assert "Email : admin@test.com" in data
        assert "Points available: 15" in data

    @staticmethod
    def test_post_signup_fails(client, get_wrong_details_2):
        client_response = client.post('/profile', data=get_wrong_details_2, follow_redirects=True)

        data = client_response.data.decode('utf-8')

        assert "Sorry, please fill all fields." in data
        assert "Welcome to the GÜDLFT Portal!" in data
        assert "Registration" in data
        assert ("Club name:" in data)
        assert ("Email:" in data)
        assert ("Password:" in data)
        assert ("Confirm Password:" in data)
