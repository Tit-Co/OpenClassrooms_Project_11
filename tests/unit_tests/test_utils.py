import pytest
import utils
import exceptions

from werkzeug.security import check_password_hash


class TestUnitUtils:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, get_clubs, get_competitions):
        mocker.patch('utils.clubs', get_clubs)
        mocker.patch('utils.competitions', get_competitions)
        mocker.patch('utils.save_clubs')
        mocker.patch('utils.save_competitions')

    @staticmethod
    def test_update_password_ok(get_credentials):
        """
        Test that the password is updated correctly.
        Args:
            get_credentials (dict): The credentials
        """
        the_club = next((c for c in utils.clubs if c['email'] == get_credentials["email"]), None)
        the_club = utils.update_club_password(the_club, "tp5_Tmn50")

        assert check_password_hash(the_club['password'], "tp5_Tmn50")

    @staticmethod
    def test_update_password_fails(get_credentials):
        """
        Test that the password is updated wrongly.
        Args:
            get_credentials (dict): The credentials
        """
        the_club = next((c for c in utils.clubs if c['email'] == get_credentials["email"]), None)
        the_club = utils.update_club_password(the_club, "tp5_Tmn50")

        assert not check_password_hash(the_club['password'], "tp6_Tmn60")

    @staticmethod
    def test_add_club_ok(get_new_club):
        """
        Test that the club is added correctly.
        Args:
            get_new_club (dict): The new club
        """
        utils.add_club(name=get_new_club["name"],
                       email=get_new_club["email"],
                       password=get_new_club["password"],
                       points=get_new_club["points"])

        assert get_new_club in utils.clubs

    @staticmethod
    def test_update_booked_places_ok(get_existing_competition_and_club_2):
        """
        Test that the required places are booked correctly.
        Args:
            get_existing_competition_and_club_2 (dict): The competition and club
        """
        club_name = get_existing_competition_and_club_2['club']
        club = next((c for c in utils.clubs if c['name'] == club_name), None)
        competition_name = get_existing_competition_and_club_2['competition']
        utils.update_club_booked_places(club=club,
                                        places=5,
                                        competition_name=competition_name)

        assert club['booked_places'][competition_name] == str(5)

    @staticmethod
    def test_update_booked_places_fails(get_existing_competition_and_club_2):
        """
        Test that the required places are booked wrongly.
        Args:
            get_existing_competition_and_club_2 (dict): The competition and club
        """
        club_name = get_existing_competition_and_club_2['club']
        club = next((c for c in utils.clubs if c['name'] == club_name), None)
        competition_name = get_existing_competition_and_club_2['competition']
        utils.update_club_booked_places(club=club,
                                        places=5,
                                        competition_name=competition_name)

        assert not club['booked_places'][competition_name] == str(6)

    @staticmethod
    def test_update_competition_available_places(get_existing_competition_and_club):
        """
        Test that the competition available places are updated correctly.
        Args:
            get_existing_competition_and_club (dict): The competition and club
        """
        competition_name = get_existing_competition_and_club['competition']
        competition = next((c for c in utils.competitions if c['name'] == competition_name), None)
        places_available = int(competition['number_of_places'])
        utils.update_competition_available_places(the_competition=competition, places=5)

        assert competition['number_of_places'] == str(places_available - 5)

    @staticmethod
    def test_update_competition_available_places_fails(get_existing_competition_and_club):
        """
        Test that the competition available places are updated wrongly.
        Args:
            get_existing_competition_and_club (dict): The competition and club
        """
        competition_name = get_existing_competition_and_club['competition']
        competition = next((c for c in utils.competitions if c['name'] == competition_name), None)
        places_available = int(competition['number_of_places'])
        utils.update_competition_available_places(the_competition=competition, places=5)

        assert not competition['number_of_places'] == str(places_available - 4)

    @staticmethod
    def test_signup_form_filled_out_ok(get_details):
        """
        Test that the form is filled out correctly.
        Args:
            get_details (dict): The details
        """
        name = get_details['name']
        email = get_details['email']
        password = get_details['password']
        password2 = get_details['password2']

        response = utils.check_signup_all_fields_filled_out(name=name,
                                                            email=email,
                                                            password=password,
                                                            password2=password2)

        assert response

    @staticmethod
    def test_signup_form_filled_out_fails(get_wrong_details):
        """
        Test that the form is filled out wrongly.
        Args:
            get_wrong_details (dict): The details
        """
        name = get_wrong_details['name']
        email = get_wrong_details['email']
        password = get_wrong_details['password']
        password2 = get_wrong_details['password2']

        response = utils.check_signup_all_fields_filled_out(name=name,
                                                            email=email,
                                                            password=password,
                                                            password2=password2)

        assert not response

    @staticmethod
    def test_login_form_filled_out_ok(get_details):
        """
        Test that the form is filled out correctly.
        Args:
            get_details (dict): The details
        """
        name = get_details['name']
        password = get_details['password']

        response = utils.check_login_all_fields_filled_out(name=name,
                                                           password=password,)

        assert response

    @staticmethod
    def test_login_form_filled_out_fails(get_wrong_details):
        """
        Test that the form is filled out wrongly.
        Args:
            get_wrong_details (dict): The details
        """
        name = get_wrong_details['name']
        password = get_wrong_details['password']

        response = utils.check_login_all_fields_filled_out(name=name,
                                                           password=password)

        assert not response

    @staticmethod
    def test_validate_places_with_negative(client, get_existing_competition_and_club):
        """
        Test that checks places validation process with negative value.
        Args:
            client (FlaskClient): A Flask client
            get_existing_competition_and_club (dict): The competition and club
        """
        club = next(
            (c for c in utils.clubs if c['name'] == get_existing_competition_and_club["club"]), None)
        competition_name = next(
            (c for c in utils.competitions if c['name'] == get_existing_competition_and_club["competition"]), None)

        try:
            utils.validate_places(places_required=-2,
                                  club=club,
                                  the_competition=competition_name)
        except exceptions.ValidationError as e:
            assert e.message == "Sorry, you should type a positive number."
            assert e.tag == "Negative number"

    @staticmethod
    def test_validate_places_over_12(client, get_existing_competition_and_club):
        """
        Test that checks places validation process with more than 12 places.
        Args:
            client (FlaskClient): A Flask client
            get_existing_competition_and_club (dict): The competition and club
        """
        club = next(
            (c for c in utils.clubs if c['name'] == get_existing_competition_and_club["club"]), None)
        competition = next(
            (c for c in utils.competitions if c['name'] == get_existing_competition_and_club["competition"]), None)
        try:
            utils.validate_places(places_required=13,
                                  club=club,
                                  the_competition=competition)
        except exceptions.ValidationError as e:
            assert e.message == "Sorry, you are not allow to purchase more than 12 places for this competition."
            assert e.tag == "Over 12 places"

    @staticmethod
    def test_validate_places_requires_more(client, get_existing_competition_and_club_5):
        """
        Test that checks places validation process with more than the number of places available.
        Args:
            client (FlaskClient): A Flask client
            get_existing_competition_and_club_5 (dict): The competition and club
        """
        club = next(
            (c for c in utils.clubs if c['name'] == get_existing_competition_and_club_5["club"]), None)
        competition = next(
            (c for c in utils.competitions if c['name'] == get_existing_competition_and_club_5["competition"]), None)
        try:
            utils.validate_places(places_required=5,
                                  club=club,
                                  the_competition=competition)
        except exceptions.ValidationError as e:
            assert e.message == "Sorry, there are not enough places available for this competition."
            assert e.tag == "Not enough places"

    @staticmethod
    def test_validate_places_not_enough(client, get_existing_competition_and_club_6):
        """
        Test that checks places validation process with not enough places.
        Args:
            client (FlaskClient): A Flask client
            get_existing_competition_and_club_6 (dict): The competition and club
        """
        club = next(
            (c for c in utils.clubs if c['name'] == get_existing_competition_and_club_6["club"]), None)
        competition = next(
            (c for c in utils.competitions if c['name'] == get_existing_competition_and_club_6["competition"]), None)

        try:
            utils.validate_places(places_required=6,
                                  club=club,
                                  the_competition=competition)
        except exceptions.ValidationError as e:
            assert e.message == "Sorry, you do not have enough points to purchase."
            assert e.tag == "Not enough points"

    @staticmethod
    def test_validate_past_competition(client, get_existing_competition_and_club_3):
        """
        Test that checks that the competition validation process with an outdated competition.
        Args:
            client (FlaskClient): A Flask client
            get_existing_competition_and_club_3 (dict): The competition and club
        """
        competition = next(
            (c for c in utils.competitions if c['name'] == get_existing_competition_and_club_3["competition"]), None)

        try:
            utils.validate_competition(the_competition=competition)
        except exceptions.ValidationError as e:
            assert e.message == "Sorry, this competition is outdated. Booking not possible."
            assert e.tag == "Outdated"

    @staticmethod
    def test_validate_competition_sold_out(client, get_existing_competition_and_club_4):
        """
        Test that the competition validation process with a sold out competition.
        Args:
            client (FlaskClient): A Flask client
            get_existing_competition_and_club_4 (dict): The competition and club
        """
        competition = next(
            (c for c in utils.competitions if c['name'] == get_existing_competition_and_club_4["competition"]), None)

        try:
            utils.validate_competition(the_competition=competition)
        except exceptions.ValidationError as e:
            assert e.message == "Sorry, this competition is sold out. Booking not possible."
            assert e.tag == "Sold out"

    @staticmethod
    def test_validate_profile_fields_fails(client, get_wrong_details):
        try:
            utils.validate_profile_fields(get_wrong_details["name"],
                                          get_wrong_details["email"],
                                          get_wrong_details["password"],
                                          get_wrong_details["password2"])

        except exceptions.ValidationError as e:

            assert e.message == "Sorry, please fill all fields."
            assert e.tag == "Empty field(s)"

    @staticmethod
    def test_validate_login_fields_fails(client, get_wrong_details):
        try:
            utils.validate_login_fields(get_wrong_details["email"], get_wrong_details["password"])
        except exceptions.ValidationError as e:

            assert e.message == "Sorry, please fill all fields."
            assert e.tag == "Empty field(s)"

    @staticmethod
    def test_validate_email_format_ok(client, get_details):
        try:
            utils.validate_email_format(get_details["email"])
            assert True

        except exceptions.ValidationError as e:
            assert e.message == "Sorry, the e-mail address you entered has invalid format."
            assert e.tag == "Invalid email format"

    @staticmethod
    def test_validate_email_format_fails(client, get_wrong_details):
        try:
            utils.validate_email_format(get_wrong_details["email"])

        except exceptions.ValidationError as e:
            assert e.message == "Sorry, the e-mail address you entered has invalid format."
            assert e.tag == "Invalid email format"

    @staticmethod
    def test_copy_clubs_for_board():
        copy_clubs = utils.copy_clubs_for_board()

        assert len(copy_clubs) == len(utils.clubs)
        assert "color" in copy_clubs[0].keys()
