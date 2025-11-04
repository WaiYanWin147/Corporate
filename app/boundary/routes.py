# app/boundary/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound

from app.control.auth_controller import AuthController

boundary_bp = Blueprint("boundary", __name__)

# ----------------------------------
# HOME & AUTH
# ----------------------------------

@boundary_bp.route("/")
def index():
    # Public landing page (templates/index.html)
    return render_template("index.html")

@boundary_bp.route("/login", methods=["GET", "POST"])
def login():
    # GET renders login form; POST uses AuthController to log in & redirect by role
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        redirect_to, err = AuthController().login(email, password)
        if err:
            flash(err, "danger")
            return render_template("auth/login.html"), 401
        return redirect(redirect_to or "/")
    return render_template("auth/login.html")

@boundary_bp.route("/logout")
@login_required
def logout():
    AuthController().logout()
    return redirect(url_for("boundary.index"))

