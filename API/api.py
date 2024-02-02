#from flask import Flask, jsonify

#app = Flask(__name__)

# Route simple pour renvoyer un message JSON
#@app.route('/', methods=['GET'])
#def hello_api():
#    return jsonify({'message': 'Hello REIMS!'})

#if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0', port=5051)



import json
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Chargement de data de films.json
with open('films.json', 'r') as file:
    movies = json.load(file)

@app.route('/movies', methods=['GET'])
def get_movies():
    return jsonify({'movies': movies})

def get_next_movie_id():
    # Trouver le maximum ID existant
    max_id = max(movie.get('id', 0) for movie in movies)
    # Incrémenter le maximum ID pour avoir le nouveau ID
    return max_id + 1

@app.route('/movies', methods=['POST'])
def add_movie():
    new_movie = request.get_json()

    # Donner le nouveau ID au film ajouté
    new_movie['id'] = get_next_movie_id()

    movies.append(new_movie)

    # Enregistrement du nouveau film sur le fichier films.json
    with open('films.json', 'w') as file:
        json.dump(movies, file, indent=2)

    return jsonify({'message': 'Movie added successfully'})


@app.route('/movies/<int:movie_id>', methods=['POST', 'DELETE'])
def delete_movie(movie_id):

    for movie in movies:
        if movie.get('id') == movie_id:
            movies.remove(movie)
            # Supression du film avec son ID et enregistrement de la nouvelle liste sur films.json
            with open('films.json', 'w') as file:
                json.dump(movies, file, indent=2)
            return jsonify({'message': 'Movie deleted successfully'})

    # Si le film ID n'existe pas
    return jsonify({'error': 'Movie not found'}), 404

@app.route('/movies/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '').lower()
    
    # Si aucune recherche n'est faite, retourner toute la liste des films
    if not query:
        return jsonify(movies)

    # Chercher le film à base de son titre
    search_results = [movie for movie in movies if query in movie.get('title', '').lower()]
    print(f"Search Query: {query}")
    print(f"Search Results: {search_results}")
    return jsonify(search_results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5051)