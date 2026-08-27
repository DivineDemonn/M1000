"""
=============================================================
M1000 — Netflix-Inspired Movie Website
=============================================================

Flask application entry point.

Features:
- JSON-based movie database
- Home page
- Movie details
- Category pages
- Search
- 404 handling
- Safe JSON loading
- Responsive frontend support
- Simple and lightweight architecture

Project structure:

M1000/
│
├── app.py
├── requirements.txt
│
├── data/
│   └── movies.json
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── movie.html
│   ├── category.html
│   ├── search.html
│   └── 404.html
│
└── static/
    ├── css/
    │   └── style.css
    │
    ├── js/
    │   └── app.js
    │
    └── images/
        └── logo.png
=============================================================
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    abort,
    render_template,
    request,
)


# =============================================================
# APPLICATION
# =============================================================

app = Flask(__name__)

app.config.update(
    SECRET_KEY="m1000-change-this-secret-key",
    JSON_AS_ASCII=False,
)


# =============================================================
# PATHS
# =============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

MOVIES_FILE = DATA_DIR / "movies.json"


# =============================================================
# CONSTANTS
# =============================================================

SITE_NAME = "M1000"

SUPPORTED_CATEGORIES = (
    "Tamil HD Movies",
    "Tamil New Movies",
    "Tamil Dubbed Movies",
    "Web Series",
)


# =============================================================
# JSON DATABASE
# =============================================================

def load_movies() -> list[dict[str, Any]]:
    """
    Load movies from data/movies.json.

    Returns:
        A list of movie dictionaries.

    The function intentionally fails safely instead of
    crashing the complete website because of a malformed
    or missing JSON file.
    """

    if not MOVIES_FILE.exists():
        app.logger.error(
            "Movie database not found: %s",
            MOVIES_FILE,
        )
        return []

    try:
        with MOVIES_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        app.logger.error(
            "Invalid movies.json: %s",
            error,
        )
        return []

    except OSError as error:
        app.logger.error(
            "Unable to read movies.json: %s",
            error,
        )
        return []

    if not isinstance(data, list):
        app.logger.error(
            "movies.json must contain a JSON array."
        )
        return []

    valid_movies: list[dict[str, Any]] = []

    for movie in data:

        if not isinstance(movie, dict):
            continue

        movie_id = movie.get("id")

        title = movie.get("title")

        if not movie_id or not title:
            continue

        valid_movies.append(movie)

    return valid_movies


# =============================================================
# MOVIE HELPERS
# =============================================================

def get_movie_by_id(
    movie_id: str,
) -> dict[str, Any] | None:
    """
    Find one movie by its unique ID.
    """

    movie_id = movie_id.strip()

    if not movie_id:
        return None

    for movie in load_movies():

        if str(movie.get("id", "")) == movie_id:
            return movie

    return None


def get_movies_by_category(
    category_name: str,
) -> list[dict[str, Any]]:
    """
    Return movies belonging to a category.
    """

    category_name = category_name.strip().casefold()

    movies = load_movies()

    return [
        movie
        for movie in movies
        if str(
            movie.get("category", "")
        ).strip().casefold()
        == category_name
    ]


def search_movies(
    query: str,
) -> list[dict[str, Any]]:
    """
    Search movie titles, original titles,
    genres, languages and categories.
    """

    query = query.strip().casefold()

    if not query:
        return []

    results: list[dict[str, Any]] = []

    for movie in load_movies():

        title = str(
            movie.get("title", "")
        ).casefold()

        original_title = str(
            movie.get("original_title", "")
        ).casefold()

        category = str(
            movie.get("category", "")
        ).casefold()

        language = str(
            movie.get("language", "")
        ).casefold()

        description = str(
            movie.get("description", "")
        ).casefold()

        genres = movie.get("genre", [])

        if not isinstance(genres, list):
            genres = []

        genre_text = " ".join(
            str(genre).casefold()
            for genre in genres
        )

        searchable_text = " ".join(
            (
                title,
                original_title,
                category,
                language,
                description,
                genre_text,
            )
        )

        if query in searchable_text:
            results.append(movie)

    return results


# =============================================================
# TEMPLATE HELPERS
# =============================================================

@app.context_processor
def inject_global_variables():
    """
    Variables available in every Jinja template.
    """

    return {
        "site_name": SITE_NAME,
        "categories": SUPPORTED_CATEGORIES,
    }


# =============================================================
# HOME
# =============================================================

@app.route("/")
def home():
    """
    M1000 homepage.

    Sections:
    - Featured
    - Trending
    - Latest
    - Web Series
    """

    movies = load_movies()

    featured = [
        movie
        for movie in movies
        if movie.get("featured") is True
    ]

    trending = [
        movie
        for movie in movies
        if movie.get("trending") is True
    ]

    latest = [
        movie
        for movie in movies
        if movie.get("latest") is True
    ]

    web_series = [
        movie
        for movie in movies
        if str(
            movie.get("type", "")
        ).casefold()
        == "series"
    ]

    # Use the first featured movie as the hero
    # if a featured item exists.
    featured_movie = (
        featured[0]
        if featured
        else (movies[0] if movies else None)
    )

    return render_template(
        "index.html",
        movies=movies,
        featured=featured,
        featured_movie=featured_movie,
        trending=trending,
        latest=latest,
        web_series=web_series,
    )


# =============================================================
# MOVIE DETAILS
# =============================================================

@app.route("/movie/<movie_id>")
def movie_detail(movie_id: str):
    """
    Display a movie or web-series detail page.
    """

    movie = get_movie_by_id(movie_id)

    if movie is None:
        abort(404)

    return render_template(
        "movie.html",
        movie=movie,
    )


# =============================================================
# CATEGORY
# =============================================================

@app.route("/category/<path:category_name>")
def category(category_name: str):
    """
    Display movies belonging to a category.

    Example:

        /category/Tamil%20HD%20Movies
        /category/Tamil%20New%20Movies
        /category/Web%20Series
    """

    movies = get_movies_by_category(
        category_name
    )

    return render_template(
        "category.html",
        category_name=category_name,
        movies=movies,
    )


# =============================================================
# SEARCH
# =============================================================

@app.route("/search")
def search():
    """
    Search movies.

    Example:

        /search?q=example
    """

    query = request.args.get(
        "q",
        "",
        type=str,
    ).strip()

    # Prevent unnecessarily huge queries.
    query = query[:100]

    results = search_movies(query)

    return render_template(
        "search.html",
        query=query,
        movies=results,
        result_count=len(results),
    )


# =============================================================
# API — MOVIES
# =============================================================

@app.route("/api/movies")
def api_movies():
    """
    Lightweight JSON endpoint.

    Useful if the frontend later needs
    asynchronous movie loading.
    """

    return {
        "success": True,
        "count": len(load_movies()),
        "movies": load_movies(),
    }


# =============================================================
# API — SINGLE MOVIE
# =============================================================

@app.route("/api/movie/<movie_id>")
def api_movie(movie_id: str):
    """
    Return one movie as JSON.
    """

    movie = get_movie_by_id(movie_id)

    if movie is None:
        return {
            "success": False,
            "error": "Movie not found",
        }, 404

    return {
        "success": True,
        "movie": movie,
    }


# =============================================================
# ROBOTS
# =============================================================

@app.route("/robots.txt")
def robots():
    """
    Basic robots.txt response.
    """

    return (
        "User-agent: *\n"
        "Allow: /\n"
    ), 200, {
        "Content-Type": "text/plain; charset=utf-8"
    }


# =============================================================
# 404 ERROR
# =============================================================

@app.errorhandler(404)
def page_not_found(error):
    """
    Custom 404 page.
    """

    return render_template(
        "404.html"
    ), 404


# =============================================================
# 500 ERROR
# =============================================================

@app.errorhandler(500)
def internal_server_error(error):
    """
    Custom 500 page.
    """

    return render_template(
        "404.html"
    ), 500


# =============================================================
# DEVELOPMENT SERVER
# =============================================================

if __name__ == "__main__":

    print()
    print("=" * 58)
    print("M1000 — Movie Website")
    print("=" * 58)
    print(f"Database : {MOVIES_FILE}")
    print(f"Movies   : {len(load_movies())}")
    print("URL      : http://127.0.0.1:5000")
    print("=" * 58)
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
