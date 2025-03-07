from flask import Blueprint, Response, redirect, render_template, url_for
from sqlalchemy import desc

from ..crud import add_queue, get_new_data, get_old_data, process_queue_item
from ..database import db
from ..forms import NewProjectForm
from ..models import Project, Tag
from ..sitemap import sitemapper
from ..utils import full_update_project_metadata

blueprint = Blueprint("website", __name__)


# Queue Manager
@blueprint.before_request
def find_new_projects():
    queue_types = {1: "pypi", 2: "git", 4: "downloads"}

    for queue_type, _name in queue_types.items():
        if data := get_new_data(queue_type=queue_type):
            add_queue(project=data, project_type=queue_type)


@blueprint.before_request
def find_old_projects():
    queue_types = {1: "pypi", 2: "git", 4: "downloads"}
    days = 7

    for queue_type, _name in queue_types.items():
        if old_data := get_old_data(days=days, queue_type=queue_type):
            add_queue(project=old_data, project_type=queue_type)


@blueprint.before_request
def queue_item():
    process_queue_item()


@sitemapper.include(
    priority=1.0,
    changefreq="daily",
)
@blueprint.get("/")
def home():
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


@sitemapper.include(
    priority=0.6,
    changefreq="weekly",
    url_variables={
        "slug": ["flask", "quart"],
    },
)
@blueprint.get("/about/<any(flask,quart):slug>/")
def get_project_info(slug):
    project = db.first_or_404(db.select(Project).where(Project.slug == slug))
    project = full_update_project_metadata(project=project)
    return render_template(f"website/{slug}_info.html", project=project)


@blueprint.get("/project/<slug>")
def get_project(slug):
    if slug in ["flask", "quart"]:
        return redirect(url_for("website.get_project_info", slug=slug), code=301)
    project = db.first_or_404(db.select(Project).where(Project.slug == slug))
    project = full_update_project_metadata(project=project)
    return render_template("website/project.html", project=project)


@sitemapper.include(
    priority=0.6,
    changefreq="weekly",
    url_variables={
        "slug": ["auth", "database", "api", "forms", "security", "frontend", "developer-tools"],
    },
)
@blueprint.get("/category/<slug>")
def get_tag(slug):
    tag = db.first_or_404(db.select(Tag).where(Tag.slug == slug))
    return render_template("website/tag.html", tag=tag)


@sitemapper.include(
    priority=1.0,
    changefreq="monthly",
)
@blueprint.route("/new-project/", methods=["GET"])
def new_project():
    form = NewProjectForm()
    return render_template("website/new_project.html", form=form)


@blueprint.route("/robots.txt", methods=["GET"])
def robok():
    robots = render_template("robots.txt")
    return Response(robots, mimetype="text/plain")


@blueprint.get("/sitemap.xml")
def full_sitemap():
    return sitemapper.generate()


@blueprint.get("/sitemap-projects.xml")
def project_sitemap():
    projects = db.session.execute(db.select(Project)).all()
    sitemap = render_template("sitemap.xml", projects=projects)
    return Response(sitemap, mimetype="application/xml")


@blueprint.get("tyn4pbqky6nwdz36cm33m343uga1pqv7.txt")
def index_now():
    return "tyn4pbqky6nwdz36cm33m343uga1pqv7"
