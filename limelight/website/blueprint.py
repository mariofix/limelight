from flask import Blueprint, render_template, redirect, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


from . import utils
from ..database import db

blueprint = Blueprint("website", __name__)


@blueprint.get("/")
def home():
    return render_template("website/landing.html")


class NewProjectForm(FlaskForm):
    slug: str = StringField("slug", validators=[DataRequired()])


@blueprint.route("/new-project/", methods=["GET", "POST"])
def new_project():
    form = NewProjectForm()
    if form.validate_on_submit():
        return redirect(f"/project/{form.slug.data}")
    return render_template("website/new_project.html", form=form)


@blueprint.get("/project/<str>")
def get_project(project):
    return render_template("website/project.html", project)


@blueprint.get("/queue")
def get_queue():
    queue = utils.get_queue_items()
    return jsonify(queue)


@blueprint.put("/queue/<str>")
def update_queue(extension):

    return jsonify(extension)


# @blueprint.get("/login-modal/")
# def login_modal():
#     form = LoginForm()
#     return render_template("accounts/login-modal.html", login_user_form=form)


# @blueprint.get("/robots.txt")
# def robots_txt():
#     return "# robots.txt\n\nUser-agent: *\n\n"


# @blueprint.post("/star/")
# def create_star():
#     data = {
#         "new-star-name": request.form["new-star-name"],
#         "new-star-slug": request.form["new-star-slug"],
#         "new-pypi-repo": request.form["new-pypi-repo"],
#         "new-conda-repo": request.form["new-conda-repo"],
#         "new-github-repo": request.form["new-github-repo"],
#         "new-gitlab-repo": request.form["new-gitlab-repo"],
#         "repos": request.form.getlist("repos"),
#     }
#     new_star = new_star_from_web(data)

#     return redirect(f"/star/{new_star.slug}")


# @blueprint.get("/stars/")
# def list_stars():
#     return render_template("website/home.html")


# @blueprint.get("/star/<star_slug>")
# def interview_star(star_slug: str):
#     context_data = {
#         "l_last_5": db.session.query(Star).order_by(Star.created_at.desc()).limit(5).all(),
#         "l_random_5": db.session.query(Star).order_by(func.rand()).limit(5).all(),
#         "star": db.session.query(Star).filter(Star.slug == star_slug).first(),
#     }

#     return render_template("website/interview.html", **context_data)


# @blueprint.get("/styles/")
# def list_styles():
#     return render_template("website/home.html")


# @blueprint.get("/copy_metadata")
# def copy_metadata():
#     from rich import print

#     todos = db.session.query(Star).all()
#     data: list = []
#     for p in todos:
#         row: dict = {}
#         # print(f"{p.slug=} {p.pypi_id=}")
#         row.update({"slug": p.slug})
#         if p.pypi_id:
#             row.update({"pypi_id": p.pypi_id})
#             queue = (
#                 db.session.query(StarQueue)
#                 .filter(StarQueue.pypi_repo_id == p.pypi_id)
#                 .order_by(StarQueue.id.desc())
#                 .first()
#             )
#             if queue:
#                 row.update({"queue_id": queue.id})
#                 if queue.response_data:
#                     info = queue.response_data.get("info", None)
#                     if info:
#                         upd = False
#                         if not p.description:
#                             p.description = info.get("summary", None)
#                             upd = True
#                         if not p.star_url:
#                             home_page = info.get("home_page", None)
#                             try:
#                                 urls_home = info["project_urls"]["Homepage"]
#                             except Exception:
#                                 urls_home = None

#                             if home_page == urls_home:
#                                 p.star_url = home_page
#                             elif not home_page and urls_home:
#                                 p.star_url = urls_home
#                             elif home_page and not urls_home:
#                                 p.star_url = home_page
#                             upd = True

#                         if not p.booklet_url:
#                             docs_url = info.get("docs_url", None)
#                             try:
#                                 urls_docs = info["project_urls"]["Documentation"]
#                             except Exception:
#                                 urls_docs = None

#                             if docs_url == urls_docs:
#                                 p.booklet_url = docs_url
#                             elif not docs_url and urls_docs:
#                                 p.booklet_url = urls_docs
#                             elif docs_url and not urls_docs:
#                                 p.booklet_url = docs_url
#                             upd = True

#                         row.update(
#                             {
#                                 "data": {
#                                     "home_page": info.get("home_page", None),
#                                     "docs_url": info.get("docs_url", None),
#                                     "download_url": info.get("download_url", None),
#                                     "project_url": info.get("project_url", None),
#                                     "project_urls": info.get("project_urls", None),
#                                 }
#                             }
#                         )
#                         if upd:
#                             print(f"Info updated for [bold]{p.slug}[/bold]!")
#                             db.session.commit()
#                     else:
#                         row.update({"data": "NO_INFO"})
#                 else:
#                     row.update({"data": "NO_DATA"})

#             else:
#                 row.update({"queue_id": "NO_ID"})

#         else:
#             row.update({"pypi_id": "NO_ID"})
#         print(f"{row=}")
#         data.append(row)

#     return jsonify(data)
