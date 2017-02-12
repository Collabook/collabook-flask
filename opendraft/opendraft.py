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
   fullName = db.Column(db.String(64), nullable=False)
   role = db.Column(db.Integer, nullable=False)
   authenticated = db.Column(db.Boolean, default=False)


   def __init__(self, email, fullName, password, role):
      self.email = email
      self.fullName = fullName
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

    def get_email(self):
        return self.email
    def get_fileid(self):
        return self.fileid



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

@od.route('/join', methods=['GET', 'POST'])
def join():
    if 'role' in flask.request.form:
        role_num = flask.request.form['role']
        role = None
        v_role_name = ""
        if role_num == '0':
            role = "Author"
        elif role_num == '1':
            role = "Editor"
        elif role_num == '2':
            role = "Publisher"
        else:
            role = "Unknown"
        if role.startswith('A') or role.startswith('E'):
            v_role_name = 'n {0}'.format(role)
        else:
            v_role_name = ' {0}'.format(role)
        print('"{0}" "{1}" "{2}"'.format(role_num, role, v_role_name))
        return flask.render_template('join.html', role_num=role_num, v_role_name=v_role_name)
    if not 'email' in flask.request.form:
        return flask.redirect(flask.url_for('index'))
    email = flask.request.form['email']
    password = flask.request.form['password']
    fullName = flask.request.form['fullname']
    role_num = flask.request.form['role_num']
    if not email:
        return flask.render_template('join.html', error="email field is empty")
    if not password:
        return flask.render_template('join.html', error="password field is empty")
    if not fullName:
        return flask.render_template('join.html', error="name field is empty")
    user = userExists(email)
    if not user is None:
        return flask.render_template('join.html', error="a user with that email already exists")
    user = User(email, fullName, ph.hash(password), role_num)
    with db.session.no_autoflush:
        db.session.add(user)
        db.session.commit()
    flask_login.login_user(user, remember=True)
    return flask.redirect(flask.url_for("document"))


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
        return flask.redirect(flask.url_for('root'))
    return flask.render_template('login.html', error="password does not match the account on file")

    

@od.route('/document')
def document():
    return flask.render_template('document.html')

@login_manager.user_loader
def user_loader(email):
   if userExists(email):
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
    return flask.redirect(flask.url_for('index'))

def main():
    od.run()

if __name__ == '__main__':
    main()
