from datetime import datetime
import json
from flask import Flask, render_template, request, redirect, flash, url_for


def load_clubs():
    with open('clubs.json') as c:
         list_of_clubs = json.load(c)['clubs']
         return list_of_clubs


def load_competitions():
    with open('competitions.json') as comps:
         list_of_competitions = json.load(comps)['competitions']
         return list_of_competitions

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = load_competitions()
clubs = load_clubs()

def update_club_booked_places(club, places, competition_name):
    clubs.remove(club)

    club.setdefault("booked_places", {})
    current = int(club["booked_places"].get(competition_name, 0))
    club["booked_places"][competition_name] = str(current + places)

    club["points"] = str(int(club["points"]) - places)

    clubs.append(club)
    save_clubs()

def save_clubs():
    with open('clubs.json', 'w') as c:
        list_of_clubs = {"clubs": clubs}
        json.dump(list_of_clubs, c, indent=4)

def update_competition_available_places(competition, places):
    competitions.remove(competition)

    competition['number_of_places'] = str(int(competition['number_of_places']) - places)

    competitions.append(competition)
    save_competitions()

def save_competitions():
    with open('competitions.json', 'w') as comps:
        list_of_competitions = {"competitions": competitions}
        json.dump(list_of_competitions, comps, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def show_summary():

    club = next((club for club in clubs if club['email'] == request.form['email']), None)

    if club is None:
        flash("Sorry, that email was not found.")
        return render_template(template_name_or_list="index.html", error="Email not found"), 404

    return render_template(template_name_or_list='welcome.html',
                           club=club,
                           competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    found_club = [c for c in clubs if c['name'] == club][0]
    found_competition = [c for c in competitions if c['name'] == competition][0]

    now = datetime.now()

    competition_date = datetime.strptime(found_competition['date'], '%Y-%m-%d %H:%M:%S')

    if now > competition_date:
        flash("Sorry, this competition is outdated. Booking not possible.")
        the_club = next((a_club for a_club in clubs if a_club['name'] == club), None)
        return render_template(template_name_or_list='welcome.html',
                               club=the_club,
                               competitions=competitions,
                               error = "Outdated"), 403

    elif found_club and found_competition:
        return render_template(template_name_or_list='booking.html',
                               club=found_club,
                               competition=found_competition)
    else:
        flash("Something went wrong-please try again")
        return render_template(template_name_or_list='welcome.html',
                               club=club,
                               competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchase_places():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    places_required = int(request.form['places'])

    cumulative_places = places_required + int(club["booked_places"][competition["name"]]) \
        if "booked_places" in club else places_required

    error_message = ""
    error_tag = ""

    if places_required < 0:
        error_message = "Sorry, you should type a positive number."
        error_tag = "Negative number"

    elif cumulative_places > 12:
        error_message = "Sorry, you are not allow to purchase more than 12 places for this competition."
        error_tag = "Over 12 places"

    elif places_required > int(competition['number_of_places']):
        error_message = "Sorry, there are not enough places available for this competition."
        error_tag = "Not enough places"

    elif places_required > int(club['points']):
        error_message = "Sorry, you do not have enough points to purchase."
        error_tag = "Not enough points"

    if error_message and error_tag:
        flash(error_message)
        return render_template(template_name_or_list='welcome.html',
                               club=club,
                               competitions=competitions,
                               error=error_tag), 403

    update_club_booked_places(club=club,
                              places=places_required,
                              competition_name=competition["name"])

    update_competition_available_places(competition=competition, places=places_required)

    flash(f"Great! Booking of {places_required} places for "
          f"{competition['name']} competition complete!")

    return render_template(template_name_or_list='welcome.html',
                           club=club,
                           competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))