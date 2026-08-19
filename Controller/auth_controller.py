from flask import Blueprint, render_template, request

from Services.auth_service import AuthService


auth_bp = Blueprint("auth_bp", __name__)
auth_service = AuthService()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        result = auth_service.login(email, password)
        return render_template("login.html", result=result)
    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user_data = request.form.to_dict()
        result = auth_service.register(user_data)
        return render_template("register.html", result=result)
    return render_template("register.html")
