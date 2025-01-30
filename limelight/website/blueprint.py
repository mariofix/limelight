from flask import Blueprint, Response, render_template
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
    # pypi
    if pypi := get_new_data(queue_type=1):
        add_queue(project=pypi, project_type=1)

    if git := get_new_data(queue_type=2):
        add_queue(project=git, project_type=2)

    if downloads := get_new_data(queue_type=4):
        add_queue(project=downloads, project_type=4)


@blueprint.before_request
def find_old_pypi():
    # pypi
    if old_pypi := get_old_data(days=7, queue_type=1):
        add_queue(project=old_pypi, project_type=1)


@blueprint.before_request
def find_old_git():
    # git
    if old_git := get_old_data(days=7, queue_type=2):
        add_queue(project=old_git, project_type=2)


@blueprint.before_request
def find_old_dloads():
    # downloads
    if old_dload := get_old_data(days=7, queue_type=4):
        add_queue(project=old_dload, project_type=4)


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


@blueprint.get("/project/<slug>")
def get_project(slug):
    project = db.session.execute(db.select(Project).where(Project.slug == slug)).first()
    project = full_update_project_metadata(project=project[0])
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


@blueprint.route("/robots.txt", methods=["GET"])
def robots():
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
