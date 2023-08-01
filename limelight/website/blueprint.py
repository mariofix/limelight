from flask import Blueprint, redirect, render_template, request
from sqlalchemy.sql import func

from ..crud import get_star_info, new_star_from_browse, new_star_from_web
from ..database import db
from ..models import Lineup, Star, StarQueue, Style
from ..tasks import send_email

blueprint = Blueprint("website", __name__, url_prefix="/")


@blueprint.get("/")
def home():
    context_data = {
        "l_last_5": db.session.query(Star).order_by(Star.created_at.desc()).limit(5).all(),
        "l_random_5": db.session.query(Star).order_by(func.rand()).limit(5).all(),
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
    context_data = {
        "l_last_5": db.session.query(Star).order_by(Star.created_at.desc()).limit(5).all(),
        "l_random_5": db.session.query(Star).order_by(func.rand()).limit(5).all(),
        "star": db.session.query(Star).filter(Star.slug == star_slug).first(),
    }

    return render_template("website/home.html", **context_data)


@blueprint.get("/styles/")
def list_styles():
    return render_template("website/home.html")


@blueprint.get("/browse_pypi")
def browse_pypi():
    import xmlrpc.client

    from rich import print

    client = xmlrpc.client.ServerProxy("https://pypi.org/pypi")
    packages = client.browse(["Framework :: Flask"])
    lista: list = []
    for package in packages:
        if package[0] in lista:
            continue
        lista.append(package[0])
        data = {
            "new-star-name": package[0],
            "new-star-slug": package[0],
            "new-pypi-repo": package[0],
            "repos": ["pypi"],
        }
        print(f"new_star_from_browse({data=})")
        new_star_from_browse(data)
        del data

    send_email.delay(
        f"{len(lista)} New Stars",
        "new_star",
        "bot@mariofix.com",
        ["mariohernandezc@gmail.com"],
        {},
        "mariofix@pm.me",
    )
