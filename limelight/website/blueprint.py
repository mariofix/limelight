from flask import Blueprint, redirect, render_template, request
from sqlalchemy.sql import func

from ..crud import get_star_info, new_star_from_web
from ..database import db
from ..models import Lineup, Star, StarQueue, Style

blueprint = Blueprint("website", __name__, url_prefix="/")


@blueprint.get("/")
def home():
    context_data = {
        "q_stars": db.session.query(Star).count(),
        "q_styles": db.session.query(Style).count(),
        "q_lineups": db.session.query(Lineup).count(),
        "q_queues": db.session.query(StarQueue).count(),
        "l_last_5": db.session.query(Star).order_by(Star.created_at.desc()).limit(5).all(),
        "l_random_5": db.session.query(Star).order_by(func.rand()).limit(5).all(),
        "l_all_styles": db.session.query(Style).all(),
    }

    return render_template("website/home.html", **context_data)


@blueprint.get("/robots.txt")
def robots_txt():
    return "# robots.txt\n\nUser-agent: *\n\n"


@blueprint.post("/star/")
def create_star():
    data = {
        "new-star-name": request.form["new-star-name"],
        "new-star-slug": request.form["new-star-slug"],
        "new-pypi-repo": request.form["new-pypi-repo"],
        "new-conda-repo": request.form["new-conda-repo"],
        "new-github-repo": request.form["new-github-repo"],
        "new-gitlab-repo": request.form["new-gitlab-repo"],
        "repos": request.form.getlist("repos"),
    }
    new_star = new_star_from_web(data)

    return redirect(f"/star/{new_star.slug}")


@blueprint.get("/stars/")
def list_stars():
    return render_template("website/home.html")


@blueprint.get("/star/<star_slug>")
def interview_star(star_slug: str):
    star = get_star_info(star_slug)
    print(f"{star=}")
    return render_template("website/home.html")


@blueprint.get("/styles/")
def list_styles():
    return render_template("website/home.html")
