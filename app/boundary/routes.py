# app/boundary/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.exceptions import NotFound

from app.control.auth_controller import AuthController

# --- UserAdmin controllers (Accounts) ---
from app.control.useradmin_viewUserAccount_controller import UserAdminViewUserAccountController
from app.control.useradmin_searchUserAccount_controller import UserAdminSearchUserAccountController
from app.control.useradmin_createUserAccount_controller import UserAdminCreateUserAccountController
from app.control.useradmin_updateUserAccount_controller import UserAdminUpdateUserAccountController
from app.control.useradmin_suspendUserAccount_controller import UserAdminSuspendUserAccountController
from app.control.useradmin_activateUserAccount_controller import UserAdminActivateUserAccountController

# --- UserAdmin controllers (Profiles) ---
from app.control.useradmin_viewUserProfile_controller import UserAdminViewUserProfileController
from app.control.useradmin_createUserProfile_controller import UserAdminCreateUserProfileController
from app.control.useradmin_updateUserProfile_controller import UserAdminUpdateUserProfileController
from app.control.useradmin_suspendUserProfile_controller import UserAdminSuspendUserProfileController
from app.control.useradmin_activateUserProfile_controller import UserAdminActivateUserProfileController
from app.control.useradmin_searchUserProfile_controller import UserAdminSearchUserProfileController

# --- CSR controllers ---
from app.control.csr_searchRequest_controller import CsrSearchRequestController
from app.control.csr_viewRequest_controller import CsrViewRequestController
from app.control.csr_saveToShortlist_controller import CsrSaveToShortlistController
from app.control.csr_searchShortlist_controller import CsrSearchShortlistController
from app.control.csr_viewShortlist_controller import CsrViewShortlistController
from app.control.csr_searchHistory_controller import CsrSearchHistoryController
from app.control.csr_viewHistory_controller import CsrViewHistoryController
from app.control.csr_removeShortlist_controller import CsrRemoveShortlistController

# --- PIN controllers ---
from app.entity.request import Request
from app.control.pin_createRequest_controller import PinCreateRequestController
from app.control.pin_viewRequest_controller import PinViewRequestController
from app.control.pin_updateRequest_controller import PinUpdateRequestController
from app.control.pin_deleteRequest_controller import PinDeleteRequestController
from app.control.pin_searchRequest_controller import PinSearchRequestController
from app.control.pin_trackViews_controller import PinTrackViewsController
from app.control.pin_trackShortlists_controller import PinTrackShortlistsController

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

# ----------------------------------
# CSR ROUTES  (/csr/*)
# ----------------------------------

from flask_login import login_required, current_user
from flask import render_template
from app.entity.request import Request
from app.entity.shortlist import Shortlist
from app.entity.match_record import MatchRecord
from app import db

@boundary_bp.route("/csr/dashboard")
@login_required
def csr_dashboard():
    # Count all open requests
    open_requests_count = Request.query.filter_by(status="open").count()

    # Count requests shortlisted by this CSR
    shortlist_count = Shortlist.query.filter_by(csrRepID=current_user.userID).count()

    # Count matches completed by this CSR
    matches_count = MatchRecord.query.filter_by(csrRepID=current_user.userID).count()

    # Pass the results to the template
    return render_template(
        "csr/dashboard.html",
        open_requests_count=open_requests_count,
        shortlist_count=shortlist_count,
        matches_count=matches_count
    )


@boundary_bp.route("/csr/requests")
@login_required
def csr_requests():
    from app.control.csr_searchRequest_controller import CsrSearchRequestController
    from app.entity.category import Category

    # pagination params
    page = request.args.get("page", 1, type=int)
    per_page = 9

    # selected filter value
    selected_category = request.args.get("category")

    # fetch all active categories for dropdown
    categories = Category.query.filter_by(isActive=True).all()

    # get filtered results
    results = CsrSearchRequestController().searchRequest(selected_category)
    
    # paginate manually (since we already filtered)
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = results[start:end]

    class SimplePagination:
        def __init__(self, page, per_page, total):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1

    pagination = SimplePagination(page, per_page, total)

    return render_template(
        "csr/requests.html",
        requests=paginated,
        categories=categories,
        selected_category=selected_category,
        pagination=pagination
    )


