from .database import db
from .models import PypiRepo, Star, StarQueue


def new_star_from_web(form_data) -> Star:
    star = db.session.query(Star).filter(Star.slug == form_data.get("new-star-slug")).first()
    if star:
        return star

    try:
        new_star = Star(slug=form_data.get("new-star-slug"), title=form_data.get("new-star-name"))
        db.session.add(new_star)
        db.session.commit()
    except Exception as e:
        print(e)
        return {}

    if "pypi" in form_data.get("repos"):
        try:
            new_pypi_package = PypiRepo(slug=form_data.get("new-pypi-repo"))
            new_star.pypi_package = new_pypi_package
            db.session.add(new_pypi_package)
            db.session.commit()
            new_queue = StarQueue(pypi_slug=form_data.get("new-pypi-repo"), status="created", package=new_pypi_package)
            db.session.add(new_queue)
            db.session.commit()
        except Exception as e:
            print(e)
            return {}

    return new_star


def get_star_info(slug: str) -> Star:
    return db.session.query(Star).filter(Star.slug == slug).first()
