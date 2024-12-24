from flask import Blueprint, render_template

from ..database import db
from ..forms import NewProjectForm
from ..models import Project

blueprint = Blueprint("website", __name__)


@blueprint.get("/")
def home():
    return render_template("website/landing.html")


@blueprint.get("/help/")
def help():
    return render_template("website/landing.html")


@blueprint.get("/<any(applications,frameworks,libraries,modules,projects):project_type>/")
def projects(project_type):
    return render_template("website/project_list.html", project_type=project_type)


@blueprint.get("/projects/<slug>")
def get_project(slug):
    project = db.session.execute(db.select(Project).where(Project.slug == slug)).first()
    return render_template("website/project.html", project=project[0])


@blueprint.route("/new-project/", methods=["GET"])
def new_project():
    form = NewProjectForm()
    return render_template("website/new_project.html", form=form)
