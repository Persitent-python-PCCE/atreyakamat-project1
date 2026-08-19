from flask import Blueprint, render_template

home_bp = Blueprint("home_bp", __name__)


@home_bp.route("/")
def index():
    return render_template("index.html", title="SeatMeUp")


@home_bp.route("/health")
def health():
    return {"status": "ok", "project": "SeatMeUp"}
