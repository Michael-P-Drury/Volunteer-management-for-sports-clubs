from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

# sets up the website and the databases for the websites
# removed login

app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
app.app_context().push()

from . import routes