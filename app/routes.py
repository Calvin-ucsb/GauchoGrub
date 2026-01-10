from flask import Blueprint, render_template, request

bp = Blueprint("main", __name__)

@bp.get("/")
def home():
    return render_template("index.html")

@bp.post("/submit")
def submit():
    # Get form data
    age = int(request.form.get("age", 0))
    weight = float(request.form.get("weight", 0))
    height = float(request.form.get("height", 0))
    activity = request.form.get("activityLevel")
    goal = request.form.get("goal")
    
    # BMR calculation (assuming gender-neutral for simplicity)
    bmr = 10 * weight + 6.25 * height - 5 * age + 5  # +5 for men, -161 for women if gender included

    # Activity multiplier
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very-active": 1.9
    }
    tdee = bmr * activity_multipliers.get(activity, 1.2)

    # Adjust for goal
    if goal == "lose-weight":
        tdee -= 500
    elif goal == "gain-weight":
        tdee += 500
    # maintain → leave unchanged

    tdee = round(tdee)

    return render_template("result.html", calories=tdee)