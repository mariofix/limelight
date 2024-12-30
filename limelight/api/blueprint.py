from flask import Blueprint, jsonify

from .. import utils
from ..database import db
from ..forms import NewProjectForm
from ..limiter import limiter

blueprint = Blueprint("api", __name__)


@blueprint.post("/new-project/")
@limiter.limit("1 per minute")
def new_project():
    form = NewProjectForm()
    if form.validate_on_submit():
        project = utils.project_exists(db, form.data["slug"])
        if project:
            return jsonify(project), 200
        else:
            new_project = utils.create_project(db, form.data)
            new_project = utils.fetch_project_info(new_project)
            new_project = utils.update_project_metadata(new_project)
            return jsonify({"slug": new_project.slug}), 201
    return jsonify(form.errors), 400
