import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

def update_club_booked_places(club, places, competition_name):
    clubs.remove(club)

    club["points"] = str(int(club["points"]) - places)

    clubs.append(club)
    save_clubs()

def save_clubs():
    with open('clubs.json', 'w') as c:
        listOfClubs = {"clubs": clubs}
        json.dump(listOfClubs, c, indent=4)

def update_competition_available_places(competition, places):
    competitions.remove(competition)

    competition['numberOfPlaces'] = str(int(competition['numberOfPlaces']) - places)

    competitions.append(competition)
    save_competitions()

def save_competitions():
    with open('competitions.json', 'w') as comps:
        listOfCompetitions = {"competitions": competitions}
        json.dump(listOfCompetitions, comps, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():

    club = next((club for club in clubs if club['email'] == request.form['email']), None)

    if club is None:
        flash("Sorry, that email was not found.")
        return render_template(template_name_or_list="index.html", error="Email not found"), 404

    return render_template(template_name_or_list='welcome.html',
                           club=club,
                           competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template(template_name_or_list='booking.html',
                               club=foundClub,
                               competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template(template_name_or_list='welcome.html',
                               club=club,
                               competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    print(placesRequired)

    if placesRequired < 0:
        flash("Sorry, you should type a positive number.")
        return render_template(template_name_or_list='welcome.html',
                               club=club,
                               competitions=competitions,
                               error="Negative number"), 403

    elif placesRequired > 12:
        flash("Sorry, you are not allow to purchase more than 12 places for this competition.")
        return render_template(template_name_or_list='welcome.html',
                               club=club,
                               competitions=competitions,
                               error="Places max reached"), 403

    elif placesRequired > int(club['points']):
        flash("Sorry, you do not have enough points to purchase.")
        return render_template(template_name_or_list='welcome.html',
                               club=club,
                               competitions=competitions,
                               error="Points not enough"), 403

    update_club_booked_places(club=club,
                              places=placesRequired,
                              competition_name=competition["name"])

    update_competition_available_places(competition=competition, places=placesRequired)

    flash('Great-booking complete!')
    return render_template(template_name_or_list='welcome.html',
                           club=club,
                           competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))