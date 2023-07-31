.PHONY: env-info
env-info:
	poetry env info

# MIG_MSG="new thing" make migrations
.PHONY: migrations
migrations:
	poetry run flask db migrate -m "${MIG_MSG}"

.PHONY: upgrade-db
upgrade-db:
	poetry run flask db upgrade head

.PHONY: pre-commit
pre-commit:
	poetry run pre-commit autoupdate -j 2
	poetry run pre-commit run --all-files
