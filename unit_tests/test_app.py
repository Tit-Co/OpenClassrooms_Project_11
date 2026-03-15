import pytest
import server

from bs4 import BeautifulSoup
from flask import url_for


class TestApp:

    @pytest.fixture(autouse=True)
    def setup(self, mocker, get_clubs, get_competitions):
        mocker.patch('server.clubs', get_clubs)
        mocker.patch('server.competitions', get_competitions)

        mocker.patch('server.save_clubs')
        mocker.patch('server.save_competitions')

    @staticmethod
    def test_index_status_code_ok(client):
        client_response = client.get('/')
        assert client_response.status_code == 200

    @staticmethod
    def test_index_return_welcome(client):
        client_response = client.get('/')
        data = client_response.data.decode('utf-8')

        assert "Welcome to the GUDLFT Registration Portal!" in data
        assert "Please enter your secretary email to continue:" in data
        assert "Email:" in data

    @staticmethod
    def test_index_mail_authentication_ok(get_existing_mail, mocker, client):
        client_response = client.post('/showSummary', data=get_existing_mail)
        assert client_response.status_code == 200

    @staticmethod
    def test_index_mail_authentication_returns_summary(client, get_existing_mail):
        client_response = client.post('/showSummary', data=get_existing_mail)
        data = client_response.data.decode('utf-8')

        assert "Welcome, kate@shelifts.co.uk" in data
        assert "Spring Festival" in data
        assert "Fall Classic" in data
        assert "Points available: 12" in data

    @staticmethod
    def test_index_mail_authentication_fail(client, get_unexisting_mail):
        client_response = client.post('/showSummary', data=get_unexisting_mail)
        data = client_response.data.decode('utf-8')
        assert client_response.status_code == 404
        assert "Sorry, that email was not found." in data

    @staticmethod
    def test_summary_logout_redirect_status_code_ok(client, get_existing_mail):
        client.post('/showSummary', data=get_existing_mail)
        logout_response = client.get('/logout')
        assert logout_response.status_code == 302

    @staticmethod
    def test_summary_logout_redirect_returns_welcome(client, get_existing_mail):
        client.post('/showSummary', data=get_existing_mail)

        logout_response = client.get('/logout')
        soup = BeautifulSoup(logout_response.data.decode(), features="html.parser")
        url = soup.find_all('a')[0].get('href')
        redirect_response = client.get(url, follow_redirects=True)

        assert redirect_response.status_code == 200
        data = redirect_response.data.decode('utf-8')

        assert "Welcome to the GUDLFT Registration Portal!" in data
        assert "Please enter your secretary email to continue:" in data
        assert "Email:" in data

    @staticmethod
    def test_booking_status_code_ok(client,
                                    get_existing_mail,
                                    get_existing_competition_and_club):

        client.post('/showSummary', data=get_existing_mail)

        client_response = client.get(url_for(endpoint='book',
                                      competition=get_existing_competition_and_club['competition'],
                                      club=get_existing_competition_and_club['club']))

        assert client_response.status_code == 200

    @staticmethod
    def test_booking_return_festival_page_booking(client,
                                                  get_existing_mail,
                                                  get_existing_competition_and_club):

        client.post('/showSummary', data=get_existing_mail)

        client_response = client.get(url_for(endpoint='book',
                                      competition=get_existing_competition_and_club['competition'],
                                      club=get_existing_competition_and_club['club']))
        data = client_response.data.decode('utf-8')
        assert "Spring Festival" in data
        assert "Places available: " in data
        assert "How many places?" in data

    @staticmethod
    def test_good_purchasing_places_status_code_ok(client,
                                                   get_existing_mail,
                                                   get_existing_competition_and_club,
                                                   get_consistent_purchasing_data):

        client.post('/showSummary', data=get_existing_mail)
        client.get(url_for(endpoint='book',
                           competition=get_existing_competition_and_club['competition'],
                           club=get_existing_competition_and_club['club']))

        client_response = client.post('/purchasePlaces', data=get_consistent_purchasing_data)

        assert client_response.status_code == 200

    @staticmethod
    def test_good_purchasing_places_returns_summary_page(client,
                                                         get_existing_mail,
                                                         get_consistent_purchasing_data):

        client.post('/showSummary', data=get_existing_mail)

        purchasing_data = get_consistent_purchasing_data
        the_club = [club for club in server.clubs if club["name"] == purchasing_data['club']][0]
        the_competition =[competition for competition in server.competitions
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
        the_club_name_utf8 = "%20".join(the_club['name'].split())
        the_competition_name_utf8 = "%20".join(the_competition['name'].split())
        li = (f'<li>\n'
              f'            {the_competition["name"]}<br/>\n'
              f'            Date: 2026-07-27 10:00:00\n'
              f'            Number of Places: {new_competition_places}\n            \n'
              f'            <a href="/book/{the_competition_name_utf8}/'
              f'{the_club_name_utf8}">Book Places</a>\n'
              f'</li>')

        assert (f"Great! Booking of {purchasing_data['places']} places for "
                f"{purchasing_data['competition']} competition complete!") in data
        assert f"Welcome, {the_club["email"]} " in data
        assert li in all_li_str
        assert f"Points available: {new_points}" in data

    @staticmethod
    def test_purchasing_places_not_enough_points_status_code_error(client,
                                                                   get_existing_mail_2,
                                                                   get_existing_competition_and_club_2,
                                                                   get_inconsistent_purchasing_data):

        client.post('/showSummary', data=get_existing_mail_2)
        client.get(url_for(endpoint='book',
                           competition=get_existing_competition_and_club_2['competition'],
                           club=get_existing_competition_and_club_2['club']))

        client_response = client.post('/purchasePlaces', data=get_inconsistent_purchasing_data)

        assert client_response.status_code == 403

    @staticmethod
    def test_purchasing_places_not_enough_points_returns_sorry(client,
                                                               get_existing_mail_2,
                                                               get_existing_competition_and_club_2,
                                                               get_inconsistent_purchasing_data):

        client.post('/showSummary', data=get_existing_mail_2)
        client.get(url_for(endpoint='book',
                           competition=get_existing_competition_and_club_2['competition'],
                           club=get_existing_competition_and_club_2['club']))

        the_club = [club for club in server.clubs
                    if club["name"] == get_existing_competition_and_club_2['club']][0]

        client_response = client.post('/purchasePlaces', data=get_inconsistent_purchasing_data)
        data = client_response.data.decode('utf-8')

        assert f"Welcome, {the_club["email"]} " in data
        assert "Sorry, you do not have enough points to purchase." in data
        assert f"Points available: {the_club['points']}" in data

    @staticmethod
    def test_purchasing_places_over_12_places_status_code_error(client,
                                                                get_existing_mail,
                                                                get_existing_competition_and_club,
                                                                purchasing_over_12_places):

        client.post('/showSummary', data=get_existing_mail)

        client.get(url_for(endpoint='book',
                           competition=get_existing_competition_and_club['competition'],
                           club=get_existing_competition_and_club['club']))

        client_response = client.post('/purchasePlaces', data=purchasing_over_12_places)

        assert client_response.status_code == 403

    @staticmethod
    def test_purchasing_places_over_12_places_returns_sorry(client,
                                                            get_existing_mail,
                                                            purchasing_over_12_places):

        client.post('/showSummary', data=get_existing_mail)

        purchasing_data = purchasing_over_12_places

        client.get(url_for(endpoint='book',
                           competition=purchasing_data['competition'],
                           club=purchasing_data['club']))

        the_club = [club for club in server.clubs if club["name"] == purchasing_data['club']][0]
        club_points = the_club['points']

        client_response = client.post('/purchasePlaces', data=purchasing_data)
        data = client_response.data.decode('utf-8')

        assert f"Welcome, {the_club["email"]} " in data
        assert "Sorry, you are not allow to purchase more than 12 places for this competition." in data
        assert f"Points available: {club_points}" in data

    @staticmethod
    def test_purchasing_places_over_12_cumulative_places_returns_sorry(client,
                                                                       get_existing_mail,
                                                                       purchasing_13_cumulative_places):

        client.post('/showSummary', data=get_existing_mail)

        purchasing_data = purchasing_13_cumulative_places

        client.get(url_for(endpoint='book',
                           competition=purchasing_data['competition'],
                           club=purchasing_data['club']))

        the_club = [club for club in server.clubs if club["name"] == purchasing_data['club']][0]
        club_points = the_club['points']

        client_response = client.post('/purchasePlaces', data=purchasing_data)
        data = client_response.data.decode('utf-8')

        assert f"Welcome, {the_club["email"]} " in data
        assert "Sorry, you are not allow to purchase more than 12 places for this competition." in data
        assert f"Points available: {club_points}" in data

    @staticmethod
    def test_purchasing_places_negative_number_status_code_error(client,
                                                                 get_existing_mail,
                                                                 purchasing_with_negative_places):

        client.post('/showSummary', data=get_existing_mail)

        purchasing_data = purchasing_with_negative_places

        client.get(url_for(endpoint='book',
                           competition=purchasing_data['competition'],
                           club=purchasing_data['club']))

        client_response = client.post('/purchasePlaces', data=purchasing_data)

        assert client_response.status_code == 403

    @staticmethod
    def test_purchasing_places_negative_number_returns_sorry(client,
                                                             get_existing_mail,
                                                             purchasing_with_negative_places):

        client.post('/showSummary', data=get_existing_mail)

        purchasing_data = purchasing_with_negative_places

        client.get(url_for(endpoint='book',
                           competition=purchasing_data['competition'],
                           club=purchasing_data['club']))

        the_club = [club for club in server.clubs if club["name"] == purchasing_data['club']][0]
        club_points = the_club['points']

        client_response = client.post('/purchasePlaces', data=purchasing_data)
        data = client_response.data.decode('utf-8')

        assert f"Welcome, {the_club["email"]} " in data
        assert "Sorry, you should type a positive number." in data
        assert f"Points available: {club_points}" in data

    @staticmethod
    def test_purchasing_places_past_competitions_status_code_error(client,
                                                                   get_existing_mail,
                                                                   get_existing_competition_and_club_3):

        client.post('/showSummary', data=get_existing_mail)

        client_response = client.get(url_for(endpoint='book',
                                      competition=get_existing_competition_and_club_3['competition'],
                                      club=get_existing_competition_and_club_3['club']))

        assert client_response.status_code == 403

    @staticmethod
    def test_purchasing_places_past_competitions_returns_sorry(client,
                                                               get_existing_mail,
                                                               get_existing_competition_and_club_3):

        client.post('/showSummary', data=get_existing_mail)

        client_response = client.get(url_for(endpoint='book',
                           competition=get_existing_competition_and_club_3['competition'],
                           club=get_existing_competition_and_club_3['club']))

        data = client_response.data.decode('utf-8')

        assert "Sorry, this competition is outdated. Booking not possible." in data

    @staticmethod
    def test_purchasing_places_over_available_status_code_error(client,
                                                                get_existing_mail,
                                                                purchasing_places_more_than_available):

        client.post('/showSummary', data=get_existing_mail)

        purchasing_data = purchasing_places_more_than_available

        client.get(url_for(endpoint='book',
                           competition=purchasing_data['competition'],
                           club=purchasing_data['club']))

        client_response = client.post('/purchasePlaces', data=purchasing_data)

        assert client_response.status_code == 403

    @staticmethod
    def test_purchasing_places_over_available_returns_sorry(client,
                                                            get_existing_mail,
                                                            purchasing_places_more_than_available):

        client.post('/showSummary', data=get_existing_mail)

        purchasing_data = purchasing_places_more_than_available

        client.get(url_for(endpoint='book',
                           competition=purchasing_data['competition'],
                           club=purchasing_data['club']))

        the_club = [club for club in server.clubs if club["name"] == purchasing_data['club']][0]
        club_points = the_club['points']

        client_response = client.post('/purchasePlaces', data=purchasing_data)
        data = client_response.data.decode('utf-8')

        assert f"Welcome, {the_club["email"]} " in data
        assert "Sorry, there are not enough places available for this competition." in data
        assert f"Points available: {club_points}" in data

    @staticmethod
    def test_purchasing_places_sold_out_status_code_error(client,
                                                          get_existing_mail,
                                                          get_existing_competition_and_club_4):

        client.post('/showSummary', data=get_existing_mail)

        client_response = client.get(url_for(endpoint='book',
                           competition=get_existing_competition_and_club_4['competition'],
                           club=get_existing_competition_and_club_4['club']))

        data = client_response.data.decode('utf-8')

        assert client_response.status_code == 403
        assert "Sorry, this competition is sold out. Booking not possible." in data
