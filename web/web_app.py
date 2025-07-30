import sys
import os
from functools import wraps


# Ensure imports work when running from different entry points
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError


# Import helpers (now user-aware)
from cli import check_db_for_destination, get_attractions, save_plan
from prompt import get_itinerary
from currencyapi import get_rate_for_city, get_city_currency
from database import SessionLocal, create_db_and_tables, Travel, Landmark, User


app = Flask(__name__)
app.secret_key = "bonvoyage123"  # consider using an environment variable in production


create_db_and_tables()


# ---------------------------
# Decorators / helpers
# ---------------------------


def login_required(json=False):
   """Require session login for routes."""
   def decorator(fn):
       @wraps(fn)
       def wrapper(*args, **kwargs):
           if "username" not in session or "user_id" not in session:
               if json or request.path.startswith("/api/"):
                   return jsonify({"error": "Unauthorized"}), 401
               return redirect(url_for("login_page"))
           return fn(*args, **kwargs)
       return wrapper
   return decorator


# ---------------------------
# Exchange Rate API
# ---------------------------


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


# ---------------------------
# AI Trip Planning
# ---------------------------


@app.route("/generate_plan", methods=["POST"])
@login_required()
def generate_plan():
   user_id = session["user_id"]


   destination = request.form.get("destination")
   duration = request.form.get("duration")
   budget = request.form.get("budget")
   interests = request.form.get("interest")


   if not destination or not duration or not budget:
       flash("Please fill out all required fields.", "error")
       return redirect(url_for("dashboard"))


   try:
       num_days = int(duration)
       budget_val = int(budget)
   except ValueError:
       flash("Duration and budget must be numbers.", "error")
       return redirect(url_for("dashboard"))


   # Only use THIS user's cached attractions for the destination
   attractions = check_db_for_destination(destination, user_id=user_id)
   if not attractions:
       attractions = get_attractions(destination, num_days)
   if not attractions:
       flash(f"No attractions found for '{destination}'.", "error")
       return redirect(url_for("dashboard"))


   itinerary_text = get_itinerary(destination, num_days, interests, attractions, budget_val)
   if itinerary_text:
       save_plan(destination, attractions, user_id=user_id)
       return render_template("travel_results.html", destination=destination, itinerary=itinerary_text)


   flash("Itinerary could not be generated.", "error")
   return redirect(url_for("dashboard"))




@app.route("/api/plan_new_trip", methods=["POST"])
@login_required(json=True)
def api_plan_new_trip():
   user_id = session["user_id"]
   data = request.get_json() or {}
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
       budget_val = int(budget)
   except ValueError:
       return jsonify({"error": "Invalid number for budget"}), 400


   attractions = check_db_for_destination(destination, user_id=user_id)
   if not attractions:
       attractions = get_attractions(destination, num_days)
   if not attractions:
       return jsonify({"error": f"No attractions found for '{destination}'"}), 404


   itinerary_text = get_itinerary(destination, num_days, interests, attractions, budget_val)
   if itinerary_text:
       save_plan(destination, attractions, user_id=user_id)
       return jsonify({"message": "Itinerary generated!", "destination": destination, "itinerary": itinerary_text}), 200


   return jsonify({"error": "Could not generate itinerary"}), 500


# ---------------------------
# View saved plans
# ---------------------------


@app.route("/api/view_plan/<int:plan_id>", methods=["GET"])
@login_required(json=True)
def api_view_saved_plan(plan_id):
   uid = session["user_id"]
   with SessionLocal() as db:
       plan = (
           db.query(Travel)
           .options(joinedload(Travel.landmarks))
           .filter(Travel.id == plan_id, Travel.user_id == uid)
           .first()
       )
       if not plan:
           return jsonify({"error": "Not found"}), 404


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
@login_required(json=True)
def api_view_all_plans():
   uid = session["user_id"]
   with SessionLocal() as db:
       my_plans = (
           db.query(Travel)
           .filter(Travel.user_id == uid)
           .order_by(Travel.id.desc())
           .all()
       )
       if not my_plans:
           return jsonify({"message": "No travel plans saved yet."}), 200


       return jsonify([
           {"id": plan.id, "destination": plan.destination, "num_attractions": plan.num_places}
           for plan in my_plans
       ]), 200


# ---------------------------
# Main Pages
# ---------------------------


@app.route("/")
@login_required()
def home():
   return render_template("home.html")


@app.route("/dashboard")
@login_required()
def dashboard():
   return render_template("dashboard.html")


@app.route("/profile")
@login_required()
def profile():
   user_id = session["user_id"]
   with SessionLocal() as db:
       user = db.query(User).filter_by(id=user_id).first()
       if not user:
           return redirect(url_for("logout"))
       return render_template("profile.html", user=user)




@app.route("/update_profile", methods=["POST"])
@login_required()
def update_profile():
   user_id = session["user_id"]
   new_username = request.form.get("username")
   new_email = request.form.get("email")


   with SessionLocal() as db:
       user = db.query(User).filter_by(id=user_id).first()
       if not user:
           return redirect(url_for("logout"))


       # Email uniqueness check (exclude current user)
       if new_email and new_email != user.email:
           existing_user = db.query(User).filter(User.email == new_email, User.id != user.id).first()
           if existing_user:
               flash("Email already in use by another account.", "error")
               return redirect(url_for("profile"))


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


   return redirect(url_for("profile"))


# ---------------------------
# Auth Pages
# ---------------------------


@app.route("/login_page", methods=["GET"])
def login_page():
   if "username" in session:
       return redirect(url_for("home"))
   return render_template("login.html")




@app.route('/forgot_password', methods=["GET", "POST"])
def forgot_password():
   step = "identify"  # default view is asking for username/email
   user = None
   error = None


   if request.method == "POST":
       with SessionLocal() as db:
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




@app.route("/register", methods=["GET", "POST"])
def register():
   if request.method == "POST":
       try:
           username = request.form["username"]
           email = request.form["email"]
           password_hash = generate_password_hash(request.form["password"])


           with SessionLocal() as db:
               # Check duplicates
               if db.query(User).filter_by(username=username).first():
                   return render_template("login.html", register_error="Username already exists")
               if db.query(User).filter_by(email=email).first():
                   return render_template("login.html", register_error="Email already registered")


               # Create user
               new_user = User(username=username, email=email, hashed_password=password_hash)
               db.add(new_user)
               db.flush()                 # Ensure PK is assigned
               user_id = new_user.id      # Capture before leaving the session
               db.commit()


           # Safe to use captured values now
           session["user_id"] = user_id
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


   username = request.form["username"]
   password = request.form["password"]


   with SessionLocal() as db:
       user = db.query(User).filter_by(username=username).first()
       if user and check_password_hash(user.hashed_password, password):
           session["username"] = user.username
           session["user_id"] = user.id
           flash("Welcome back!", "success")
           return redirect(url_for("home"))


   flash("Invalid username or password", "error")
   return redirect(url_for("login_page"))




@app.route("/logout")
def logout():
   session.clear()
   flash("You have been logged out", "success")
   return redirect(url_for("login_page"))


# ---------------------------
# Start App
# ---------------------------


if __name__ == "__main__":
   create_db_and_tables()
   app.run(debug=True)


