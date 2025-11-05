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

from app.entity.user_account import UserAccount
from app.entity.user_profile import UserProfile
from app import db

#!!!! --- ADMIN GUARD (simple) ---
def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if getattr(current_user, "role", None) != "admin":
            flash("Admin access required.", "warning")
            return redirect(url_for("boundary.index"))
        return fn(*args, **kwargs)
    return wrapper
#!!!! --- ADMIN GUARD (simple) DELETE THIS FUNCTION!!!--- 

@boundary_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    # Calculate statistics for dashboard
    total_users = UserAccount.query.count()
    active_users = UserAccount.query.filter_by(isActive=True).count()
    suspended_users = UserAccount.query.filter_by(isActive=False).count()
    total_profiles = UserProfile.query.count()

    # Pass data to template
    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        active_users=active_users,
        suspended_users=suspended_users,
        total_profiles=total_profiles
    )

# Users list + search !!! need to fix
@boundary_bp.route("/admin/users")
@admin_required
def admin_users():
    from app.entity.user_account import UserAccount
    search_query = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 10

    q = UserAccount.query
    #!!! fix this loop
    if search:
        q = q.filter(UserAccount.name.ilike(f"%{search}%"))
    #!!! class need action
    pagination = q.order_by(UserAccount.userID.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template("admin/users.html",
                           users=pagination.items,
                           pagination=pagination,
                           search_query=search)

# Create user (GET form + POST submit) !!!! need to fix
@boundary_bp.route("/admin/users/create", methods=["GET", "POST"])
@login_required
def admin_create_user():
    from app.entity.user_profile import UserProfile
    profiles = UserProfile.query.filter_by(isActive=True).all()

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        # !!! inconsistant. fix this
        if not all([name, email, password]):
            flash("Name, email and password are required.", "warning")
            return render_template("admin/create_user.html")

        # minimal create (hash later)
        user = UserAccount(name=name, email=email, password=password, role=role, isActive=True)
        db.session.add(user)
        db.session.commit()
        flash("User account created.", "success")
        return redirect(url_for("boundary.admin_users"))
    return render_template("admin/create_user.html")
    # !!! inconsistant. fix this

# view user account detail
@boundary_bp.route("/admin/users/<int:user_id>")
@admin_required
# !!!!!! need error handling here
def admin_view_user(user_id):
    user = UserAccount.query.get_or_404(user_id)
    return render_template("admin/view_user.html", user=user)

# Update user account
@boundary_bp.route("/admin/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def admin_edit_user(user_id):
    from app.entity.user_profile import UserProfile
    from app.entity.user_account import UserAccount
    profiles = UserProfile.query.filter_by(isActive=True).all()
    user = UserAccount.query.get(user_id)
    
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("boundary.admin_users"))
        
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("new_password") or None
        # !!! need other data to match also
        try:
            ok = UserAdminUpdateUserAccountController().updateUserAccount(
                userID=user_id,
                name=name,
                email=email,
                password=password # !!! need other data to match also
            )
            if ok:
                flash("User updated successfully.", "success")
                return redirect(url_for("boundary.admin_users"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("admin/edit_user.html", user=user, profiles=profiles)

# Suspend user account
@boundary_bp.route("/admin/users/<int:user_id>/suspend", methods=["POST"])
@login_required
def admin_suspend_user(user_id):
    try:
        ok = UserAdminSuspendUserAccountController().suspendUserAccount(user_id)
        if ok:
            flash("User suspended successfully.", "success")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("boundary.admin_users"))


# Activate user account
@boundary_bp.route("/admin/users/<int:user_id>/activate", methods=["POST"])
@login_required
def admin_activate_user(user_id):
    try:
        ok = UserAdminActivateUserAccountController().activateUserAccount(user_id)
        if ok:
            flash("User reactivated successfully.", "success")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("boundary.admin_users"))

# Profiles list
@boundary_bp.route("/admin/profiles")
@login_required
def admin_profiles():
    page = request.args.get("page", 1, type=int)
    per_page = 10

    from app.entity.user_profile import UserProfile
    pagination = UserProfile.query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "admin/profiles.html",
        profiles=pagination.items,
        pagination=pagination
    )
