from flask import Blueprint, jsonify

from .. import utils
from ..database import db
from ..forms import NewProjectForm

blueprint = Blueprint("api", __name__)


@blueprint.post("/new-project/")
def new_project():
    form = NewProjectForm()
    if form.validate_on_submit():
        project = utils.project_exists(db, form.data["slug"])
        if project:
            return jsonify(project), 200
        else:
            new_project = utils.create_project(db, form.data)
            new_project = utils.process_pypi_data(new_project)
            return jsonify(new_project), 201
    return jsonify(form.errors), 400
