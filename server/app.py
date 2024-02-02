#from flask import Flask

#app = Flask(__name__)

#@app.route('/')
#def hello_world():
#   return 'Hello, World! This is a Flask web server.'

#if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0', port=5050)


#from flask import Flask, render_template

#app = Flask(__name__)

#@app.route("/")
#def index():
#  return render_template("index.html")

#@app.route("/formulaire")
#def page_formulaire():
#  return render_template("formulaire.html")
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
import json
import os
import uuid  # Pour générer des ID uniques


app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

login_manager = LoginManager(app)


API_URL = 'http://api:5051'  # Faut utiliser le nom défini sur docker-compose.yml (note pour moi)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'users.json')
# Fonction pour chargement de data de users.json
def load_user_data():
    try:
        with open(USERS_FILE, 'r') as file:
            users_data = json.load(file)
            return users_data or []  
    except FileNotFoundError:
        return []
    
def save_user_data(users_data):
    with open(USERS_FILE, 'w') as file:
        json.dump(users_data, file, indent=2)


# User class
class User(UserMixin):
    def __init__(self, user_id, username, password, email=None):
        self.id = str(user_id)
        self.username = username
        self.password = password
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    users = load_users_from_file()  
    return users.get(user_id)

def load_users_from_file():
    users = {}
    with open('users.json', 'r') as file:
        user_data = json.load(file)
        for user_entry in user_data:
            user = User(
                user_entry.get('id'),
                user_entry.get('username'),
                user_entry.get('password'),
                user_entry.get('email')
            )
            users[user.id] = user
    return users



# Route pour l'affichage de la page login
@app.route('/login')
def login():
    return render_template('login.html')

# Route pour l'affichage de la page sigup
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Route pour l'opération de login
@app.route('/login', methods=['POST'])
def perform_login():
    username = request.form['username']
    password = request.form['password']

    users = load_users_from_file()
    user = next((user for user in users.values() if user.username == username and user.password == password), None)

    if user:
        login_user(user)
        return redirect(url_for('landing', message='Login successful'))
    else:
        return render_template('login.html', message='Invalid credentials. Please try again.')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing', message='Logout successful'))

def generate_user_id():
    return str(uuid.uuid4())

# Route pour la page sigup
@app.route('/signup', methods=['POST'])
def signup_user():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']

    users_data = load_user_data()

    for user in users_data:
        if user['username'] == username:
            return render_template('signup.html', message='Username already exists. Please choose another.')

    # Ajout du nouvel utilisateur
    new_user = {'id': len(users_data) + 1, 'username': username, 'password': password, 'email': email}
    users_data.append(new_user)
    save_user_data(users_data)

    # Redirection vers la page de login
    return redirect(url_for('login', message='Signup successful. Please login.'))

@app.route('/')
def landing():
    # Charger la data des films depuis l'API
    movies_response = requests.get(f'{API_URL}/movies')
    movies = movies_response.json().get('movies', [])

    return render_template('landing.html', movies=movies, section='list')

@app.route('/process_form', methods=['POST'])
@login_required
def add_movie():
    
    title = request.form.get('title')
    genre = request.form.get('genre')
    year = request.form.get('year')

    new_movie = {'title': title, 'genre': genre, 'year': year}

    # Une requete post pour l'api pour l'ajout du nouveau film
    response = requests.post(f'{API_URL}/movies', json=new_movie)

    # Répense de l'api
    if response.status_code == 200:
        return render_template('result_adding.html', message=response.json().get('message'))
    else:
        return render_template('result_adding.html', message='Failed to add the movie')

@app.route('/delete_movie', methods=['POST'])
@login_required
def delete_movie():
    
    movie_id = request.form.get('movie_id')

    # Requete Delete envoyé à l'api pour supprimer le film par son ID
    response = requests.delete(f'{API_URL}/movies/{movie_id}')

    
    if response.status_code == 200:
        return render_template('result_delete.html', message=response.json().get('message'))
    else:
        return render_template('result_delete.html', message='Failed to delete the movie')

def search_movies_post():
    query = request.form.get('query', '')
    
    return redirect(url_for('search_movies', query=query))


@app.route('/search', methods=['GET', 'POST'])
def search_movies():
    if request.method == 'POST':
        
        query = request.form.get('query', '')
        
        return redirect(url_for('search_movies', query=query))

    query = request.args.get('query', '')
    
    # Chercher les resultats de la recherche depuis l'api
    search_response = requests.get(f'{API_URL}/movies/search', params={'query': query})
    search_results = search_response.json()  
    
    return render_template('result_search.html', query=query, results=search_results)

@app.route('/rate_movie', methods=['POST'])
@login_required
def rate_movie():
    try:
        data = request.get_json()
        movie_id = data.get('movieId')
        user_rating = int(data.get('userRating'))

        
        movies_response = requests.get(f'{API_URL}/movies')
        movies = movies_response.json().get('movies', [])

        
        movie = next((m for m in movies if str(m['id']) == movie_id), None)

        if movie:
            
            movie['ratings'].append({'username': current_user.username, 'rating': user_rating})

            update_response = requests.put(f'{API_URL}/movies/{movie_id}', json=movie)

            if update_response.status_code == 200:
                return jsonify({'success': True, 'message': 'Rating submitted successfully.'}), 200
            else:
                return jsonify({'success': False, 'message': 'Failed to update movie data in the API'}), 500
        else:
            return jsonify({'success': False, 'message': 'Movie not found.'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)









#@app.route('/jinja')
#def jinja():
    # Load movie data from films.json
#    with open('films.json', 'r') as file:
#        movies = json.load(file)

    # Render the template with the movie data
#    return render_template('jinja.html', movies=movies)
