import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import server

def fake_save(*args, **kwargs):
    pass

server.save_clubs = fake_save
server.save_competitions = fake_save
server.update_club_booked_places = fake_save
server.update_competition_available_places = fake_save

import copy
from locust import HttpUser, task, between

real_clubs = server.clubs
real_competitions = server.competitions


class TestPerfApp(HttpUser):
    wait_time = between(1, 3)

    @staticmethod
    def get_clubs():
        return copy.deepcopy(real_clubs)

    @staticmethod
    def get_competitions():
        return copy.deepcopy(real_competitions)

    def on_start(self):
        self.clubs = self.get_clubs()
        self.competitions = self.get_competitions()

        server.clubs = self.clubs
        server.competitions = self.competitions

        club = [c for c in self.clubs if c["name"]=="Simply Lift"][0]
        self.client.post(
            "/showSummary",
            data={
                "email": club["email"],
                "password": "tgl_Prn_C2"
            }
        )

    @task(2)
    def index_competitions(self):
        self.client.get("/")

    @task(3)
    def book_places(self):
        club = [c for c in self.clubs if c["name"]=="Simply Lift"][0]
        competition = [c for c in self.competitions if c["name"] == "Spring Festival"][0]

        self.client.post('/purchasePlaces', data=dict(competition=competition["name"],
                                                      club=club["name"],
                                                      places="2"))

    @task(1)
    def logout(self):
        self.client.get('/logout')
