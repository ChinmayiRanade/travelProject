from flask import Flask, jsonify, render_template
from flask import request, jsonify
from flask import Blueprint
from cli import check_db_for_destination, get_attractions, save_plan
from prompt import get_itinerary
from database import SessionLocal, create_db_and_tables, Travel, Landmark
from sqlalchemy.orm import joinedload

app = Flask(__name__)


@app.route("/api/plan_new_trip", methods=["POST"])
def api_plan_new_trip():
    data = request.get_json()

    # Validate input
    destination = data.get("destination")
    duration = data.get("duration")
    budget = data.get("budget")
    travelers = data.get("travelers")  # Optional, if you want to use it
    interests = data.get("interests", "sightseeing")  # Default interest

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

    # Check database for attractions
    attractions = check_db_for_destination(destination)

    if not attractions:
        print(f"🔎 Fetching from Yelp for {destination}...")
        attractions = get_attractions(destination, num_days)

    if not attractions:
        return (
            jsonify(
                {
                    "error": f"No attractions found for '{destination}'. Try another city."
                }
            ),
            404,
        )

    # Generate itinerary
    itinerary_text = get_itinerary(
        destination, num_days, interests, attractions, budget
    )

    if itinerary_text:
        save_plan(destination, attractions)  # Save regardless of source
        return (
            jsonify(
                {
                    "message": "Itinerary generated successfully!",
                    "destination": destination,
                    "itinerary": itinerary_text,
                }
            ),
            200,
        )
    else:
        return jsonify({"error": "Could not generate an itinerary at this time."}), 500


@app.route("/api/view_plan/<int:plan_id>", methods=["GET"])
def api_view_saved_plan(plan_id):
    """
    API endpoint to retrieve a saved travel plan by ID.
    """
    with SessionLocal() as db:
        plan = (
            db.query(Travel)
            .options(joinedload(Travel.landmarks))
            .filter(Travel.id == plan_id)
            .first()
        )

        if not plan:
            return jsonify({"error": f"No travel plan found with ID: {plan_id}"}), 404

        # Build response
        return (
            jsonify(
                {
                    "plan_id": plan.id,
                    "destination": plan.destination,
                    "num_attractions": plan.num_places,
                    "attractions": [
                        {
                            "name": landmark.name,
                            "address": landmark.address,
                            "rating": landmark.rating,
                            "url": landmark.url,
                        }
                        for landmark in plan.landmarks
                    ],
                }
            ),
            200,
        )


@app.route("/api/view_all_plans", methods=["GET"])
def api_view_all_plans():
    """
    API endpoint to retrieve a summary of all saved travel plans.
    """
    with SessionLocal() as db:
        all_plans = db.query(Travel).order_by(Travel.id.desc()).all()

        if not all_plans:
            return jsonify({"message": "No travel plans have been saved yet."}), 200

        plan_summaries = [
            {
                "id": plan.id,
                "destination": plan.destination,
                "num_attractions": plan.num_places,
            }
            for plan in all_plans
        ]

        return jsonify(plan_summaries), 200


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/dashboard")
def page():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)
