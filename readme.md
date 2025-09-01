# CodeFolio - A Flask Portfolio Web App

## Description

CodeFolio is a full-stack web application built with Flask that allows developers to create an account, log in, and manage a portfolio of their projects. Each user gets a public-facing portfolio page to showcase their work to the world.

This was built as a major project for the 100 Days of Code challenge.

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** SQLite
- **Frontend:** HTML, CSS, Jinja2
- **Password Hashing:** Werkzeug

## Local Setup

1.  Clone the repository:
    `git clone <your-repo-link>`
2.  Navigate into the project directory:
    `cd your-project-folder`
3.  Create and activate a virtual environment:
    `python -m venv venv`
    `source venv/bin/activate` (or `.\venv\Scripts\activate` on Windows)
4.  Install the dependencies:
    `pip install -r requirements.txt`
5.  Run the application:
    `python app.py`

The database will be created automatically on the first run. The app will be available at `http://127.0.0.1:5000`.