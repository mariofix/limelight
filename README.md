# limelight

## Babel

```shell
poetry run pybabel extract . -F babel/babel.cfg -o babel/base.pot
poetry run pybabel init -l es -i babel/base.pot -d limelight/translations
poetry run pybabel init -l en -i babel/base.pot -d limelight/translations
poetry run pybabel compile -d limelight/translations
poetry run pybabel update -i babel/base.pot -d limelight/translations
```
