import pytest

from random import randint

from server import app, clubs

@pytest.fixture
def client():
    my_app = app
    with my_app.test_client() as client:
        yield client

def get_existing_mail():
    data = {"email": "kate@shelifts.co.uk"}
    return data

def get_existing_mail_2():
    data = {"email": "admin@irontemple.com"}
    return data

def get_unexisting_mail():
    data = {"email": "nicolas.marie@unexisting.com"}
    return data

def get_existing_competition_and_club():
    data = {"competition": "Spring Festival", "club": "She Lifts"}
    return data

def get_existing_competition_and_club_2():
    data = {"competition": "Spring Festival", "club": "Iron Temple"}
    return data

def get_consistent_purchasing_data():
    competition = "Spring Festival"
    club_name = "She Lifts"
    places_to_book = randint(1, 12)
    data = {"competition": competition, "club": club_name, "places": str(places_to_book)}

    return data

def get_inconsistent_purchasing_data():
    competition = "Spring Festival"
    club_name = "Iron Temple"
    club_points = 4
    places_to_book = randint(club_points+1, 12)
    data = {"competition": competition, "club": club_name, "places": str(places_to_book)}

    return data

def get_inconsistent_purchasing_data_over_12_places():
    competition = "Spring Festival"
    club_name = "She Lifts"
    places_to_book = 13
    data = {"competition": competition, "club": club_name, "places": str(places_to_book)}

    return data

def get_inconsistent_purchasing_data_with_negative_places():
    competition = "Spring Festival"
    club_name = "She Lifts"
    places_to_book = -2
    data = {"competition": competition, "club": club_name, "places": str(places_to_book)}

    return data