@boundary_bp.route("/csr/requests/<int:request_id>")
@login_required
def csr_view_request(request_id):
    from app.control.csr_viewRequest_controller import CsrViewRequestController
    try:
        r = CsrViewRequestController().viewRequestDetails(request_id)
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("boundary.csr_requests"))

    return render_template("csr/view_request.html", request=r)

@boundary_bp.route("/csr/requests/<int:request_id>/shortlist", methods=["POST"])
@login_required
def csr_shortlist_add(request_id):
    ok = CsrSaveToShortlistController().saveToShortlist(request_id, current_user.userID)
    if ok:
        flash("Request added to shortlist.", "success")
    else:
        flash("This request is already in your shortlist.", "info")
    return redirect(url_for("boundary.csr_requests"))

@boundary_bp.route("/csr/shortlist")
@login_required
def csr_shortlist():
    from app.control.csr_searchShortlist_controller import CsrSearchShortlistController
    from app.entity.category import Category

    # Pagination setup
    page = request.args.get("page", 1, type=int)
    per_page = 9

    # Get selected category filter
    selected_category = request.args.get("category", type=int)

    # Fetch shortlist filtered by category
    results = CsrSearchShortlistController().searchShortlistByCategory(current_user.userID, selected_category)

    # Paginate manually
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_results = results[start:end]

    # Pagination helper class
    class SimplePagination:
        def __init__(self, page, per_page, total):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1

    pagination = SimplePagination(page, per_page, total)

    # All active categories for dropdown
    categories = Category.query.filter_by(isActive=True).all()

    # Extract associated requests for display
    requests = [s.request for s in paginated_results]

    return render_template(
        "csr/shortlist.html",
        requests=requests,
        pagination=pagination,
        categories=categories,
        selected_category=selected_category
    )


@boundary_bp.route("/csr/matches")
@login_required
def csr_matches():
    from app.control.csr_searchHistory_controller import CsrSearchHistoryController
    from app.entity.category import Category

    # Get filters
    page = request.args.get("page", 1, type=int)
    per_page = 10
    category_filter = request.args.get("category", type=int)
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    # Fetch all categories for dropdown
    categories = Category.query.filter_by(isActive=True).all()

    # Apply filters
    results = CsrSearchHistoryController().searchHistory(
        current_user.userID,
        category_filter,
        start_date,
        end_date
    )

    # Pagination
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = results[start:end]

    class SimplePagination:
        def __init__(self, page, per_page, total):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1

    pagination = SimplePagination(page, per_page, total)

    return render_template(
        "csr/matches.html",
        matches=paginated,
        categories=categories,
        selected_category=category_filter,
        start_date=start_date,
        end_date=end_date,
        pagination=pagination
    )




@boundary_bp.route("/csr/shortlist/<int:request_id>/remove", methods=["POST"])
@login_required
def csr_shortlist_remove(request_id):
    try:
        CsrRemoveShortlistController().removeFromShortlist(current_user.userID, request_id)
        flash("Removed from shortlist.", "warning")
    except ValueError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Unexpected error: {e}", "danger")
    return redirect(url_for("boundary.csr_shortlist"))

# ----------------------------------
# PIN ROUTES  (/pin/*)
# ----------------------------------

from sqlalchemy import or_

@boundary_bp.route("/pin/dashboard")
@login_required
def pin_dashboard():
    stats = {
        "total": Request.query.filter_by(pinID=current_user.userID).count(),
        "draft": Request.query.filter(
            Request.pinID == current_user.userID,
            Request.status.ilike("draft")
        ).count(),
        "open": Request.query.filter(
            Request.pinID == current_user.userID,
            Request.status.ilike("open")
        ).count(),
        "completed": Request.query.filter(
            Request.pinID == current_user.userID,
            Request.status.ilike("completed")
        ).count(),
    }

    matches_count = stats["completed"]

    return render_template(
        "pin/dashboard.html",
        stats=stats,
        matches_count=matches_count
    )

