import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Simple configuration for a single SQLite database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'codefolio.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a-super-secret-key-you-should-change' # We will replace this on the server

db = SQLAlchemy(app)

# --- Database Models (No changes) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    projects = db.relationship('Project', backref='owner', lazy=True, cascade="all, delete-orphan")

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech_used = db.Column(db.String(200), nullable=False)
    github_link = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username already exists.", "warning")
            return redirect(url_for("register"))
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        flash("You need to be logged in to access this page.", "warning")
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        tech_used = request.form.get("tech_used")
        github_link = request.form.get("github_link")
        if title and description and tech_used and github_link:
            new_project = Project(title=title, description=description, tech_used=tech_used, github_link=github_link, user_id=user_id)
            db.session.add(new_project)
            db.session.commit()
            flash("Project added successfully!", "success")
        else:
            flash("All fields are required.", "warning")
        return redirect(url_for("dashboard"))

    projects = Project.query.filter_by(user_id=user_id).order_by(Project.id.desc()).all()
    return render_template("dashboard.html", projects=projects)

@app.route("/edit/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    if "user_id" not in session:
        flash("Please log in to edit projects.", "warning")
        return redirect(url_for("login"))
    project = Project.query.get_or_404(project_id)
    if project.user_id != session["user_id"]:
        abort(403)
    if request.method == "POST":
        project.title = request.form.get("title")
        project.description = request.form.get("description")
        project.tech_used = request.form.get("tech_used")
        project.github_link = request.form.get("github_link")
        db.session.commit()
        flash("Project updated successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("edit_project.html", project=project)

@app.route("/delete/<int:project_id>", methods=["POST"])
def delete_project(project_id):
    if "user_id" not in session:
        flash("Please log in to delete projects.", "warning")
        return redirect(url_for("login"))
    project = Project.query.get_or_404(project_id)
    if project.user_id != session["user_id"]:
        abort(403)
    db.session.delete(project)
    db.session.commit()
    flash("Project deleted successfully.", "success")
    return redirect(url_for("dashboard"))

@app.route("/portfolio/<username>")
def portfolio(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("portfolio.html", user=user, projects=user.projects)

@app.route("/search")
def search():
    query = request.args.get('q', '')
    users = []
    if query:
        search_term = f"%{query}%"
        users = User.query.filter(User.username.ilike(search_term)).all()
    return render_template("search_results.html", users=users, query=query)



@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)