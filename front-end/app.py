import logging
import webbrowser
from flask import Flask, render_template, request
from imagescraper import ImageScraper
import pandas as pd
import imdb
from content_based_app import recommend

app = Flask(__name__, static_folder='UI/static')


#app = Flask(__name__)
app.config["Debug"] = True

imgscrape = ImageScraper()
matric_factorization_df = pd.read_csv("file2.csv")
knn_df = pd.read_csv("file1.csv")

# Configure Flask app logger
app.logger.setLevel(logging.INFO)  # Set log level to INFO

file_handler = logging.FileHandler('flask.log')
file_handler.setLevel(logging.INFO)  # Set log level for file handler
app.logger.addHandler(file_handler)

url_cache = {}
recommendation_cache = {}


@app.route("/homepage", methods=["GET"])
def homepage():
    app.logger.info('Accessed homepage')
    return render_template("index.html")


@app.route("/content_based", methods=["POST"])
def show_content_based_recommendation():
    try:
        movie_name = request.form["movie_name"]
        app.logger.info(f'Content-based recommendation requested for movie: {movie_name}')

        movie_list = generate_file3(movie_name)
        movie_inputs = []
        for movie in movie_list:
            if movie not in url_cache:
                img_url = imgscrape.get_poster_url(movie)
                url_cache[movie] = img_url  # Store in cache
                app.logger.info(f"Movie: {movie}, Image URL: {img_url}")
            else:
                img_url = url_cache[movie]  # Fetch from cache
                app.logger.info(f"Movie: {movie}, Image URL fetched from cache: {img_url}")
            
            movie_inputs.append({"movie_name": movie, "img_url": img_url})

        return render_template(
            "content_based_recommendation.html",
            movie_name=movie_name,
            movie_list=movie_inputs,
        )
    except Exception as e:
        app.logger.error(f'Error in content-based recommendation: {str(e)}')
        return "Couldn't find that! Please try again."
    

@app.route("/show_recommendation", methods=["POST"])
def show_recommendation():
    try:
        user_id = int(request.form["user_id"])
        if not 0 < user_id < 611:
            raise UserIDException(user_id)

        if user_id not in recommendation_cache:
            matrix_data = list(matric_factorization_df.iloc[user_id - 1])
            knn_data = list(knn_df.iloc[user_id - 1])
            matrix_send_data = []
            knn_send_data = []
            for x in matrix_data:
                if x not in recommendation_cache:
                    url = imgscrape.get_poster_url(x)
                    recommendation_cache[x] = url  # Store in cache
                    app.logger.info(f"Movie: {x}, Image URL: {url}")
                else:
                    url = recommendation_cache[x]  # Fetch from cache
                    app.logger.info(f"Movie: {x}, Image URL fetched from cache: {url}")
                matrix_send_data.append(url)

            for x in knn_data:
                if x not in recommendation_cache:
                    url = imgscrape.get_poster_url(x)
                    recommendation_cache[x] = url  # Store in cache
                    app.logger.info(f"Movie: {x}, Image URL: {url}")
                else:
                    url = recommendation_cache[x]  # Fetch from cache
                    app.logger.info(f"Movie: {x}, Image URL fetched from cache: {url}")
                knn_send_data.append(url)

            recommendation_cache[user_id] = (matrix_send_data, knn_send_data)  # Store in cache

        else:
            matrix_send_data, knn_send_data = recommendation_cache[user_id]  # Fetch from cache

        return render_template(
            "id_based_recommendation.html",
            matrix_data=matrix_send_data,
            knn_data=knn_send_data,
        )

    except UserIDException as e:
        return f"Please enter a userid between 1 and 610, your userid was {str(e.value)}"


class UserIDException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def generate_file3(movie_name):
    recommend(movie_name)
    content_based_rec = pd.read_csv("file3.csv")
    return content_based_rec.columns.tolist()


if __name__ == "__main__":
    # Open the browser automatically
    webbrowser.open("http://127.0.0.1:5000/homepage")

    # Start the Flask development server
    app.run()
