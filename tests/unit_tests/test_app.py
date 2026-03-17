import pytest
import server

from werkzeug.security import check_password_hash
from flask import url_for


class TestUnitApp:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, get_clubs, get_competitions):
        mocker.patch('server.clubs', get_clubs)
        mocker.patch('server.competitions', get_competitions)
        mocker.patch('server.save_clubs')

    @staticmethod
    def test_index_status_code_ok(client):
        client_response = client.get('/')
        assert client_response.status_code == 200

    @staticmethod
    def test_index_return_welcome(client):
        client_response = client.get('/')
        data = client_response.data.decode('utf-8')

        assert "Welcome to the GUDLFT Registration Portal!" in data
        assert ('Please enter your secretary email and your password to continue '
                'or <a href="/signUp">sign up</a>') in data
        assert "Email:" in data
        assert "Password:" in data

    @staticmethod
    def test_index_mail_authentication_ok(get_credentials, client):
        client_response = client.post('/showSummary', data=get_credentials)
        assert client_response.status_code == 200

    @staticmethod
    def test_index_mail_authentication_returns_summary(client, get_credentials):
        client_response = client.post('/showSummary', data=get_credentials)
        data = client_response.data.decode('utf-8')

        assert "Welcome, kate@shelifts.co.uk" in data
        assert "Spring Festival" in data
        assert "Fall Classic" in data
        assert "Points available: 12" in data

    @staticmethod
    def test_index_mail_authentication_fail(client, get_unexisting_credentials):
        client_response = client.post('/showSummary', data=get_unexisting_credentials)
        data = client_response.data.decode('utf-8')
        assert client_response.status_code == 404
        assert "Sorry, that email was not found." in data

    @staticmethod
    def test_summary_logout_redirect_status_code_ok(client, get_credentials):
        client.post('/showSummary', data=get_credentials)
        logout_response = client.get('/logout')
        assert logout_response.status_code == 302

    @staticmethod
    def test_booking_status_code_ok(client,
                                    get_credentials,
                                    get_existing_competition_and_club):

        client.post('/showSummary', data=get_credentials)

        client_response = client.get(url_for(endpoint='book',
                                      competition=get_existing_competition_and_club['competition'],
                                      club=get_existing_competition_and_club['club']))

        assert client_response.status_code == 200

    @staticmethod
    def test_signup_status_code_ok(client):
        client_response = client.get('/signUp')
        assert client_response.status_code == 200

    @staticmethod
    def test_signup_returns_welcome(client):
        client_response = client.get('/signUp')
        data = client_response.data.decode('utf-8')
        assert "Welcome to the GUDLFT sign up page!" in data
        assert ("Club name:" in data)
        assert ("Email:" in data)
        assert ("Password:" in data)
        assert ("Confirm Password:" in data)

    @staticmethod
    def test_change_password_status_code_ok(client):
        with client.session_transaction() as session:
            session["club"] = "She Lifts"

        client_response = client.get('/changePassword/She Lifts')
        assert client_response.status_code == 200

    @staticmethod
    def test_update_password_ok(get_credentials):
        the_club = next((c for c in server.clubs if c['email'] == get_credentials["email"]), None)
        the_club = server.update_club_password(the_club, "tp5_Tmn50")

        assert check_password_hash(the_club['password'], "tp5_Tmn50")

    @staticmethod
    def test_update_password_fails(get_credentials):
        the_club = next((c for c in server.clubs if c['email'] == get_credentials["email"]), None)
        the_club = server.update_club_password(the_club, "tp5_Tmn50")

        assert not check_password_hash(the_club['password'], "tp6_Tmn60")

    @staticmethod
    def test_add_club_ok(get_new_club):
        server.add_club(name=get_new_club["name"],
                        email=get_new_club["email"],
                        password=get_new_club["password"],
                        points=get_new_club["points"])

        assert get_new_club in server.clubs

    @staticmethod
    def test_profile_ok(client):
        with client.session_transaction() as session:
            session["club"] = "She Lifts"

        client_response = client.get('/profile/She Lifts')
        assert client_response.status_code == 200

    @staticmethod
    def test_profile_without_authentication_fails(client):
        client_response = client.get('/profile/Simply Lift')
        assert client_response.status_code == 403

    @staticmethod
    def test_profile_returns_welcome(client):
        with client.session_transaction() as session:
            session["club"] = "She Lifts"

        client_response = client.get('/profile/She Lifts')
        data = client_response.data.decode('utf-8')
        assert "Welcome, kate@shelifts.co.uk" in data
        assert "Profile:" in data
        assert "Name : She Lifts" in data
        assert "Email : kate@shelifts.co.uk" in data
        assert "Points available: 12" in data

    @staticmethod
    def test_update_booked_places_ok(get_existing_competition_and_club_2):
        club_name = get_existing_competition_and_club_2['club']
        club = next((c for c in server.clubs if c['name'] == club_name), None)
        competition_name = get_existing_competition_and_club_2['competition']
        server.update_club_booked_places(club=club,
                                         places=5,
                                         competition_name=competition_name)

        assert club['booked_places'][competition_name] == str(5)

    @staticmethod
    def test_update_booked_places_fails(get_existing_competition_and_club_2):
        club_name = get_existing_competition_and_club_2['club']
        club = next((c for c in server.clubs if c['name'] == club_name), None)
        competition_name = get_existing_competition_and_club_2['competition']
        server.update_club_booked_places(club=club,
                                         places=5,
                                         competition_name=competition_name)

        assert not club['booked_places'][competition_name] == str(6)

    @staticmethod
    def test_update_competition_available_places(get_existing_competition_and_club):
        competition_name = get_existing_competition_and_club['competition']
        competition = next((c for c in server.competitions if c['name'] == competition_name), None)
        places_available = int(competition['number_of_places'])
        server.update_competition_available_places(competition=competition, places=5)

        assert competition['number_of_places'] == str(places_available - 5)

    @staticmethod
    def test_update_competition_available_places_fails(get_existing_competition_and_club):
        competition_name = get_existing_competition_and_club['competition']
        competition = next((c for c in server.competitions if c['name'] == competition_name), None)
        places_available = int(competition['number_of_places'])
        server.update_competition_available_places(competition=competition, places=5)

        assert not competition['number_of_places'] == str(places_available - 4)

    @staticmethod
    def test_points_board_status_code_ok(client):
        client_response = client.get('/pointsBoard')
        data = client_response.data.decode('utf-8')
        assert client_response.status_code == 200
        assert "Welcome to the GUDLFT clubs points board!" in data
        assert "⯈ Here is the board for all the clubs and their points." in data
