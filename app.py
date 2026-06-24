import pickle
import pandas as pd
import requests
from flask import Flask,render_template,request



app = Flask(__name__)

movies_dict = pickle.load(open('movie_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl','rb'))

API_KEY = "6ebdb0f3a9c366ae210776ab7fbba528"

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"
    videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        credits_data = requests.get(credits_url,headers=headers,timeout=20).json()
        data = requests.get(url,headers=headers,timeout=20).json()
        videos_data = requests.get(videos_url,headers=headers, timeout=20).json()
    except Exception as e:
        print("TMDB ERROR:",e)
        return None

    rating = data.get("vote_average")

    year = data.get("release_date","")[:4]

    genres = ",".join(genre["name"] for genre in data.get("genres",[])
                     )
    overview = data.get("overview")

    director = "Not Available"

    for person in credits_data.get("crew",[]):
        if person["job"] == "Director":
            director = person["name"]
            break

    cast = ",".join(
        actor["name"]
        for actor in credits_data.get("cast",[])[:6]
    )

    trailer = "#"
    for video in videos_data.get("results",[]):
        if video["site"] == "YouTube" and video["type"] == "Trailer":
            trailer = f"https://www.youtube.com/watch?v={video['key']}"
            break


    poster_path = data.get('poster_path')


    if poster_path:
        return {
            "poster":  "https://image.tmdb.org/t/p/w500" + poster_path,
            "rating": rating,
            "year": year,
            "genres": genres,
            "overview": overview,
            "director": director,
            "cast": cast,
            "trailer": trailer
        }
    return None


def recommend(movie):
    print("Selected Movie:", movie)
    movie_index = movies[movies['title'] == movie].index[0]
    print("Movie Index:",movie_index)
    distances = similarity[movie_index]

    movie_list = sorted(list(enumerate(distances)),reverse=True,key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        print("Recommended:",movies.iloc[i[0]].title)
        movie_id = movies.iloc[i[0]].movie_id
        movie_details = fetch_poster(movie_id)
        if movie_details is None:
            continue
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(movie_details)
    # print(recommended_posters[0])
    return recommended_movies,recommended_posters

@app.route("/", methods=["GET","POST"])
def home():
    movie_names = movies['title'].values

    movie_data = []
    if request.method == "POST":
        selected_movie = request.form.get("movie")

        recommendations,posters = recommend(selected_movie)
        print(posters[0])

        movie_data = list(zip(recommendations,posters))

    return  render_template(
        "index.html",
        movie_names=movie_names,
        movie_data=movie_data
    )

if __name__ == "__main__":
    app.run(debug=True)