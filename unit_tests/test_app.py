from bs4 import BeautifulSoup
from flask import url_for

from unit_tests.conftest import (client, get_existing_mail, get_existing_mail_2,
                                 get_unexisting_mail, get_existing_competition_and_club,
                                 get_existing_competition_and_club_2,
                                 get_consistent_purchasing_data, get_inconsistent_purchasing_data,
                                 get_inconsistent_purchasing_data_over_12_places)

from server import clubs, competitions

def test_index_status_code_ok(client):
    response = client.get('/')
    assert response.status_code == 200

def test_index_return_welcome(client):
    response = client.get('/')
    data = response.data.decode('utf-8')

    assert "Welcome to the GUDLFT Registration Portal!" in data
    assert "Please enter your secretary email to continue:" in data
    assert "Email:" in data

def test_index_mail_authentication_ok(client):
    mail_data = get_existing_mail()
    response = client.post('/showSummary', data=mail_data)
    assert response.status_code == 200

def test_index_mail_authentication_returns_summary(client):
    mail_data = get_existing_mail()
    response = client.post('/showSummary', data=mail_data)
    data = response.data.decode('utf-8')

    assert "Welcome, kate@shelifts.co.uk" in data
    assert "Spring Festival" in data
    assert "Fall Classic" in data
    assert "Points available: 15" in data

def test_index_mail_authentication_fail(client):
    mail_data = get_unexisting_mail()
    response = client.post('/showSummary', data=mail_data)
    assert response.status_code == 404
    assert "Sorry, that email was not found." in response.data.decode('utf-8')

def test_summary_logout_redirect_status_code_ok(client):
    mail_data = get_existing_mail()
    client.post('/showSummary', data=mail_data)
    logout_response = client.get('/logout')
    assert logout_response.status_code == 302

def test_summary_logout_redirect_returns_welcome(client):
    mail_data = get_existing_mail()
    client.post('/showSummary', data=mail_data)

    logout_response = client.get('/logout')
    soup = BeautifulSoup(logout_response.data.decode(), features="html.parser")
    url = soup.find_all('a')[0].get('href')
    redirect_response = client.get(url, follow_redirects=True)

    assert redirect_response.status_code == 200
    data = redirect_response.data.decode('utf-8')

    assert "Welcome to the GUDLFT Registration Portal!" in data
    assert "Please enter your secretary email to continue:" in data
    assert "Email:" in data

def test_booking_status_code_ok(client):
    mail_data = get_existing_mail()
    client.post('/showSummary', data=mail_data)

    competition_and_club_data = get_existing_competition_and_club()
    response = client.get(url_for(endpoint='book',
                                  competition=competition_and_club_data['competition'],
                                  club=competition_and_club_data['club']))

    assert response.status_code == 200

def test_booking_return_festival_page_booking(client):
    mail_data = get_existing_mail()
    client.post('/showSummary', data=mail_data)

    competition_and_club_data = get_existing_competition_and_club()
    response = client.get(url_for(endpoint='book',
                                  competition=competition_and_club_data['competition'],
                                  club=competition_and_club_data['club']))
    data = response.data.decode('utf-8')
    assert "Spring Festival" in data
    assert "Places available: " in data
    assert "How many places?" in data

def test_good_purchasing_places_status_code_ok(client):
    mail_data = get_existing_mail()
    client.post('/showSummary', data=mail_data)
    competition_and_club_data = get_existing_competition_and_club()
    client.get(url_for(endpoint='book',
                       competition=competition_and_club_data['competition'],
                       club=competition_and_club_data['club']))

    purchasing_data = get_consistent_purchasing_data()

    response = client.post('/purchasePlaces', data=purchasing_data)

    assert response.status_code == 200

