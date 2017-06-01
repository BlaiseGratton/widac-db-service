# WIDAC Database REST Service

Getting Started:

1. After cloning, create a virtual environment (e.g. `virtualenv venv`) and then run `pip install -r requirements.txt`

2. Initialize a PostgreSQL database instance by running `createdb demo`. If you create it under a different name you need to change the local postgres url that `app.py` points to

3. Follow the Heroku tutorial to deploy a Python app. Note that you must initialize a postgres database as an addon. The following link contains all the required steps: https://devcenter.heroku.com/articles/getting-started-with-python#introduction

4. Heroku is set up as a git remote for the python app. Automate the database url the remote app connects to by running `heroku config:set HEROKU=1`
