from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme  # type: ignore
from flask_babel import lazy_gettext as _

from ..database import db
from ..models import Project, ProjectTags, Tag
from .views import ProjectAdmin, ProjectTagAdmin, TagAdmin

admin_site = Admin(name="limelight", theme=Bootstrap4Theme(swatch="pulse", fluid=False))

admin_site.add_view(ProjectAdmin(Project, db.session, category=_("Projects")))
admin_site.add_view(TagAdmin(Tag, db.session, category=_("Projects")))
admin_site.add_view(ProjectTagAdmin(ProjectTags, db.session, category=_("Projects")))
