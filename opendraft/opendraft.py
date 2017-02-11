import flask
import flask_login
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher

od = flask.Flask(__name__)
od.debug = True
(secret_key, g_client_id, g_client_sec) = read_for_secrets('google.secret')
od.secret_key = secret_key
od.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/main.db'
ph = PasswordHasher()
db = SQLAlchemy(od)

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



def read_for_secrets(file):
    insides = None
    id = None
    dev_sec = None
    secret = None
    with open('secrets/{}'.format(file)) as f:
        for line in f:
            if not line.startswith('|'):
                if line.startswith('id'):
                    id = line.split('=')[1]
                elif line.startswith('sec'):
                    secret = line.split('=')[1]
                elif line.startswith('dev'):
                    dev_sec = line.split('=')[1]
    return (dev_sec, id, secret)


#########################################
#                                       #
#                                       #
#    FLASK SETTINGS ETC ETC ETC ETC     #
#                                       #
#                                       #
#########################################

@app.route('/login', methods=['GET', 'POST'])
def login():
   if flask.request.method == 'GET':
      return flask.render_template('login.html')
   email = flask.request.form["email"]
   passw = flask.request.form["password"]
   pUser = User.query.get(email)
   if pUser:
      if verify_password(pUser.password, passw):
         pUser.authenticated = True
         db.session.add(pUser)
         db.session.commit()
         flask_login.login_user(pUser, remember=True)
         flask.flash('You were successfully logged in')
         return flask.redirect(flask.url_for("root"))
      else:
         return flask.render_template('login.html', error='password does not match')
   else:
     return flask.render_template('login.html', error='user does not exist')

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

@app.route('/logout')
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