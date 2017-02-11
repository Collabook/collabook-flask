import flask
import flask_login
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher

od = flask.Flask(__name__)
od.debug = True

od.secret_key = "Y7L1xOBu2A0d08zUWO63753m3"
od.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/main.db'
ph = PasswordHasher()
db = SQLAlchemy(od)


login_manager = flask_login.LoginManager()
login_manager.login_view = "login"
login_manager.init_app(od)

class User(db.Model):
   __tablename__ = 'users'

   email = db.Column(db.String(80), primary_key=True, nullable=False)
   password = db.Column(db.String(128), nullable=False)
   role = db.Column(db.Integer, nullable=False)
   authenticated = db.Column(db.Boolean, default=False)

   def __init__(self, email, password, role):
      self.email = email
      self.password = password
      self.authenticated = False
      self.role = role

   def __repr__(self):
        return '<User e:{0}, u:{1}>'.format(self.email, self.username)

   def is_active(self):
        return True

   def get_id(self):
        return self.email

   def is_authenticated(self):
        return self.authenticated

   def is_anonymous(self):
        return False




#########################################
#                                       #
#                                       #
#    FLASK SETTINGS ETC ETC ETC ETC     #
#                                       #
#                                       #
#########################################

def email_exists(email):
    allUsers = User.query.all()
    for user in allUsers:
        if user.email == email:
            return True
    return False

def verify_password(hash, passx):
    try:
        return ph.verify(hash, passx)
    except:
        return False

@od.route('/')
def index():
    return flask.render_template('home.html')

@od.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html')
    flask_login.login_user(User("admin@od.haze.pw", "test", 1), remember=True)
    return flask.render_template('document.html')

@od.route('/document')
@flask_login.login_required
def document():
    return flask.render_template('document.html')

@login_manager.user_loader
def user_loader(email):
   if email_exists(email):
      usr = User.query.filter_by(email=email).first()
      usr.email = email
      return usr
   else:
      return

@login_manager.request_loader
def request_loader(request):
   email = request.form.get('email')
   passw = request.form.get('password')
   if email_exists(email):
      user = User.query.get(email)
      if verify_password(user.password, passw):
         return user
   return

@od.route('/logout')
@flask_login.login_required
def logout():
    user = flask_login.current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    flask_login.logout_user()
    return flask.redirect(flask.url_for('root'))

def main():
    od.run()

if __name__ == '__main__':
    main()