def test_good_purchasing_places_returns_summary_page(client):
    mail_data = get_existing_mail()
    client.post('/showSummary', data=mail_data)

    purchasing_data = get_consistent_purchasing_data()
    the_club = [club for club in clubs if club["name"] == purchasing_data['club']][0]
    the_competition =[competition for competition in competitions
                      if competition["name"] == purchasing_data['competition']][0]

    client.get(url_for(endpoint='book',
                       competition=the_competition['name'],
                       club=the_club['name']))

    club_points = the_club['points']
    competition_places = the_competition['numberOfPlaces']

    response = client.post('/purchasePlaces', data=purchasing_data)
    data = response.data.decode('utf-8')

    new_points = int(club_points) - int(purchasing_data['places'])
    new_competition_places = int(competition_places) - int(purchasing_data['places'])

    soup = BeautifulSoup(data, features="html.parser")
    all_li_str = [str(li) for li in soup.find_all('li')]
    the_club_name_utf8 = "%20".join(the_club['name'].split())
    the_competition_name_utf8 = "%20".join(the_competition['name'].split())
    li = (f'<li>\n'
          f'            {the_competition["name"]}<br/>\n'
          f'            Date: 2020-03-27 10:00:00\n'
          f'            Number of Places: {new_competition_places}\n            \n'
          f'            <a href="/book/{the_competition_name_utf8}/{the_club_name_utf8}">Book Places</a>\n'
          f'</li>')

    assert "Great-booking complete!" in data
    assert f"Welcome, {the_club["email"]} " in data
    assert li in all_li_str
    # assert f"Points available: {new_points}" in data

def test_purchasing_places_with_not_enough_points_status_code_error(client):
    mail_data = get_existing_mail_2()
    client.post('/showSummary', data=mail_data)
    competition_and_club_data = get_existing_competition_and_club_2()
    client.get(url_for(endpoint='book',
                       competition=competition_and_club_data['competition'],
                       club=competition_and_club_data['club']))

    purchasing_data = get_inconsistent_purchasing_data()

    response = client.post('/purchasePlaces', data=purchasing_data)

    assert response.status_code == 403

def test_purchasing_places_with_not_enough_points_returns_sorry(client):
    mail_data = get_existing_mail_2()
    client.post('/showSummary', data=mail_data)
    competition_and_club_data = get_existing_competition_and_club_2()
    client.get(url_for(endpoint='book',
                       competition=competition_and_club_data['competition'],
                       club=competition_and_club_data['club']))

    purchasing_data = get_inconsistent_purchasing_data()

    the_club = [club for club in clubs if club["name"] == purchasing_data['club']][0]
    club_points = the_club['points']

    response = client.post('/purchasePlaces', data=purchasing_data)
    data = response.data.decode('utf-8')

    assert "Sorry, you do not have enough points to purchase." in data
    assert f"Points available: {club_points}" in data

def test_purchasing_places_with_over_12_places_status_code_error(client):
    mail_data = get_existing_mail()
    client.post('/showSummary', data=mail_data)
    competition_and_club_data = get_existing_competition_and_club()
    client.get(url_for(endpoint='book',
                       competition=competition_and_club_data['competition'],
                       club=competition_and_club_data['club']))

    purchasing_data = get_inconsistent_purchasing_data_over_12_places()

    response = client.post('/purchasePlaces', data=purchasing_data)

    assert response.status_code == 403

def test_purchasing_places_with_over_12_places_returns_sorry(client):
    mail_data = get_existing_mail()
    client.post('/showSummary', data=mail_data)
    competition_and_club_data = get_existing_competition_and_club()
    client.get(url_for(endpoint='book',
                       competition=competition_and_club_data['competition'],
                       club=competition_and_club_data['club']))

    purchasing_data = get_inconsistent_purchasing_data_over_12_places()
    the_club = [club for club in clubs if club["name"] == purchasing_data['club']][0]
    club_points = the_club['points']

    response = client.post('/purchasePlaces', data=purchasing_data)
    data = response.data.decode('utf-8')

    assert "Sorry, you are not allow to purchase more than 12 places." in data
    assert f"Points available: {club_points}" in data
