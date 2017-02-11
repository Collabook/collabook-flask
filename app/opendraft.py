import flask
from flask_oauth import OAuth


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

(secret_key, g_client_id, g_client_sec) = read_for_secrets('google.secret')

#########################################
#                                       #
#                                       #
#    FLASK SETTINGS ETC ETC ETC ETC     #
#                                       #
#                                       #
#########################################

od = flask.Flask(__name__)
od.debug = True
od.secret_key = secret_key
redirect_oauth_uri = '/api/oauth/redirect'
od.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/main.db'

oauth = OAuth()
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=g_client_id,
                          consumer_secret=g_client_sec)


@od.route('/')
def home():
    a_token = flask.session.get('access_token')
    return flask.render_template('home.html')

@od.route('/login')
def login():
    return google.authorize(callback=flask.url_for('authorized', _external=true))

@google.tokengetter
def get_access_token():
    return flask.session.get('access_token')

def main():
    app.run()
if __name__ == '__main__':
    main()