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
   f_name = db.Column(db.String(32), nullable = False)
   l_name = db.Column(db.String(32), nullable = False);
   

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



def userExists(email):
    return User.query.filter_by(email=email).first()

class Book(db.Model):
    __tablename__ = 'book'

    email = db.Column(db.String(80), primary_key=True, nullable=False)
    fileid = db.Column(db.Integer, nullable=False)




#########################################
#                                       #
#                                       #
#    FLASK SETTINGS ETC ETC ETC ETC     #
#                                       #
#                                       #
#########################################


def verify_password(hash, passx):
    try:
        return ph.verify(hash, passx)
    except:
        return False

@od.route('/')
def index():
    return flask.render_template('home.html')

@od.route('/join', methods=['POST'])
def join():
    if 'role' in flask.request.form:
        role_num = flask.request.form['role']
        role = ""
        if role_num == 0:
            role = "Author"
        elif role_num == 1:
            role = "Editor"
        elif role_num == 2:
            role = "Publisher"
        if role.startswith('A') or role.startswith('E'):
            v_role_name = 'n {0}'.format(role)
        else:
            v_role_name = ' {0}'.format(role)
        return flask.render_template('join.html', role_name=role, v_role_name=v_role_name)
    email = flask.request.form['email']
    password = flask.request.form['password']

    return flask.redirect(flask.urlfor('document'))


@od.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return flask.render_template('login.html')
    email = flask.request.form['email']
    password = flask.request.form['password']
    if not email:
        return flask.render_template('login.html', error="email field empty")
    if not password:
        return flask.render_template('login.html', error="password field empty")
    user = userExists(email)
    if user is None:
        return flask.render_template('login.html', error="user does not exist")
    if verifyPassword(user.password, password):
        return flask.redirect(flask.urlfor('/'))
    return flask.render_template('login.html', error="password does not match the account on file")

    

@od.route('/document')
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
   if userExists(email):
      user = User.query.get(email)
      if verify_password(user.password, passw):
         return user
   return

@od.route('/doc/', defaults={'page': '0'})
@od.route('/doc/<page>')
def docs(page):
    return flask.render_template('edit_doc.html', page=page)

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
