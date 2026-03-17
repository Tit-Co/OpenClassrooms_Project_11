import json

from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash


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

CLUB_POINTS = 15

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

def add_club(name, email, password, points):
    clubs.append({"name": name, "email": email, "password": password, "points": points})
    save_clubs()

def update_club_password(club, password):
    hashed_password = generate_password_hash(password)
    club["password"] = hashed_password
    save_clubs()
    return club

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signUp')
def sign_up():
    return render_template('sign_up.html')

@app.route('/profile/<club>', methods=['GET'])
def profile(club):
    if "club" in session and session['club'] == club:
        the_club = next((c for c in clubs if c['name'] == club), None)

        if the_club is None:
            flash("Sorry, that club was not found.")
            return render_template(template_name_or_list="index.html", error="Club not found"), 404

        return render_template(template_name_or_list='profile.html', club=the_club)

    flash("Sorry, you are not allow to see that profile.")
    return render_template(template_name_or_list='index.html', error="Not allow"), 403

@app.route('/profile', methods=['POST'])
def profile_post():
    club_name = request.form['name']
    club_email = request.form['email']
    club_password = request.form['password']
    club_password_confirmation = request.form['confirm_password']

    club_exists = next((c for c in clubs if c['email'] == club_email or c['name'] == club_name), None)
    if club_exists is None:
        if club_password != club_password_confirmation:
            flash('Sorry, passwords do not match')
            return redirect(url_for('sign_up'))

        hashed_password = generate_password_hash(club_password)
        add_club(club_name, club_email, hashed_password, str(CLUB_POINTS))

        the_club = next((c for c in clubs if c['email'] == club_email), None)

        if the_club is None:
            flash("Sorry, something went wrong. Please try again.")
            return render_template(template_name_or_list='sign_up.html')

        flash("Great! You have successfully signed up.")
        return render_template(template_name_or_list='profile.html', club=the_club)

    else:
        flash("Sorry, the club already exists.")
        return render_template(template_name_or_list='sign_up.html')

@app.route('/changePassword/<club>', methods=['GET', 'POST'])
def change_password(club):
    if "club" in session and session['club'] == club:
        if request.method == 'GET':
            the_club = next((c for c in clubs if c['name'] == club), None)

            if the_club is None:
                flash("Sorry, that club was not found.")
                return render_template(template_name_or_list="index.html", error="Email not found"), 404

            return render_template(template_name_or_list='change_password.html', club=the_club)
        else:
            club_password = request.form['password']
            club_password_confirmation = request.form['confirm_password']

            if club_password != club_password_confirmation:
                flash('Sorry, passwords do not match')
                return redirect(url_for('change_password'))

            the_club = next((c for c in clubs if c['name'] == club), None)

            if check_password_hash(the_club['password'], club_password):
                flash('Sorry, you have to type a new different password.')
                return render_template(template_name_or_list='change_password.html', club=the_club)

            the_club = update_club_password(the_club, club_password)

            if the_club:
                flash("Great! You have successfully changed your password.")
                return render_template(template_name_or_list='profile.html', club=the_club)

            flash("Sorry, something went wrong. Please try again.")
            return render_template(template_name_or_list='index.html')

    flash("Sorry, you are not allow to do this action.")
    return render_template(template_name_or_list='index.html', error="Not allow"), 403


@app.route('/showSummary/<club>', methods=['GET'])
def show_summary(club):
    if "club" in session and session['club'] == club:
        the_club = next((c for c in clubs if c['name'] == club), None)
        return render_template(template_name_or_list='welcome.html',
                               club=the_club,
                               competitions=competitions)

    flash("Sorry, you are not allow to do this action.")
    return render_template(template_name_or_list='index.html', error="Not allow"), 403

@app.route('/showSummary', methods=['POST'])
def show_summary_post():
    the_club = next((c for c in clubs if c['email'] == request.form['email']), None)

    if the_club is None:
        flash("Sorry, that email was not found.")
        return render_template(template_name_or_list="index.html", error="Email not found"), 404

    if not check_password_hash(the_club['password'], request.form['password']):
        flash("Sorry, the password is incorrect.")
        return render_template(template_name_or_list="index.html",)

    session["club"] = the_club["name"]

    return render_template(template_name_or_list='welcome.html',
                           club=the_club,
                           competitions=competitions)

@app.route('/book/<competition>/<club>')
def book(competition, club):
    if "club" in session and session['club'] == club:
        found_club = [c for c in clubs if c['name'] == club][0]
        found_competition = [c for c in competitions if c['name'] == competition][0]

        now = datetime.now()

        competition_date = datetime.strptime(found_competition['date'], '%Y-%m-%d %H:%M:%S')

        error_message = ""
        error_tag = ""

        the_competition = next((a_competition for a_competition in competitions
                                if a_competition['name'] == competition), None)
        competition_places = int(the_competition['number_of_places'])

        if now > competition_date:
            error_message = "Sorry, this competition is outdated. Booking not possible."
            error_tag = "Outdated"

        elif competition_places == 0:
            error_message = "Sorry, this competition is sold out. Booking not possible."
            error_tag = "Sold out"

        if error_message and error_tag:
            flash(error_message)

            the_club = next((a_club for a_club in clubs if a_club['name'] == club), None)

            return render_template(template_name_or_list='welcome.html',
                                   club=the_club,
                                   competitions=competitions,
                                   error=error_tag), 403

        if found_club and found_competition:
            return render_template(template_name_or_list='booking.html',
                                   club=found_club,
                                   competition=found_competition)
        else:
            flash("Sorry, something went wrong. Please try again.")
            return render_template(template_name_or_list='welcome.html',
                                   club=club,
                                   competitions=competitions)

    flash("Sorry, you are not allow to do this action.")
    return render_template(template_name_or_list='index.html', error="Not allow"), 403

@app.route('/purchasePlaces', methods=['POST'])
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
@app.route('/pointsBoard')
def points_board():
    clubs_for_board=[]
    for club in clubs:
        if clubs.index(club) %2 == 0:
            club["color"] = "#cccccc"
        else:
            club["color"] = "#aaaaaa"
        clubs_for_board.append(club)

    return render_template(template_name_or_list='points_board.html', clubs=clubs_for_board)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))