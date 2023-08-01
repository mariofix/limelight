from .database import db
from .models import GithubRepo, Lineup, PypiRepo, QueueStatus, Star, StarQueue, Style
from .tasks import send_email
from .version import __version_info_str__ as __version__


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
            new_pypi_repo = PypiRepo(slug=form_data.get("new-pypi-repo"))
            new_star.pypi_repo = new_pypi_repo
            db.session.add(new_pypi_repo)
            db.session.commit()
            new_queue = StarQueue(
                status=QueueStatus.CREATED,
                pypi_repo=new_pypi_repo,
                request_url=new_pypi_repo.json_url(),
                post_process="pypi_repo",
            )
            db.session.add(new_queue)
            db.session.commit()
        except Exception as e:
            print(e)
            raise Exception("No se pudo crear el repo PyPi")
    if "github" in form_data.get("repos"):
        try:
            new_github_repo = GithubRepo(namespace=form_data.get("new-github-repo"))
            new_star.github_repo = new_github_repo
            db.session.add(new_github_repo)
            db.session.commit()
            new_queue = StarQueue(
                status=QueueStatus.CREATED,
                github_repo=new_github_repo,
                request_url=new_github_repo.json_url(),
                post_process="github_repo",
            )
            db.session.add(new_queue)
            db.session.commit()
        except Exception as e:
            print(e)
            raise Exception("No se pudo crear el repo Github")

    send_email.delay(
        f"New Star {new_star.slug}",
        "new_star",
        "bot@mariofix.com",
        ["mariohernandezc@gmail.com"],
        {},
        "mariofix@pm.me",
    )

    return new_star


def get_star_info(slug: str) -> Star:
    return db.session.query(Star).filter(Star.slug == slug).first()


def get_context_data() -> dict:
    data = {
        "app_version": __version__,
        "q_stars": db.session.query(Star).count(),
        "q_styles": db.session.query(Style).count(),
        "q_lineups": db.session.query(Lineup).count(),
        "q_queues": db.session.query(StarQueue).filter(StarQueue.status == QueueStatus.CREATED).count(),
        "l_all_styles": db.session.query(Style).all(),
    }
    return data
