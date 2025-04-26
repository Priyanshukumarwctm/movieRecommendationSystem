import streamlit as st
import pickle
import pandas as pd
import requests
from PIL import Image

# -------------------------------
# Load Model Files with Exception Handling
# -------------------------------
@st.cache_resource
def load_model_data():
    try:
        movies = pickle.load(open('movie_list.pkl', 'rb'))

        # similarity = pickle.load(open('similarity.pkl','rb'))

        # Number of parts
        num_parts = 8
        
        # Recombine the parts
        combined_data = []
        for i in range(1, num_parts + 1):
            part_file = f'similarity_part{i}.pkl'
            with open(part_file, 'rb') as part_f:
                part_data = pickle.load(part_f)
                combined_data.extend(part_data)  # Combine the lists or arrays

        # Use the recombined data
        similarity = combined_data
        return movies, similarity

    except FileNotFoundError:
        st.error("Model files not found. Please check if movie_list.pkl and similarity.pkl exist.")
        return None, None
    except Exception as e:
        st.error(f"Error loading model files: {e}")
        return None, None

# -------------------------------
# Fetch Poster from TMDb API
# -------------------------------
def fetch_poster(movie_id):
    try:
        api_key = "20eed2e47fd42c2200ed5238eddfeb17"  # Replace with your actual TMDb API key
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "poster_error"
    except:
        return "poster_error"

# -------------------------------
# Recommend Movies Function
# -------------------------------
def recommend(movie, movies_df, similarity_matrix):
    try:
        if movie not in movies_df['title'].values:
            raise ValueError("Selected movie not found in dataset.")

        index = movies_df[movies_df['title'] == movie].index[0]
        distances = similarity_matrix[index]
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

        recommended_titles = []
        recommended_posters = []

        for i in movie_list:
            movie_id = movies_df.iloc[i[0]].movie_id
            recommended_titles.append(movies_df.iloc[i[0]].title)
            recommended_posters.append(fetch_poster(movie_id))

        return recommended_titles, recommended_posters

    except ValueError as ve:
        st.error(str(ve))
        return [], []
    except Exception as e:
        st.error(f"Error during recommendation: {e}")
        return [], []

# -------------------------------
# Streamlit UI
# -------------------------------
def main():
    st.set_page_config(page_title="Movie Recommender System")
    st.title("🎬 Movie Recommender System")

    # Load data
    movies_df, similarity_matrix = load_model_data()

    if movies_df is not None and similarity_matrix is not None:
        with st.container():
            movie_list = movies_df['title'].values
            selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list, key="movie_selectbox")

        if st.button("Show Recommendations"):
            names, posters = recommend(selected_movie, movies_df, similarity_matrix)

            if names and posters:
                st.subheader("🎥 Top 5 Recommended Movies")
                cols = st.columns(5)

                for i in range(len(names)):
                    with cols[i]:
                        if posters[i] == "poster_error":
                            try:
                                img = Image.open("Internet_Error.jpg")
                                st.markdown("""
                                    <style>
                                        .stImage img {
                                            pointer-events: none;
                                            border-radius: 10px;
                                            box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
                                            height: 180px;
                                        }
                                        button[title="View fullscreen"] {
                                            display: none;
                                        }
                                    </style>
                                """, unsafe_allow_html=True)

                                
                                st.image(img, width=130)

                                st.markdown(f"""
                                    </div>
                                        <p style='
                                            text-align: center;
                                        '>
                                        {names[i]}
                                        </p>
                                    </div>
                                """, unsafe_allow_html=True)

                            except FileNotFoundError:
                                st.error("Error image not found")
                                st.write(names[i])
                        else:
                            st.markdown(f"""
                                <div style='text-align: center;'>
                                    <img src="{posters[i]}" width="200" style="border-radius: 10px; box-shadow: 2px 2px 8px rgba(0,0,0,0.3);'>
                                    <p style="margin-top: 10px; font-weight: bold;">{names[i]}</p>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.warning("⚠️ No recommendations to display. Please select a valid movie.")

    st.markdown("---")
    st.markdown("<div style='text-align: center;'>Made with ❤️ by Priyanshu Kumar</div>", unsafe_allow_html=True)

# -------------------------------
# Run the App
# -------------------------------
if __name__ == '__main__':
    main()
