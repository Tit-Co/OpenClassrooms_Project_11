import pytest
import utils

from bs4 import BeautifulSoup
from flask import url_for


class TestIntegrationViews:
    @pytest.fixture(autouse=True, scope='function')
    def setup(self, mocker, get_clubs, get_competitions):
        mocker.patch('utils.clubs', get_clubs)
        mocker.patch('utils.competitions', get_competitions)

        mocker.patch('utils.save_clubs')
        mocker.patch('utils.save_competitions')

    @staticmethod
    def test_summary_logout_redirect_returns_welcome(client, get_credentials):
        """
        Test that the logout redirects to the index page with the 200 status code and appropriate
         information.
        Args:
            client (FlaskClient): A Flask client
            get_credentials (dict): The credentials
        """
        client.post('/showSummary', data=get_credentials)

        logout_response = client.get('/logout')
        soup = BeautifulSoup(logout_response.data.decode(), features="html.parser")
        url = soup.find_all('a')[0].get('href')
        redirect_response = client.get(url, follow_redirects=True)

        assert redirect_response.status_code == 200
        data = redirect_response.data.decode('utf-8')

        assert "Welcome to the GUDLFT Portal!" in data
        assert "Authentication" in data
        assert ('Please enter your secretary email and your password to continue '
                'or <a href="/signUp">sign up</a>') in data
        assert "Email:" in data
        assert "Password:" in data

    @staticmethod
    def test_booking_return_festival_page_booking(client,
                                                  get_credentials,
                                                  get_existing_competition_and_club):
        """
        Test that the competition bookin page is returned with the appropriate information.
        Args:
            client (FlaskClient): A Flask client
            get_credentials (dict): The credentials
            get_existing_competition_and_club (dict): The competition and club
        """
        client.post('/showSummary', data=get_credentials)

        client_response = client.get(url_for(endpoint='book',
                                      competition=get_existing_competition_and_club['competition'],
                                      club=get_existing_competition_and_club['club']))
        data = client_response.data.decode('utf-8')
        assert "Spring Festival" in data
        assert "Places available: " in data
        assert "How many places?" in data

    @staticmethod
    def test_good_purchasing_places_returns_summary_page(client,
                                                         get_credentials,
                                                         get_consistent_purchasing_data):
        """
        Test that the competition purchasing page is returned with the 200 status code and the
        appropriate information.
        Args:
            client (FlaskClient): A Flask client
            get_credentials (dict): The credentials
            get_consistent_purchasing_data (dict): The competition and club
        """
        client.post('/showSummary', data=get_credentials)

        purchasing_data = get_consistent_purchasing_data
        the_club = [club for club in utils.clubs if club["name"] == purchasing_data['club']][0]
        the_competition =[competition for competition in utils.competitions
                          if competition["name"] == purchasing_data['competition']][0]

        client.get(url_for(endpoint='book',
                           competition=the_competition['name'],
                           club=the_club['name']))

        club_points = the_club['points']
        competition_places = the_competition['number_of_places']

        client_response = client.post('/purchasePlaces', data=purchasing_data)
        data = client_response.data.decode('utf-8')

        new_points = int(club_points) - int(purchasing_data['places'])
        new_competition_places = int(competition_places) - int(purchasing_data['places'])

        soup = BeautifulSoup(data, features="html.parser")
        all_li_str = [str(li) for li in soup.find_all('li')]
        expected_li = "".join(all_li_str)
        the_club_name_utf8 = "%20".join(the_club['name'].split())
        the_competition_name_utf8 = "%20".join(the_competition['name'].split())

        li = f"""<li class="competition">
        <b>{the_competition["name"]}</b><br/>
        Date: 2026-07-27 10:00:00<br/>
        Number of Places: {new_competition_places}<br/><br/>
        <a class="book" href="/book/{the_competition_name_utf8}/{the_club_name_utf8}">Book Places</a>
        </li>"""

        assert client_response.status_code == 200
        assert (f"Great! Booking of {purchasing_data['places']} place(s) for "
                f"{purchasing_data['competition']} competition complete!") in data
        assert f"Welcome, {the_club["email"]} " in data
        assert " ".join(li.split()) in " ".join(expected_li.split())
        assert f"Points available: {new_points}" in data

    @staticmethod
    def test_purchasing_places_not_enough_points_returns_sorry(client,
                                                               get_credentials_2,
                                                               get_existing_competition_and_club_2,
                                                               get_inconsistent_purchasing_data):
        """
        Test that the 403 status code and an error message are returned in case of not enough
        points while purchasing.
        Args:
            client (FlaskClient): A Flask client
            get_credentials_2 (dict): The credentials
            get_existing_competition_and_club_2 (dict): The competition and club
            get_inconsistent_purchasing_data (dict): The purchasing data
        """
        client.post('/showSummary', data=get_credentials_2)
        client.get(url_for(endpoint='book',
                           competition=get_existing_competition_and_club_2['competition'],
                           club=get_existing_competition_and_club_2['club']))

        the_club = [club for club in utils.clubs
                    if club["name"] == get_existing_competition_and_club_2['club']][0]

        client_response = client.post('/purchasePlaces', data=get_inconsistent_purchasing_data)
        data = client_response.data.decode('utf-8')

        assert client_response.status_code == 200
        assert "Not enough points" in data
        assert f"Welcome, {the_club["email"]} " in data
        assert "Sorry, you do not have enough points to purchase." in data
        assert f"Points available: {the_club['points']}" in data

    @staticmethod
    def test_purchasing_places_over_12_places_returns_sorry(client,
                                                            get_credentials,
                                                            purchasing_over_12_places):
        """
        Test that the 403 status code and an error message are returned in case of purchasing more
        than 12 places.
        Args:
            client (FlaskClient): A Flask client
            get_credentials (dict): The credentials
            purchasing_over_12_places (dict): The purchasing data
        """
        client.post('/showSummary', data=get_credentials)

        purchasing_data = purchasing_over_12_places

        client.get(url_for(endpoint='book',
                           competition=purchasing_data['competition'],
                           club=purchasing_data['club']))

        the_club = [club for club in utils.clubs if club["name"] == purchasing_data['club']][0]
        club_points = the_club['points']

        client_response = client.post('/purchasePlaces', data=purchasing_data)
        data = client_response.data.decode('utf-8')

        assert client_response.status_code == 200
        assert "Over 12 places" in data
        assert f"Welcome, {the_club["email"]} " in data
        assert "Sorry, you are not allow to purchase more than 12 places for this competition." in data
        assert f"Points available: {club_points}" in data

    @staticmethod
    def test_purchasing_places_over_12_cumulative_places_returns_sorry(client,
                                                                       get_credentials,
                                                                       purchasing_13_cumulative_places):
        """
        Test that the 403 status code and an error message are returned in case of purchasing more
        than 12 cumulative places.
        Args:
            client (FlaskClient): A Flask client
            get_credentials (dict): The credentials
            purchasing_13_cumulative_places (dict): The purchasing data
        """
        client.post('/showSummary', data=get_credentials)

        purchasing_data = purchasing_13_cumulative_places

        client.get(url_for(endpoint='book',
                           competition=purchasing_data['competition'],
                           club=purchasing_data['club']))

        the_club = [club for club in utils.clubs if club["name"] == purchasing_data['club']][0]
        club_points = the_club['points']

        client_response = client.post('/purchasePlaces', data=purchasing_data)
        data = client_response.data.decode('utf-8')

        assert client_response.status_code == 200
        assert f"Welcome, {the_club["email"]} " in data
        assert "Over 12 places" in data
        assert "Sorry, you are not allow to purchase more than 12 places for this competition." in data
        assert f"Points available: {club_points}" in data

    @staticmethod
    def test_purchasing_places_negative_number_returns_sorry(client,
                                                             get_credentials,
                                                             purchasing_with_negative_places):
        """
        Test that the 403 status code and an error message are returned in case of purchasing with
        negative value of places.
        Args:
            client (FlaskClient): A Flask client
            get_credentials (dict): The credentials
            purchasing_with_negative_places (dict): The purchasing data
        """
        client.post('/showSummary', data=get_credentials)

        purchasing_data = purchasing_with_negative_places

        client.get(url_for(endpoint='book',
                           competition=purchasing_data['competition'],
                           club=purchasing_data['club']))

        the_club = [club for club in utils.clubs if club["name"] == purchasing_data['club']][0]
        club_points = the_club['points']

        client_response = client.post('/purchasePlaces', data=purchasing_data)
        data = client_response.data.decode('utf-8')

        assert client_response.status_code == 200
        assert "Negative number" in data
        assert f"Welcome, {the_club["email"]} " in data
        assert "Sorry, you should type a positive number." in data
        assert f"Points available: {club_points}" in data

    @staticmethod
    def test_purchasing_places_past_competitions_returns_sorry(client,
                                                               get_credentials_2,
                                                               get_existing_competition_and_club_3):
        """
        Test that the 403 status code and an error message are returned in case of outdated
        competition.
        Args:
            client (FlaskClient): A Flask client
            get_credentials_2 (dict): The credentials
            get_existing_competition_and_club_3 (dict): The competition and club
        """
        client.post('/showSummary', data=get_credentials_2)

        client_response = client.get(url_for(endpoint='book',
                           competition=get_existing_competition_and_club_3['competition'],
                           club=get_existing_competition_and_club_3['club']))

        data = client_response.data.decode('utf-8')

        assert client_response.status_code == 200
        assert "Outdated" in data
        assert "Sorry, this competition is outdated. Booking not possible." in data

    @staticmethod
    def test_purchasing_places_over_available_returns_sorry(client,
                                                            get_credentials,
                                                            purchasing_places_more_than_available):
        """
        Test that the 403 status code and an error message are returned in case of purchasing more
        than places available in the competition.
        Args:
            client (FlaskClient): A Flask client
            get_credentials (dict): The credentials
            purchasing_places_more_than_available (dict): The purchasing data
        """
        client.post('/showSummary', data=get_credentials)

        purchasing_data = purchasing_places_more_than_available

        client.get(url_for(endpoint='book',
                           competition=purchasing_data['competition'],
                           club=purchasing_data['club']))

        the_club = [club for club in utils.clubs if club["name"] == purchasing_data['club']][0]
        club_points = the_club['points']

        client_response = client.post('/purchasePlaces', data=purchasing_data)
        data = client_response.data.decode('utf-8')

        assert client_response.status_code == 200
        assert "Not enough places" in data
        assert f"Welcome, {the_club["email"]} " in data
        assert "Sorry, there are not enough places available for this competition." in data
        assert f"Points available: {club_points}" in data

    @staticmethod
    def test_purchasing_places_sold_out_status_code_error(client,
                                                          get_credentials_3,
                                                          get_existing_competition_and_club_4):
        """
        Test that the 403 status code and an error message are returned in case of purchasing in a
        sold out competition.
        Args:
            client (FlaskClient): A Flask client
            get_credentials_3 (dict): The credentials
            get_existing_competition_and_club_4 (dict): The competition and club
        """
        client.post('/showSummary', data=get_credentials_3)

        client_response = client.get(url_for(endpoint='book',
                           competition=get_existing_competition_and_club_4['competition'],
                           club=get_existing_competition_and_club_4['club']))

        data = client_response.data.decode('utf-8')

        assert client_response.status_code == 200
        assert "Sold out" in data
        assert "Sorry, this competition is sold out. Booking not possible." in data

    @staticmethod
    def test_change_password_status_code_ok(client,
                                            get_credentials_3,
                                            get_existing_competition_and_club_4):
        """
        Test that the 200 status code and appropriate information are returned in case of correct
        changing password
        Args:
            client (FlaskClient): A Flask client
            get_credentials_3 (dict): The credentials
            get_existing_competition_and_club_4 (dict): The competition and club
        """
        client.post('/showSummary', data=get_credentials_3)

        passwords = {
            "password": "tr_nl_er4",
            "confirm_password": "tr_nl_er4",
        }

        client_response = client.post(f'/changePassword/{get_existing_competition_and_club_4["club"]}',
                                      data=passwords)

        data = client_response.data.decode('utf-8')

        assert client_response.status_code == 200
        assert "Great! You have successfully changed your password." in data

    @staticmethod
    def test_change_password_match_fails(client,
                                   get_credentials_3,
                                   get_existing_competition_and_club_4):
        """
        Test that the 406 status code and an error message are returned in case of incorrect
        changing password.
        Args:
            client (FlaskClient): A Flask client
            get_credentials_3 (dict): The credentials
            get_existing_competition_and_club_4 (dict): The competition and club
        """
        client.post('/showSummary', data=get_credentials_3)

        passwords = {
            "password": "tr_Pl_er4",
            "confirm_password": "tr_nl_er4",
        }

        client_response = client.post(f'/changePassword/{get_existing_competition_and_club_4["club"]}',
                                      data=passwords)

        data = client_response.data.decode('utf-8')

        assert client_response.status_code == 200
        assert "Passwords not match" in data
        assert "Sorry, passwords do not match." in data

    @staticmethod
    def test_change_password_identical(client,
                                         get_credentials_3,
                                         get_existing_competition_and_club_4):
        """
        Test that the 406 status code and an error message are returned in case of changing
        password with identical password as current.
        Args:
            client (FlaskClient): A Flask client
            get_credentials_3 (dict): The credentials
            get_existing_competition_and_club_4 (dict): The competition and club
        """
        client.post('/showSummary', data=get_credentials_3)

        passwords = {
            "password": "tp4_Tmn40",
            "confirm_password": "tp4_Tmn40",
        }

        client_response = client.post(f'/changePassword/{get_existing_competition_and_club_4["club"]}',
                                      data=passwords)

        data = client_response.data.decode('utf-8')

        assert client_response.status_code == 200
        assert "Identical password" in data
        assert "Sorry, you have to type a new different password." in data

    @staticmethod
    def test_change_password_empty_field(client,
                                       get_credentials_3,
                                       get_existing_competition_and_club_4):
        """
        Test that the 406 status code and an error message are returned in case of changing
        password with at least one empty field.
        Args:
            client (FlaskClient): A Flask client
            get_credentials_3 (dict): The credentials
            get_existing_competition_and_club_4 (dict): The competition and club
        """
        client.post('/showSummary', data=get_credentials_3)

        passwords = {
            "password": "tp4_Tmn40",
            "confirm_password": "",
        }

        client_response = client.post(f'/changePassword/{get_existing_competition_and_club_4["club"]}',
                                      data=passwords)

        data = client_response.data.decode('utf-8')

        assert client_response.status_code == 200
        assert "Empty field(s)" in data
        assert "Sorry, please fill all fields." in data
