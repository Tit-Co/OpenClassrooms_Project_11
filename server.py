import os

from flask import Flask, render_template, request, redirect, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'something_special'

app.config["CLUBS_JSON"] = os.environ.get("CLUBS_JSON")
app.config["COMPETITIONS_JSON"] = os.environ.get("COMPETITIONS_JSON")

CLUB_POINTS = 15

import utils

utils.clubs = utils.load_clubs()
utils.competitions = utils.load_competitions()


@app.route('/')
def index():
    """
    Route to home page
    Returns:
        The template for home page
    """
    return render_template(template_name_or_list='index.html')


@app.route('/signUp')
def sign_up():
    """
    Route to sign up page
    Returns:
        The template for sign up page
    """
    return render_template(template_name_or_list='sign_up.html')


@app.route('/profile/<club>', methods=['GET'])
def profile(club):
    """
    Route to club profile page
    Args:
        club (str): The club name

    Returns:
        The template for club profile page. The template may display a message to the user.
    """
    if "club" in session and session['club'] == club:
        the_club = next((c for c in utils.clubs if c['name'] == club), None)

        if the_club is None:
            flash(message="Sorry, that club was not found.")
            return render_template(template_name_or_list="index.html", error="Club not found"), 404

        return render_template(template_name_or_list='profile.html', club=the_club)

    flash(message="Sorry, you are not allow to see that profile.")
    return render_template(template_name_or_list='index.html', error="Not allow"), 403


@app.route('/profile', methods=['POST'])
def profile_post():
    """
    Route for signing up.
    Returns:
        The template to profile page if correctly signed up or sign up page otherwise.
    """
    club_name = request.form['name']
    club_email = request.form['email']
    club_password = request.form['password']
    club_password_confirmation = request.form['confirm_password']

    try:
        utils.validate_profile_fields(club_name, club_email, club_password, club_password_confirmation)

    except utils.ValidationError as e:
        flash(message=e.message)
        return redirect(location=url_for('sign_up'))

    try:
        utils.validate_email_format(club_email)

    except utils.ValidationError as e:
        flash(message=e.message)
        return redirect(location=url_for('sign_up'))

    existing_club = next((c for c in utils.clubs if c['email'] == club_email or c['name'] == club_name), None)
    if existing_club is None:
        if club_password != club_password_confirmation:
            flash(message='Sorry, passwords do not match')
            return redirect(location=url_for('sign_up'))

        hashed_password = generate_password_hash(club_password)
        utils.add_club(name=club_name,
                       email=club_email,
                       password=hashed_password,
                       points=str(CLUB_POINTS))

        the_club = next((c for c in utils.clubs if c['email'] == club_email), None)

        if the_club is None:
            flash(message="Sorry, something went wrong. Please try again.")
            return render_template(template_name_or_list='sign_up.html')

        flash(message="Great! You have successfully signed up.")
        session['club'] = the_club['name']
        return render_template(template_name_or_list='profile.html', club=the_club)

    else:
        flash(message="Sorry, the club already exists.")
        return render_template(template_name_or_list='sign_up.html')


@app.route('/changePassword/<club>', methods=['GET', 'POST'])
def change_password(club):
    """
    Route to change password.
    Args:
        club (str): The club name

    Returns:
        The template for club profile page. The index template otherwise.
    """
    if "club" in session and session['club'] == club:
        if request.method == 'GET':
            the_club = next((c for c in utils.clubs if c['name'] == club), None)

            if the_club is None:
                flash(message="Sorry, that club was not found.")
                return render_template(template_name_or_list="index.html", error="Email not found"), 404

            return render_template(template_name_or_list='change_password.html', club=the_club)
        else:
            club_password = request.form['password']
            club_password_confirmation = request.form['confirm_password']

            the_club = next((c for c in utils.clubs if c['name'] == club), None)

            try:
                utils.validate_password(password=club_password,
                                        password2=club_password_confirmation,
                                        club=the_club)
            except utils.ValidationError as e:
                flash(e.message)
                return render_template(template_name_or_list='change_password.html',
                                       club=the_club,
                                       error=e.tag), 200

            the_club = utils.update_club_password(the_club, club_password)

            if the_club:
                flash(message="Great! You have successfully changed your password.")
                return render_template(template_name_or_list='profile.html', club=the_club)

            flash(message="Sorry, something went wrong. Please try again.")
            return render_template(template_name_or_list='index.html')

    flash(message="Sorry, you are not allow to do this action.")
    return render_template(template_name_or_list='index.html', error="Not allow"), 403


