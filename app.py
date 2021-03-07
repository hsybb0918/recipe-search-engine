from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ini import FlaskIni


app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/')

# database path
# PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
# DATABASE = os.path.join(PROJECT_ROOT, 'data', 'se.db')

# SQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/se.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# deal with config.ini file
with app.app_context():
    app.iniconfig = FlaskIni()
    app.iniconfig.read('/modules/config.ini')

if __name__ == '__main__':
    from controller.search import *
    app.register_blueprint(search)

    app.run(debug=True)
