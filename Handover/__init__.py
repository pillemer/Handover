# Before running flask you must type these lines into the shell:
# > $env:FLASK_APP = "application" (where 'application' is the name of the application) # noqa E501
# > $env:FLASK_ENV = "development" (to set flask debug mode on and thus enable changes to load instead of having to quit and restart each time.) # noqa E501
# > flask run


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SECRET_KEY'] = '778cb3228b406566077e7771fbd8b8c7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Handover.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from Handover import routes # noqa E402