# Search users by profile ID
@boundary_bp.route("/admin/search/users-by-profile", methods=["GET"])
@login_required
def admin_search_users_by_profile():
    from app.entity.user_profile import UserProfile
    profile_id = request.args.get("profile_id", type=int)
    # Prevent negative or zero ID
    if profile_id is not None and profile_id < 1:
        flash("Profile ID must be a positive number.", "warning")
        return redirect(url_for('boundary.admin_profiles'))
    page = request.args.get("page", 1, type=int)
    per_page = 10

    users = []
    profile = None
    if profile_id:
        try:
            profile = UserProfile.query.get(profile_id)
            if profile:
                users = UserAdminSearchUserProfileController().searchUserByProfile(profile_id)
            else:
                flash("Profile not found.", "warning")
        except Exception as e:
            flash(str(e), "danger")

    total = len(users)
    start = (page - 1) * per_page
    end = start + per_page
    pagination_users = users[start:end]

    class Pagination:
        def __init__(self, page, per_page, total, items):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.items = items
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1

    pagination = Pagination(page, per_page, total, pagination_users)
    
    # search second time
    return render_template(
        "admin/profiles.html",
        profiles=[profile],  # show only this one profile row
        pagination=None
    )



# Create profile
@boundary_bp.route("/admin/profiles/create", methods=["GET", "POST"])
@login_required
def admin_create_profile():
    if request.method == "POST":
        name = request.form.get("profile_name")
        desc = request.form.get("description")
        try:
            UserAdminCreateUserProfileController().createUserProfile(name, desc)
            flash("Profile created.", "success")
            return redirect(url_for("boundary.admin_profiles"))
        except Exception as e:
            flash(str(e), "danger")
    return render_template("admin/create_profile.html")

# View User Profile
@boundary_bp.route("/admin/profiles/<int:profile_id>")
@login_required
def admin_view_profile(profile_id):
    profile = UserAdminViewUserProfileController().viewUserProfile(profile_id)
    if not profile:
        flash("Profile not found.", "danger")
        return redirect(url_for("boundary.admin_profiles"))

    return render_template("admin/view_profile.html", profile=profile)


# Edit User profile
@boundary_bp.route("/admin/profiles/<int:profile_id>/edit", methods=["GET", "POST"])
@login_required
def admin_edit_profile(profile_id):
    profile = UserAdminViewUserProfileController().viewUserProfile(profile_id)
    if not profile:
        flash("Profile not found.", "danger")
        return redirect(url_for("boundary.admin_profiles"))

    if request.method == "POST":
        new_profile_id = request.form.get("new_profile_id") or None
        profile_name = request.form.get("profile_name")
        description = request.form.get("description")
        is_active = (request.form.get("is_active") == "on")

        try:
            # handle activation toggle via respective controller
            UserAdminUpdateUserProfileController().toggleActivation(profile_id, is_active)

            # handle UML-aligned profile update
            ok = UserAdminUpdateUserProfileController().updateUserProfile(
                profileID=profile_id,
                newProfileID=int(new_profile_id) if new_profile_id else None,
                profileName=profile_name,
                description=description
            )
            if ok:
                flash("Profile updated successfully.", "success")
                return redirect(url_for("boundary.admin_profiles"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("admin/edit_profile.html", profile=profile)

# Suspend User profile
@boundary_bp.route("/admin/profiles/<int:profile_id>/suspend")
@login_required
def admin_suspend_profile(profile_id):
    UserAdminSuspendUserProfileController().suspendUserProfile(profile_id)
    flash("Profile suspended.", "warning")
    return redirect(url_for("boundary.admin_profiles"))

# Activate User profile
@boundary_bp.route("/admin/profiles/<int:profile_id>/activate")
@login_required
def admin_activate_profile(profile_id):
    UserAdminActivateUserProfileController().activateUserProfile(profile_id)
    flash("Profile activated.", "success")
    return redirect(url_for("boundary.admin_profiles"))
