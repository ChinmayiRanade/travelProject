from flask import Flask, jsonify, render_template, request
from cli import check_db_for_destination, get_attractions, save_plan
from prompt import get_itinerary
from database import SessionLocal, create_db_and_tables, Travel, Landmark
from sqlalchemy.orm import joinedload
from currencyapi import get_rate_for_city, get_city_currency

app = Flask(__name__)

# --- Exchange Rate API ---
@app.route("/api/exchange_rate/<destination>", methods=["GET"])
def api_get_exchange_rate(destination):
    """
    Get exchange rate for a given destination.
    """
    try:
        currency = get_city_currency(destination)

        if currency == "Unknown":
            return jsonify({
                "destination": destination,
                "currency": "USD",
                "rate": "USD is base currency",
                "note": "Currency information not available"
            }), 200

        if currency == "USD":
            return jsonify({
                "destination": destination,
                "currency": "USD",
                "rate": "USD is base currency"
            }), 200

        exchange_rate = get_rate_for_city(destination)

        return jsonify({
            "destination": destination,
            "currency": currency,
            "rate": exchange_rate
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"Failed to get exchange rate: {str(e)}"
        }), 500

# --- Plan a new trip ---
@app.route("/api/plan_new_trip", methods=["POST"])
def api_plan_new_trip():
    data = request.get_json()

    # Validate input
    destination = data.get("destination")
    duration = data.get("duration")
    budget = data.get("budget")
    travelers = data.get("travelers")
    interests = data.get("interests", "sightseeing")

    if not destination or not duration or not budget:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        num_days = int(duration)
        if num_days <= 0:
            return jsonify({"error": "Number of days must be a positive number"}), 400
    except ValueError:
        return jsonify({"error": "Invalid number for days"}), 400

    try:
        budget = int(budget)
    except ValueError:
        return jsonify({"error": "Invalid number for budget"}), 400

    # Check if we already have data
    attractions = check_db_for_destination(destination)
    if not attractions:
        print(f"🔎 Fetching from Yelp for {destination}...")
        attractions = get_attractions(destination, num_days)

    if not attractions:
        return jsonify({
            "error": f"No attractions found for '{destination}'. Try another city."
        }), 404

    # Generate AI itinerary
    itinerary_text = get_itinerary(destination, num_days, interests, attractions, budget)

    if itinerary_text:
        save_plan(destination, attractions)
        return jsonify({
            "message": "Itinerary generated successfully!",
            "destination": destination,
            "itinerary": itinerary_text
        }), 200
    else:
        return jsonify({"error": "Could not generate an itinerary at this time."}), 500

# --- View single saved plan ---
@app.route("/api/view_plan/<int:plan_id>", methods=["GET"])
def api_view_saved_plan(plan_id):
    with SessionLocal() as db:
        plan = (
            db.query(Travel)
            .options(joinedload(Travel.landmarks))
            .filter(Travel.id == plan_id)
            .first()
        )

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
                    "url": lm.url
                }
                for lm in plan.landmarks
            ]
        }), 200

# --- View all saved plan summaries ---
@app.route("/api/view_all_plans", methods=["GET"])
def api_view_all_plans():
    with SessionLocal() as db:
        all_plans = db.query(Travel).order_by(Travel.id.desc()).all()

        if not all_plans:
            return jsonify({"message": "No travel plans have been saved yet."}), 200

        return jsonify([
            {
                "id": plan.id,
                "destination": plan.destination,
                "num_attractions": plan.num_places,
            }
            for plan in all_plans
        ]), 200

# --- Pages ---
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    create_db_and_tables()
    app.run(debug=True)
