import sys
import random
import json
import tempfile

from locust import HttpUser, task, between


temp_clubs_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
temp_comps_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
json.dump({"clubs": []}, temp_clubs_file)
json.dump({"competitions": []}, temp_comps_file)
temp_clubs_file.close()
temp_comps_file.close()

PATH = r"D:\WORK\Formation\Openclassrooms\Python\OpenClassrooms_Project_11\02_Repository\OpenClassrooms_Project_11"

sys.path.insert(0, PATH)


import utils
import copy

utils.get_clubs_path = lambda: temp_clubs_file.name
utils.get_competitions_path = lambda: temp_comps_file.name

with open(utils.CLUBS_PATH) as f:
    real_clubs = json.load(f)["clubs"]

with open(utils.COMPETITIONS_PATH) as f:
    real_competitions = json.load(f)["competitions"]


class TestPerfApp(HttpUser):
    wait_time = between(1, 3)

    @staticmethod
    def get_clubs():
        return copy.deepcopy(real_clubs)

    @staticmethod
    def get_competitions():
        return copy.deepcopy(real_competitions)

    def on_start(self):
        self.clubs = copy.deepcopy(real_clubs)
        self.competitions = copy.deepcopy(real_competitions)

        utils.clubs = self.clubs
        utils.competitions = self.competitions

        passwords_table = {
            "Simply Lift": "tgl_Prn_C2",
            "Iron Temple": "tgl_Prn_C3",
            "Power Lift": "tgl_Prn_C4",
            "She Lifts": "tgl_Prn_C5",
            "Iron Titans": "tgl_Prn_C6",
            "Barbell Warriors": "tgl_Prn_C7",
            "Power Lifts Club": "tgl_Prn_C8",
            "Steel Strength": "tgl_Prn_C9",
            "The Weightroom": "tgl_Prn_C10",
            "Olympic Lifters": "tgl_Prn_C11",
            "Titanium Tribes": "tgl_Prn_C12",
            "Heavy Hitters": "tgl_Prn_C13",
        }

        self.club = random.choice(utils.clubs)
        self.club["points"] = 60

        self.client.post(
            "/showSummary",
            data={
                "email": self.club["email"],
                "password": passwords_table[self.club["name"]]
            }
        )

    @task(2)
    def index_competitions(self):
        self.client.get("/")

    @task(3)
    def book_places(self):
        competition = random.choice(utils.competitions)

        while competition.get("is_past"):
            competition = random.choice(utils.competitions)

        competition["number_of_places"] = 60

        self.client.post('/purchasePlaces', data={
            "competition": competition["name"],
            "club": self.club["name"],
            "places": "1"
        })

    @task(1)
    def logout(self):
        self.client.get('/logout')
