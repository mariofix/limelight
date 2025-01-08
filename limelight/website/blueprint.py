from flask import Blueprint, Response, render_template
from sqlalchemy import desc

from ..crud import process_queue
from ..database import db
from ..forms import NewProjectForm
from ..models import Project, Tag
from ..sitemap import sitemapper

blueprint = Blueprint("website", __name__)


@sitemapper.include(
    priority=1.0,
    changefreq="daily",
)
@blueprint.get("/")
def home():
    # We just want one on each request
    process_queue(limit=1)
    featured_tags = db.session.execute(db.select(Tag).where(Tag.feature_in_home).order_by(Tag.order_in_home)).all()
    projects = db.session.execute(db.select(Project).order_by(desc(Project.id)).limit(5)).all()
    releases = db.session.execute(db.select(Project).order_by(desc(Project.last_release_date)).limit(5)).all()
    return render_template(
        "website/landing.html",
        featured_tags=featured_tags,
        projects=projects,
        releases=releases,
    )


@sitemapper.include(
    priority=0.8,
    changefreq="yearly",
)
@blueprint.get("/help/")
def help():
    # We just want one on each request
    process_queue(limit=1)
    return render_template("website/help.html")


@sitemapper.include(
    priority=0.6,
    changefreq="weekly",
    url_variables={
        "project_type": ["framework", "extension", "module", "project"],
    },
)
@blueprint.get("/<any(framework,extension,module,project,fulllist):project_type>/")
def projects(project_type):
    if project_type == "fulllist":
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


@sitemapper.include(
    priority=0.6,
    changefreq="weekly",
    url_variables={
        "slug": ["auth", "database", "api", "forms", "security", "frontend", "developer-tools"],
    },
)
@blueprint.get("/category/<slug>")
def get_tag(slug):
    tag = db.session.execute(db.select(Tag).where(Tag.slug == slug)).first()

    return render_template("website/tag.html", tag=tag[0])


@sitemapper.include(
    priority=1.0,
    changefreq="monthly",
)
@blueprint.route("/new-project/", methods=["GET"])
def new_project():
    form = NewProjectForm()
    return render_template("website/new_project.html", form=form)


@blueprint.get("/sitemap.xml")
def full_sitemap():
    return sitemapper.generate()


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


@blueprint.get("tyn4pbqky6nwdz36cm33m343uga1pqv7.txt")
def index_now():
    return "tyn4pbqky6nwdz36cm33m343uga1pqv7"
