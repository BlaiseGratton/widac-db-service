# WIDAC Database REST Service

Getting Started:

1. Follow the Heroku tutorial to deploy a Python app. Note that you must initialize a postgres database as an addon. The following link contains all the required steps: https://devcenter.heroku.com/articles/getting-started-with-python#introduction

2. Heroku is set up as a git remote for the python app. For local development comment out the line heroku = Heroku(app) and uncomment out the line app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/demo'. Before deploying any changes to Heroku, comment out the line app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/demo' and uncomment out the line heroku = Heroku(app)

3. Set app.run(debug=False) for production. 

