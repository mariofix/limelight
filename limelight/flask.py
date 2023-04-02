from flask import Blueprint, current_app


blueprint = Blueprint(
    "limelight", __name__, template_folder="templates", static_folder="static"
)


@blueprint.route("/recipe/<int:id>")
def recipe(id):
    # imprime la receta con lista de ingredientes
    return 1
