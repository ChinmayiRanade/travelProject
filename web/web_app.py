import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
from cli import check_db_for_destination, get_attractions, save_plan
from prompt import get_itinerary
from currencyapi import get_rate_for_city, get_city_currency
from database import SessionLocal, create_db_and_tables, Travel, Landmark, User
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = "bonvoyage123"

create_db_and_tables()

# --- Exchange Rate API ---
@app.route("/api/exchange_rate/<destination>", methods=["GET"])
def api_get_exchange_rate(destination):
    try:
        currency = get_city_currency(destination)
        if currency == "Unknown":
            return jsonify({"destination": destination, "currency": "USD", "rate": "USD is base currency", "note": "Currency info not available"}), 200
        if currency == "USD":
            return jsonify({"destination": destination, "currency": "USD", "rate": "USD is base currency"}), 200
        rate = get_rate_for_city(destination)
        return jsonify({"destination": destination, "currency": currency, "rate": rate}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get exchange rate: {str(e)}"}), 500

# --- AI Trip Planning ---
@app.route("/generate_plan", methods=["POST"])
def generate_plan():
    destination = request.form.get("destination")
    duration = request.form.get("duration")
    budget = request.form.get("budget")
    interests = request.form.get("interest")  # match form name

    if not destination or not duration or not budget:
        flash("Please fill out all required fields.", "error")
        return redirect(url_for("dashboard"))

    try:
        num_days = int(duration)
        budget = int(budget)
    except ValueError:
        flash("Duration and budget must be numbers.", "error")
        return redirect(url_for("dashboard"))

    attractions = check_db_for_destination(destination)
    if not attractions:
        attractions = get_attractions(destination, num_days)
    if not attractions:
        flash(f"No attractions found for '{destination}'.", "error")
        return redirect(url_for("dashboard"))

    itinerary_text = get_itinerary(destination, num_days, interests, attractions, budget)
    if itinerary_text:
        save_plan(destination, attractions)
        return render_template("travel_results.html", destination=destination, itinerary=itinerary_text)
    
    flash("Itinerary could not be generated.", "error")
    return redirect(url_for("dashboard"))


@app.route("/api/plan_new_trip", methods=["POST"])
def api_plan_new_trip():
    data = request.get_json()
    destination = data.get("destination")
    duration = data.get("duration")
    budget = data.get("budget")
    interests = data.get("interests", "sightseeing")

    if not destination or not duration or not budget:
        return jsonify({"error": "Missing required fields"}), 400
    try:
        num_days = int(duration)
        if num_days <= 0:
            return jsonify({"error": "Days must be a positive number"}), 400
    except ValueError:
        return jsonify({"error": "Invalid number for days"}), 400
    try:
        budget = int(budget)
    except ValueError:
        return jsonify({"error": "Invalid number for budget"}), 400

    attractions = check_db_for_destination(destination)
    if not attractions:
        attractions = get_attractions(destination, num_days)
    if not attractions:
        return jsonify({"error": f"No attractions found for '{destination}'"}), 404

    itinerary_text = get_itinerary(destination, num_days, interests, attractions, budget)
    if itinerary_text:
        save_plan(destination, attractions)
        return jsonify({"message": "Itinerary generated!", "destination": destination, "itinerary": itinerary_text}), 200
    return jsonify({"error": "Could not generate itinerary"}), 500

# --- View saved plans ---
@app.route("/api/view_plan/<int:plan_id>", methods=["GET"])
def api_view_saved_plan(plan_id):
    with SessionLocal() as db:
        plan = db.query(Travel).options(joinedload(Travel.landmarks)).filter(Travel.id == plan_id).first()
        if not plan:
            return jsonify({"error": f"No travel plan found with ID: {plan_id}"}), 404
        return jsonify({
            "plan_id": plan.id,
            "destination": plan.destination,
            "num_attractions": plan.num_places,
            "attractions": [
                {
                    "name": lm.name,
                    "address": lm.address,
                    "rating": lm.rating,
                    "url": lm.url,
                    "image_url": lm.image_url
                }
                for lm in plan.landmarks
            ]
        }), 200

@app.route("/api/view_all_plans", methods=["GET"])
def api_view_all_plans():
    with SessionLocal() as db:
        all_plans = db.query(Travel).order_by(Travel.id.desc()).all()
        if not all_plans:
            return jsonify({"message": "No travel plans saved yet."}), 200
        return jsonify([
            {"id": plan.id, "destination": plan.destination, "num_attractions": plan.num_places}
            for plan in all_plans
        ]), 200

# --- Main Pages ---
@app.route("/")
def home():
    if "username" not in session:
        return redirect(url_for("login_page"))
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login_page"))
    return render_template("dashboard.html")

@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login_page"))

    db = SessionLocal()
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        return redirect(url_for("logout"))

    return render_template("profile.html", user=user)


@app.route("/update_profile", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return redirect(url_for("login_page"))

    db = SessionLocal()
    user = db.query(User).filter_by(id=session["user_id"]).first()
    
    if user:
        new_username = request.form.get("username")
        new_email = request.form.get("email")

        # Check if new email is already taken by another user
        if new_email and new_email != user.email:
            existing_user = db.query(User).filter(User.email == new_email, User.id != user.id).first()
            if existing_user:
                flash("Email already in use by another account.", "error")
                db.close()
                return redirect(url_for("profile"))

        # Proceed to update username and email
        try:
            if new_username:
                user.username = new_username
                session["username"] = new_username

            if new_email:
                user.email = new_email

            db.commit()
            flash("Profile updated successfully!", "success")
        except IntegrityError:
            db.rollback()
            flash("An error occurred while updating your profile.", "error")

    db.close()
    return redirect(url_for("profile"))

# --- Auth Pages ---
@app.route("/login_page", methods=["GET"])
def login_page():
    if "username" in session:
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route('/forgot_password', methods=["GET", "POST"])
def forgot_password():
    db = SessionLocal()
    step = "identify"  # default view is asking for username/email
    user = None
    error = None

    if request.method == "POST":
        if "identifier" in request.form:
            identifier = request.form.get("identifier")
            user = db.query(User).filter(
                (User.username == identifier) | (User.email == identifier)
            ).first()
            if user:
                session["reset_user_id"] = user.id
                step = "reset"
            else:
                error = "No user found with that username or email."

        elif "new_password" in request.form:
            user_id = session.get("reset_user_id")
            user = db.query(User).filter_by(id=user_id).first()
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")

            if not user:
                error = "Session expired. Please enter your username/email again."
                step = "identify"

            elif not new_password or not confirm_password:
                error = "Both password fields are required."
                step = "reset"

            elif new_password != confirm_password:
                error = "Passwords do not match."
                step = "reset"

            elif check_password_hash(user.hashed_password, new_password):
                error = "New password must be different from the current password."
                step = "reset"

            else:
                user.hashed_password = generate_password_hash(new_password)
                db.commit()
                session.pop("reset_user_id", None)
                flash("Password reset successful. Please login.", "success")
                return redirect(url_for("login"))



    return render_template("forgot_password.html", step=step, error=error)


# @app.route('/reset_password', methods=["GET", "POST"])
# def reset_password():
#     user_id = session.get("reset_user_id")
#     if not user_id:
#         return redirect(url_for("login_page"))

#     db = SessionLocal()
#     user = db.query(User).filter_by(id=user_id).first()

#     if request.method == "POST":
#         new_password = request.form.get("new_password")
#         if new_password:
#             user.hashed_password = generate_password_hash(new_password)
#             db.commit()
#             session.pop("reset_user_id", None)  # Clear reset session
#             return redirect(url_for("login_page"))
#         else:
#             return render_template("reset_password.html", error="Please enter a new password.")

#     return render_template("reset_password.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            username = request.form["username"]
            email = request.form["email"]
            password = generate_password_hash(request.form["password"])

            print(f"[DEBUG] Registering user: {username}, {email}")

            db = SessionLocal()

            # Check for duplicate username
            if db.query(User).filter_by(username=username).first():
                db.close()
                return render_template("login.html", register_error="Username already exists")

            # Check for duplicate email
            if db.query(User).filter_by(email=email).first():
                db.close()
                return render_template("login.html", register_error="Email already registered")

            # All good, create new user
            new_user = User(username=username, email=email, hashed_password=password)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            db.close()

            session["user_id"] = new_user.id
            session["username"] = username
            return redirect(url_for("home"))

        except Exception as e:
            import traceback
            print("🔥 Registration error:")
            traceback.print_exc()
            return "500 Internal Server Error", 500

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    db = SessionLocal()
    username = request.form["username"]
    password = request.form["password"]
    user = db.query(User).filter_by(username=username).first()
    if user and check_password_hash(user.hashed_password, password):
        session["username"] = user.username
        session["user_id"] = user.id
        flash("Welcome back!", "success")
        return redirect(url_for("home"))
    flash("Invalid username or password", "error")
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for("login_page"))

# --- Start App ---
if __name__ == "__main__":
    create_db_and_tables()
    app.run(debug=True)
