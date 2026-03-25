import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ValidationError(Exception):
    def __init__(self, message, tag):
        self.message = message
        self.tag = tag
        super().__init__(message)


class NegativePlacesError(ValidationError):
    pass


class Over12PlacesError(ValidationError):
    pass


class NotEnoughPlacesError(ValidationError):
    pass


class NotEnoughPointsError(ValidationError):
    pass


class OutdatedCompetitionError(ValidationError):
    pass


class CompetitionNullPlacesError(ValidationError):
    pass


class PasswordEmptyFieldError(ValidationError):
    pass


class PasswordsNotMatchError(ValidationError):
    pass


class PasswordNotDifferentError(ValidationError):
    pass


def get_clubs_path() -> str:
    """
    Method that returns the path to the clubs json file
    Returns:
        The path to the clubs json file
    """
    path = os.environ.get("CLUBS_JSON")

    if not path:
        path = os.path.join(BASE_DIR, "clubs.json")

    return path

def get_competitions_path() -> str:
    """
    Method that returns the path to the competitions json file
    Returns:
        The path to the competitions json file
    """
    path = os.environ.get("COMPETITIONS_JSON")

    if not path:
        path = os.path.join(BASE_DIR, "competitions.json")

    return path

def load_clubs() -> list:
    """
    Method that loads the clubs json file
    Returns:
        The list of clubs
    """
    path = os.path.join(BASE_DIR, "clubs.json")
    with open(path) as c:
        return json.load(c)['clubs']

def load_competitions() -> list:
    """
    Method that loads the competitions json file
    Returns:
        The sorted list of competitions
    """
    path = os.path.join(BASE_DIR, "competitions.json")
    with open(path) as comps:
        list_of_competitions = json.load(comps)['competitions']
        return sorted(list_of_competitions, key=lambda c: c['date'])

competitions = []

clubs = []

def save_clubs() -> None:
    """
    Method that saves the clubs json file
    """
    path = get_clubs_path()
    with open(path, 'w') as f:
        list_of_clubs = {"clubs": clubs}
        json.dump(list_of_clubs, f, indent=4)

def save_competitions() -> None:
    """
    Method that saves the competitions json file
    """
    path = get_competitions_path()
    with open(path, 'w') as f:
        list_of_competitions = {"competitions": sorted(competitions, key=lambda c: c['date'])}
        json.dump(list_of_competitions, f, indent=4)

for competition in competitions:
    competition['is_past'] = datetime.strptime(competition['date'], "%Y-%m-%d %H:%M:%S") < datetime.now()

def update_club_booked_places(club: dict, places: int, competition_name: str) -> None:
    """
    Method that updates the club booked places based on the number of places
    Args:
        club (dict): The club dictionary
        places (int): The number of places
        competition_name (str): The name of the competition
    """
    clubs.remove(club)

    club.setdefault("booked_places", {})
    current = int(club["booked_places"].get(competition_name, 0))
    club["booked_places"][competition_name] = str(current + places)

    club["points"] = str(int(club["points"]) - places)

    clubs.append(club)
    save_clubs()

def update_competition_available_places(the_competition: dict, places: int) -> None:
    """
    Method that updates the competition available places based on the number of places
    Args:
        the_competition (dict): The competition dictionary
        places (int): The number of places
    """
    competitions.remove(the_competition)

    the_competition['number_of_places'] = str(int(the_competition['number_of_places']) - places)

    competitions.append(the_competition)

    save_competitions()

def add_club(name: str, email: str, password: str, points: str) -> None:
    """
    Method that adds a club to the clubs list
    Args:
        name (str): The name of the club
        email (str): The email of the club
        password (str): The password of the club
        points (str): The points of the club in string format
    """
    clubs.append({"name": name, "email": email, "password": password, "points": points})
    save_clubs()

def update_club_password(club: dict, password: str) -> dict:
    """
    Method that updates the club password based on the password
    Args:
        club (dict): The club dictionary
        password (str): The password of the club

    Returns:
        The updated club
    """
    hashed_password = generate_password_hash(password)
    club["password"] = hashed_password
    save_clubs()
    return club

def check_all_fields_filled_out(name: str, email: str, password: str, password2: str) -> bool:
    """
    Method that checks if all the fields are filled out
    Args:
        name (str): The name of the club
        email (str): The email of the club
        password (str): The password of the club
        password2 (str): The password of the club

    Returns:
        A boolean indicating if all the fields are filled out
    """
    if len(name) == 0 or len(email) == 0 or len(password) == 0 or len(password2) == 0:
        return False
    return True

def validate_places(places_required: int, club: dict, the_competition: dict) -> None:
    """
    Method that validates the places required
    Args:
        places_required (int): The number of places required
        club (dict): The club dictionary
        the_competition (dict): The competition dictionary

    Returns:
        None
    """
    booked_places = int(club.get("booked_places", {}).get(the_competition["name"], 0))

    cumulative_places = places_required + booked_places

    if places_required <= 0:
        raise NegativePlacesError(
            message = "Sorry, you should type a positive number.",
            tag = "Negative number"
        )

    if cumulative_places > 12:
        raise Over12PlacesError(
            message = "Sorry, you are not allow to purchase more than 12 places for this competition.",
            tag = "Over 12 places"
        )

    if places_required > int(the_competition['number_of_places']):
        raise NotEnoughPlacesError(
            message = "Sorry, there are not enough places available for this competition.",
            tag = "Not enough places"
        )

    if places_required > int(club['points']):
        raise NotEnoughPointsError(
            message = "Sorry, you do not have enough points to purchase.",
            tag = "Not enough points"
        )

def validate_competition(the_competition: dict) -> None:
    """
    Method that validates the competition
    Args:
        the_competition (dict): The competition dictionary

    Returns:
        None
    """
    now = datetime.now()

    competition_date = datetime.strptime(the_competition['date'], '%Y-%m-%d %H:%M:%S')

    competition_places = int(the_competition['number_of_places'])

    if now > competition_date:
        raise OutdatedCompetitionError(
            message = "Sorry, this competition is outdated. Booking not possible.",
            tag = "Outdated"
        )

    if competition_places == 0:
        raise CompetitionNullPlacesError(
            message = "Sorry, this competition is sold out. Booking not possible.",
            tag = "Sold out"
        )

def validate_password(password: str, password2: str, club: dict) -> None:
    """
    Method that validates the password
    Args:
        password (str): The password of the club.
        password2 (str): The password of the club.
        club (dict): The club dictionary.

    Returns:
        None
    """
    if len(password) == 0 or len(password2) == 0:
        raise PasswordEmptyFieldError(
            message = "Sorry, please fill all fields.",
            tag = "Empty field(s)"
        )

    if password != password2:
        raise PasswordsNotMatchError(
            message = "Sorry, passwords do not match.",
            tag = "Passwords not match"
        )

    if check_password_hash(club['password'], password):
        raise PasswordNotDifferentError(
            message = "Sorry, you have to type a new different password.",
            tag = "Identical password"
        )
