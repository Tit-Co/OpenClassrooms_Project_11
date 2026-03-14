import pytest

from random import randint

from server import app

@pytest.fixture
def client():
    my_app = app
    with my_app.test_client() as client:
        yield client

@pytest.fixture
def get_clubs():
    the_clubs = [
    {
        "name":"Simply Lift",
        "email":"john@simplylift.co",
        "points":"13"
    },
    {
        "name":"Iron Temple",
        "email": "admin@irontemple.com",
        "points":"4"
    },
    {   "name":"She Lifts",
        "email": "kate@shelifts.co.uk",
        "points":"12",
        "booked_places": {
                            "Spring Festival": "7"
                        }
    },
    {
        "name": "Power Lift",
        "email": "admin@powerlift.com",
        "points": "5"
    }
    ]
    return the_clubs

@pytest.fixture
def get_competitions():
    the_competitions = [
        {
            "name": "Fall Classic",
            "date": "2020-10-22 13:30:00",
            "number_of_places": "13"
        },
        {
            "name": "Spring Festival",
            "date": "2026-07-27 10:00:00",
            "number_of_places": "25"
        },
        {
            "name": "Winter Power",
            "date": "2026-06-26 12:16:00",
            "number_of_places": "4"
        },
        {
            "name": "Summer Stronger",
            "date": "2026-05-30 18:23:40",
            "number_of_places": "0"
        }
    ]
    return the_competitions

@pytest.fixture
def get_existing_mail():
    data = {"email": "kate@shelifts.co.uk"}
    return data

@pytest.fixture
def get_existing_mail_2():
    data = {"email": "admin@irontemple.com"}
    return data

@pytest.fixture
def get_unexisting_mail():
    data = {"email": "nicolas.marie@unexisting.com"}
    return data

@pytest.fixture
def get_existing_competition_and_club():
    data = {"competition": "Spring Festival", "club": "She Lifts"}
    return data

@pytest.fixture
def get_existing_competition_and_club_2():
    data = {"competition": "Spring Festival", "club": "Iron Temple"}
    return data

@pytest.fixture
def get_existing_competition_and_club_3():
    data = {"competition": "Fall Classic", "club": "Iron Temple"}
    return data

@pytest.fixture
def get_existing_competition_and_club_4():
    data = {"competition": "Summer Stronger", "club": "Power Lift"}
    return data

@pytest.fixture
def get_consistent_purchasing_data():
    competition = "Spring Festival"
    club_name = "She Lifts"
    places_to_book = randint(1, 5)
    data = {"competition": competition, "club": club_name, "places": str(places_to_book)}

    return data

@pytest.fixture
def get_inconsistent_purchasing_data():
    competition = "Spring Festival"
    club_name = "Iron Temple"
    club_points = 4
    places_to_book = randint(club_points+1, 12)
    data = {"competition": competition, "club": club_name, "places": str(places_to_book)}

    return data

@pytest.fixture
def purchasing_over_12_places():
    competition = "Spring Festival"
    club_name = "She Lifts"
    places_to_book = 13
    data = {"competition": competition, "club": club_name, "places": str(places_to_book)}

    return data

@pytest.fixture
def purchasing_13_cumulative_places():
    competition = "Spring Festival"
    club_name = "She Lifts"
    places_to_book = 6
    data = {"competition": competition, "club": club_name, "places": str(places_to_book)}

    return data

@pytest.fixture
def purchasing_with_negative_places():
    competition = "Spring Festival"
    club_name = "She Lifts"
    places_to_book = -2
    data = {"competition": competition, "club": club_name, "places": str(places_to_book)}

    return data

@pytest.fixture
def purchasing_places_more_than_available():
    competition = "Winter Power"
    club_name = "Power Lift"
    places_to_book = 5
    data = {"competition": competition, "club": club_name, "places": str(places_to_book)}

    return data
