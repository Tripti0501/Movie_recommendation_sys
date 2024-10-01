from flask import Flask, render_template, redirect, request, url_for, session
import sqlite3
import requests
import random
app = Flask(__name__)
app.secret_key = '0731a259b56dbeb85d58c4fba3f5912638f2971ffaf8c183'
TMDB_API_KEY = 'e8cf8b13183a04b0c73dd5f6ea3ac6e7'
DATABASE = 'movies.db'
TMDB_API_KEY = 'e8cf8b13183a04b0c73dd5f6ea3ac6e7'
genre_mapping = {
    'Action': 28,       #these id's i found from TMDB API's documentations
    'Adventure': 12,
    'Animation': 16,
    'Comedy': 35,
    'Crime': 80,
    'Documentary': 99,
    'Drama': 18,
    'Family': 10751,
    'Fantasy': 14,
    'History': 36,
    'Horror': 27,
    'Music': 10402,
    'Mystery': 9648,
    'Romance': 10749,
    'Science Fiction': 878,
    'TV Movie': 10770,
    'Thriller': 53,
    'War': 10752,
    'Western': 37
}
def connect_db():
    return sqlite3.connect(DATABASE)
def init_db():
    with connect_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                age INTEGER,
                profession TEXT,
                genre TEXT,
                rating INTEGER
            )
        ''')
init_db()
@app.route('/', methods=['GET', 'POST'])
def give():
    if request.method == 'POST':
        name = request.form.get('name')
        lastname = request.form.get('lastname')  
        email = request.form.get('email')
        age = request.form.get('age')
        profession = request.form.get('profession')
        if not name or not email:  
            return "Name and email are required!", 400  
        session['name'] = name # here session is used for storing all these data temporarily on the server
        session['lastname'] = lastname  
        session['email'] = email
        session['age'] = age 
        session['profession'] = profession  
        return redirect(url_for('tutu'))  # here redirect means it says to browser move to next web page and url_for tells which page will be open and here insider the url_for() directly says index2 file so it will be open automaitcally.
    return render_template('index.html')
@app.route('/index2', methods=['POST', 'GET'])
def tutu():
    if request.method == 'POST':
        genre = request.form.get('genre')
        rating = request.form.get('imdb')  
        # Retrieve data from session
        name = session.get('name')
        lastname = session.get('lastname')
        email = session.get('email')
        age = session.get('age')
        profession = session.get('profession')

        if not genre or not rating or not name or not email:
            return "All fields are required!", 400

        try:
            rating = float(rating)
            if rating < 1 or rating > 10:
                return "Rating must be between 1 and 10", 400
        except ValueError:
            return "Invalid rating value", 400

        try:
            with connect_db() as conn:
                conn.execute('''INSERT INTO user_movies (name, email, age, profession, genre, rating)
                                VALUES (?, ?, ?, ?, ?, ?)''',
                             (name, email, age, profession, genre, rating))
                conn.commit()

            # Fetch movie recommendations based on genre and rating
            genre_id = genre_mapping.get(genre, 18)  # Default to Drama if not found
            movies = get_movie_recommendations(genre_id, rating)

        except sqlite3.Error as e:
            return "Database error", 500

        return render_template('recommendation.html', movies=movies, user_name=name)

    return render_template('index2.html')
def get_movie_recommendations(genre_id, rating):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": genre_id,
        "vote_average.gte": rating,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "page": 1
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raises HTTPError if the response is unsuccessful
        data = response.json()
        movies = []
        movie_list = data['results']  # List of movies returned by the API
        random.shuffle(movie_list)
        for movie in data['results'][:10]:  # Limit to 10 movies
            movies.append({
                'title': movie['title'],
                'overview': movie['overview'],
                'poster_path': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else None,
                'vote_average': movie['vote_average']
            })
        return movies
    except requests.exceptions.ConnectTimeout:
        print("Connection timed out. Please try again later.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []
@app.route('/result')
def result():
    with connect_db() as conn:
        cursor = conn.execute('SELECT * FROM user_movies')
        data = cursor.fetchall()
    return render_template('result.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
