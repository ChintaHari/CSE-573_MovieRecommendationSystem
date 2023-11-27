# Get Movie Poster from IMDB from the Movie Title
import json
import logging
from bs4 import BeautifulSoup
import requests
import os
from PIL import Image
from io import BytesIO
import urllib
import imdb


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageScraper:
    def __init__(self):
        self.ia = imdb.IMDb()
        
    def beautiful_soup(self, url):
        response = requests.get(url)
        return BeautifulSoup(response.content, "html.parser")

    def get_IMDb_ID2(self, title):
        url = f"http://www.imdb.com/find?s=tt&q={title}"
        soup = self.beautiful_soup(url)
        if result := soup.find("a", {"class": "ipc-metadata-list-summary-item__t"}):
            imdb_id = result.get("href").split("/")[2]
            logger.info(f"IMDb ID found for {title}: {imdb_id}")
            return imdb_id
        logger.warning(f"No IMDb ID found for {title}")
        return None
        
    def get_IMDb_ID(self, title):
        search = self.ia.search_movie(title)
        for result in search:
            logger.info(f"Found: {result['title']} ({result.movieID})")
            return result.movieID
        logger.warning(f"No IMDb ID available for {title}")
        return None

    def get_movie_info_IMDb(self, title):
        imdb_id = self.get_IMDb_ID(title)
        if not imdb_id:
            logger.warning(f"No IMDb ID available for {title}")
            return None
        url = f"https://www.imdb.com/title/{imdb_id}/?ref_=fn_tt_tt_1"
        soup = self.beautiful_soup(url)
        movie_info = json.loads(
            str(soup.findAll("script", {"type": "application/ld+json"})[0].text)
        )
        logger.info(f"Movie info retrieved for {title}")
        return movie_info

    def get_poster_url2(self, title):
        if movie_info := self.get_movie_info_IMDb(title):
            return movie_info["image"]
        return None
        
        
    def get_poster_url(self, title):
        imdb_id = self.get_IMDb_ID(title)
        access = imdb.IMDb()
        movie = access.get_movie(imdb_id)

        logger.info(f"Title: {movie['title']} Year: {movie['year']}")
        cover_url = movie.get('cover url')
        if cover_url:
            logger.info(f"Cover URL: {cover_url}")
            return cover_url

        logger.warning("Cover URL not found.")
        return None

    def download_poster(self, title, dir_name):
        if src := self.get_poster_url(title):
            if not os.path.isdir(dir_name):
                os.mkdir(dir_name)
            response = requests.get(src)
            ext = src.split(".")[-1]
            img = Image.open(BytesIO(response.content))
            img.save(f"{dir_name}/{title}.{ext}")
        else:
            print(f"No poster found for {title}")
