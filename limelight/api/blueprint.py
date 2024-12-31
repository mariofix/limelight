from flask import Blueprint, jsonify

from ..crud import create_project, find_project
from ..forms import NewProjectForm
from ..limiter import limiter

blueprint = Blueprint("api", __name__)


@blueprint.post("/new-project/")
@limiter.limit("1 per minute")
def new_project():
    form = NewProjectForm()
    if form.validate_on_submit():
        if project := find_project(form.data["slug"]):
            return jsonify(project), 200
        new_project = create_project(form.data, True)
        return jsonify({"slug": new_project.slug}), 201
    return jsonify(form.errors), 400
