from flask import Blueprint, render_template, request
from .db import db
from bson.objectid import ObjectId
from passlib.hash import bcrypt
from datetime import datetime, timezone

bp = Blueprint("main", __name__)

@bp.get("/")
def home():
    return render_template("index.html")

@bp.post("/signup")
def signup():
    data = request.get_json(force=True)
    email = data["email"].strip().lower()
    try:
        password = normalize_password(data["password"])
    except ValueError as e:
        return {"error": str(e)}, 400

    if db.users.find_one({"email": email}):
        return {"error": "Email already exists"}, 409

    user_doc = {
        "email": email,
        "name": data.get("name", ""),
        "password_hash": bcrypt.hash(password),
        "created_at": datetime.now(timezone.utc),
    }
    res = db.users.insert_one(user_doc)

    return {"user_id": str(res.inserted_id)}, 201

@bp.post("/login")
def login():
    data = request.get_json(force=True)
    email = data["email"].strip().lower()
    try:
        password = normalize_password(data["password"])
    except ValueError as e:
        return {"error": str(e)}, 400

    user = db.users.find_one({"email": email})
    if not user or not bcrypt.verify(password, user["password_hash"]):
        return {"error": "Invalid credentials"}, 401

    return {"user_id": str(user["_id"])}

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

@bp.get("/health")
def health():
    # quick DB ping
    db.command("ping")
    return {"ok": True}

@bp.post("/items")
def create_item():
    data = request.get_json(force=True)
    res = db.items.insert_one({"name": data["name"]})
    return {"id": str(res.inserted_id)}, 201

@bp.get("/items")
def list_items():
    items = list(db.items.find().limit(50))
    for it in items:
        it["_id"] = str(it["_id"])
    return {"items": items}

@bp.delete("/items/<item_id>")
def delete_item(item_id):
    res = db.items.delete_one({"_id": ObjectId(item_id)})
    return {"deleted": res.deleted_count}

def normalize_password(pw: str) -> str:
    pw = pw.strip()
    if len(pw.encode("utf-8")) > 72:
        raise ValueError("Password too long (max 72 bytes).")
    return pw