@app.route('/showSummary/<club>', methods=['GET'])
def show_summary(club):
    """
    Route to club summary page
    Args:
        club (str): The club name

    Returns:
        The welcome template if authorized. The index template otherwise.
    """
    if "club" in session and session['club'] == club:
        the_club = next((c for c in utils.clubs if c['name'] == club), None)

        return render_template(template_name_or_list='welcome.html',
                               club=the_club,
                               competitions=utils.competitions)

    flash(message="Sorry, you are not allow to do this action.")
    return render_template(template_name_or_list='index.html', error="Not allow"), 403


@app.route('/showSummary', methods=['POST'])
def show_summary_post():
    """
    Route to log in.
    Returns:
        The welcome template if success. The index template otherwise.
    """
    try:
        utils.validate_login_fields(request.form['email'], request.form['password'])
    except utils.ValidationError as e:
        flash(message=e.message)
        return render_template(template_name_or_list="index.html", error=e.tag), 404

    the_club = next((c for c in utils.clubs if c['email'] == request.form['email']), None)

    if the_club is None:
        flash(message="Sorry, that email was not found.")
        return render_template(template_name_or_list="index.html", error="Email not found"), 404

    if not check_password_hash(the_club['password'], request.form['password']):
        flash(message="Sorry, the password is incorrect.")
        return render_template(template_name_or_list="index.html", error="Incorrect password"), 403

    session["club"] = the_club["name"]

    flash("Great! You are successfully logged in.")
    return render_template(template_name_or_list='welcome.html',
                           club=the_club,
                           competitions=utils.competitions)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    """
    Route to book page
    Args:
        competition (str): The competition name
        club (str): The club name

    Returns:
        The booking template if success. The welcome template if error. The index template otherwise.
    """
    if "club" in session and session['club'] == club:
        found_club = [c for c in utils.clubs if c['name'] == club][0]
        found_competition = [c for c in utils.competitions if c['name'] == competition][0]

        try:
            utils.validate_competition(the_competition=found_competition)

        except utils.ValidationError as e:
            flash(message=e.message)

            the_club = next((a_club for a_club in utils.clubs if a_club['name'] == club), None)

            return render_template(template_name_or_list='welcome.html',
                                   club=the_club,
                                   competitions=utils.competitions,
                                   error=e.tag), 200

        if found_club and found_competition:
            return render_template(template_name_or_list='booking.html',
                                   club=found_club,
                                   competition=found_competition), 200
        else:
            flash(message="Sorry, something went wrong. Please try again.")
            return render_template(template_name_or_list='welcome.html',
                                   club=club,
                                   competitions=utils.competitions)

    flash(message="Sorry, you are not allow to do this action.")
    return render_template(template_name_or_list='index.html', error="Not allow"), 403


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    """
    Route to purchase places page
    Returns:
        The welcome template if success. The welcome template with error message otherwise.
    """
    competition = [c for c in utils.competitions if c['name'] == request.form['competition']][0]
    club = [c for c in utils.clubs if c['name'] == request.form['club']][0]

    places_required = int(request.form['places']) if request.form['places'] else 0

    try:
        utils.validate_places(places_required=places_required,
                              club=club,
                              the_competition=competition)

    except utils.ValidationError as e:
        flash(message=e.message)
        return render_template(template_name_or_list='welcome.html',
                               club=club,
                               competitions=utils.competitions,
                               error=e.tag), 200

    utils.update_club_booked_places(club=club,
                                    places=places_required,
                                    competition_name=competition["name"])

    utils.update_competition_available_places(the_competition=competition, places=places_required)

    flash(message=f"Great! Booking of {places_required} place(s) for "
                  f"{competition['name']} competition complete!")

    return render_template(template_name_or_list='welcome.html',
                           club=club,
                           competitions=utils.competitions)


@app.route('/pointsBoard')
def points_board():
    """
    Route to points board page
    Returns:
        The points board template.
    """
    clubs_for_board = []
    for club in utils.clubs:
        club_copy = club.copy()
        if utils.clubs.index(club) % 2 == 0:
            club_copy["color"] = "#cccccc"
        else:
            club_copy["color"] = "#aaaaaa"
        clubs_for_board.append(club_copy)

    club = session.get('club')

    return render_template(template_name_or_list='points_board.html',
                           clubs=clubs_for_board,
                           club=club)


@app.route('/logout')
def logout():
    """
    Route for logging out
    Returns:
        The index template.
    """
    flash(message="Great! You are successfully logged out.")
    if 'club' in session:
        session.pop('club')
    return redirect(location=url_for('index'))
