from flask_admin import Admin
from flask_admin.theme import Bootstrap4Theme  # type: ignore
from flask_babel import lazy_gettext as _

from ..database import db
from ..models import Project, Queue, Tag
from .views import ProjectAdmin, QueueAdmin, TagAdmin

admin_site = Admin(name="limelight", theme=Bootstrap4Theme(swatch="pulse", fluid=False))

admin_site.add_view(ProjectAdmin(Project, db.session, category=_("Projects")))
admin_site.add_view(TagAdmin(Tag, db.session, category=_("Projects")))
admin_site.add_view(QueueAdmin(Queue, db.session, category=_("Projects")))
