from flask import Blueprint, render_template, request

bp = Blueprint("main", __name__)

@bp.get("/")
def home():
    return render_template("index.html")

@bp.post("/submit")
def submit():
    data = request.form.to_dict(flat=False)
    print(data)
    return {"status": "received", "data": data}
