import pickle
import requests
import streamlit as st
import requests
import os

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names,recommended_movie_posters


# st.header('Movie Recommender System')
# movies = pickle.load(open('movie_list.pkl','rb'))
# similarity = pickle.load(open('similarity.pkl','rb'))

def download_file_from_google_drive(file_id, dest_path):
    """
    Downloads a file from Google Drive to a local destination.

    Args:
        file_id (str): The ID of the file to download from Google Drive.
        dest_path (str): The local file path to save the downloaded file.
    """
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    session = requests.Session()

    response = session.get(url, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {"confirm": token}
        response = session.get(url, params=params, stream=True)

    save_response_content(response, dest_path)

def get_confirm_token(response):
    """
    Extracts the confirmation token from the response cookies if present.
    """
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    return None

def save_response_content(response, dest_path):
    """
    Saves the content of the response to the specified file path.
    """
    CHUNK_SIZE = 32768

    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:  # Filter out keep-alive new chunks
                f.write(chunk)

@st.cache_data
def load_files():
    """
    Loads the pickle files, downloading them from Google Drive if not present locally.
    """
    # Google Drive File IDs
    movie_file_id = "1cDIb1bxVFJJkYX8FNxcC2Ufh5HcBOuKa"
    similarity_file_id = "12yT7yyp24p0cnaeWKKr3sKpGVuSYx5kA"

    # Local file paths
    movie_file_path = "movie_list.pkl"
    similarity_file_path = "similarity.pkl"

    # Download files if not present locally
    if not os.path.exists(movie_file_path):
        download_file_from_google_drive(movie_file_id, movie_file_path)
    if not os.path.exists(similarity_file_path):
        download_file_from_google_drive(similarity_file_id, similarity_file_path)

    # Load the pickle files
    with open(movie_file_path, "rb") as f:
        movies = pickle.load(f)

    with open(similarity_file_path, "rb") as f:
        similarity = pickle.load(f)

    return movies, similarity

# Streamlit App
st.header("Movie Recommender System")

# Load the files
movies, similarity = load_files()



movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names,recommended_movie_posters = recommend(selected_movie)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommended_movie_names[0])
        st.image(recommended_movie_posters[0])
    with col2:
        st.text(recommended_movie_names[1])
        st.image(recommended_movie_posters[1])

    with col3:
        st.text(recommended_movie_names[2])
        st.image(recommended_movie_posters[2])
    with col4:
        st.text(recommended_movie_names[3])
        st.image(recommended_movie_posters[3])
    with col5:
        st.text(recommended_movie_names[4])
        st.image(recommended_movie_posters[4])