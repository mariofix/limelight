from flask import Blueprint, Response, render_template

from ..database import db
from ..forms import NewProjectForm
from ..models import Project, Tag

blueprint = Blueprint("website", __name__)


@blueprint.get("/")
def home():
    return render_template("website/landing.html")


@blueprint.get("/help/")
def help():
    return render_template("website/landing.html")


@blueprint.get("/<any(application,framework,library,module,project):project_type>/")
def projects(project_type):
    if project_type == "project":
        projects = db.session.execute(db.select(Project)).all()
    else:
        projects = db.session.execute(db.select(Project).where(Project.category == project_type)).all()

    return render_template(
        "website/project_list.html",
        project_type=project_type,
        projects=projects,
    )


@blueprint.get("/project/<slug>")
def get_project(slug):
    project = db.session.execute(db.select(Project).where(Project.slug == slug)).first()
    return render_template("website/project.html", project=project[0])


@blueprint.get("/category/<slug>")
def get_tag(slug):
    tag = db.session.execute(db.select(Tag).where(Tag.slug == slug)).first()

    return render_template("website/tag.html", tag=tag[0])


@blueprint.route("/new-project/", methods=["GET"])
def new_project():
    form = NewProjectForm()
    return render_template("website/new_project.html", form=form)


@blueprint.get("/sitemap-projects.xml")
def project_sitemap():
    projects = db.session.execute(db.select(Project)).all()
    sitemap: str = (
        '<?xml version="1.0" encoding="utf-8"?>\n\
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" \
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 \
http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">'
    )
    for project in projects:
        sitemap = f"{sitemap}\n<url><loc>https://flaskpackages.pythonanywhere.com/project/{project[0].slug}</loc><priority>1.00</priority></url>"
    sitemap = f"{sitemap}\n</urlset>"
    return Response(sitemap, mimetype="application/xml")