@boundary_bp.route("/pin/requests")
@login_required
def pin_requests():
    from app.control.pin_searchRequest_controller import PinSearchRequestController
    from app.entity.category import Category

    # --- pagination ---
    page = request.args.get("page", 1, type=int)
    per_page = 9

    # --- search keyword ---
    search_query = request.args.get("search", "").strip()

    # --- run controller query ---
    controller = PinSearchRequestController()
    all_requests = controller.searchRequests(current_user.userID, keyword=search_query)

    # --- paginate manually ---
    total = len(all_requests)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = all_requests[start:end]

    # --- simple pagination helper ---
    class SimplePagination:
        def __init__(self, page, per_page, total):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1

    pagination = SimplePagination(page, per_page, total)

    return render_template(
        "pin/requests.html",
        requests=paginated,
        pagination=pagination,
        search_query=search_query,
    )

@boundary_bp.route("/pin/requests/<int:request_id>")
@login_required
def pin_view_request(request_id):
    from app.control.pin_viewRequest_controller import PinViewRequestController
    try:
        req = PinViewRequestController().viewRequestDetails(request_id)
    except Exception as e:
        flash(str(e), "danger")
        return redirect(url_for("boundary.pin_requests"))

    return render_template("pin/view_request.html", request=req)



@boundary_bp.route("/pin/requests/create", methods=["GET", "POST"])
@login_required
def pin_create_request():
    from app.entity.category import Category
    categories = Category.query.filter_by(isActive=True).all()

    if request.method == "POST":
        category_id = request.form.get("category_id")
        title = request.form.get("title")
        description = request.form.get("description")

        try:
            success = PinCreateRequestController().createRequest(
                userID=current_user.userID,
                categoryID=category_id,
                title=title,
                description=description
            )
            if success:
                flash("Request created successfully.", "success")
                return redirect(url_for("boundary.pin_requests"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("pin/create_request.html", categories=categories)


@boundary_bp.route("/pin/requests/<int:request_id>/edit", methods=["GET", "POST"])
@login_required
def pin_edit_request(request_id):
    from app.entity.request import Request
    from app.entity.category import Category
    from app.control.pin_updateRequest_controller import PinUpdateRequestController

    req = Request.query.get(request_id)
    if not req or req.pinID != current_user.userID:
        raise NotFound("Request not found or unauthorized.")

    # fetch active categories for dropdown
    categories = Category.query.filter_by(isActive=True).all()

    if request.method == "POST":
        # grab inputs
        title = request.form.get("title")
        description = request.form.get("description")
        status = request.form.get("status")
        category_id = request.form.get("category_id", type=int)

        # NOTE: we are NOT letting user pick newRequestID from the form,
        # so we pass None for that param in UML.
        try:
            PinUpdateRequestController().updateRequest(
                requestID=req.requestID,
                newRequestID=None,                     # not changing PK in UI
                userID=current_user.userID,            # auth
                categoryID=category_id,
                title=title,
                description=description,
                status=status
            )
            flash("Request updated.", "success")
            return redirect(url_for("boundary.pin_requests"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("pin/edit_request.html", req=req, categories=categories)


@boundary_bp.route("/pin/requests/<int:request_id>/delete", methods=["POST"])
@login_required
def pin_delete_request(request_id):
    from app.control.pin_deleteRequest_controller import PinDeleteRequestController
    try:
        PinDeleteRequestController().deleteRequest(request_id, current_user.userID)
        flash("Request deleted successfully.", "warning")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("boundary.pin_requests"))


@boundary_bp.route("/pin/match-records", methods=["GET"])
@login_required
def pin_match_records():
    from app.control.pin_searchMatchRecord_controller import PinSearchMatchRecordController

    # Get filters
    category_query = request.args.get("category", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 10

    # Controller call
    results = PinSearchMatchRecordController().searchMatchRecord(
        current_user.userID, category_query, start_date, end_date
    )

    # Manual pagination
    total = len(results)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_matches = results[start:end]

    class SimplePagination:
        def __init__(self, page, per_page, total):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1
            self.next_num = page + 1

    pagination = SimplePagination(page, per_page, total)

    return render_template(
        "pin/matches.html",
        matches=paginated_matches,
        pagination=pagination,
        category_query=category_query,
        start_date=start_date,
        end_date=end_date
    )


@boundary_bp.route("/pin/requests/<int:request_id>/view-counters")
@login_required
def pin_request_counters(request_id):
    views = PinTrackViewsController().trackViews(request_id)
    shorts = PinTrackShortlistsController().trackShortlists(request_id)
    flash(f"Views: {views} | Shortlisted: {shorts}", "info")
    return redirect(url_for("boundary.pin_requests"))
