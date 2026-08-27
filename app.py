"""
=========================================================
M1000 — CINEMATIC MOVIE WEBSITE
Flask Application
=========================================================

Project structure:

M1000/
│
├── app.py
├── requirements.txt
├── Procfile
│
├── data/
│   └── movies.json
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── movie.html
│   ├── search.html
│   └── 404.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js

=========================================================
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    abort,
    jsonify,
    render_template,
    request,
)


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

MOVIES_FILE = DATA_DIR / "movies.json"


app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


# =========================================================
# APPLICATION SETTINGS
# =========================================================

app.config.update(
    SECRET_KEY=os.environ.get(
        "SECRET_KEY",
        "m1000-development-secret",
    ),

    JSON_SORT_KEYS=False,

    SEND_FILE_MAX_AGE_DEFAULT=86400,
)


# =========================================================
# MOVIE DATA
# =========================================================

def load_movies() -> list[dict[str, Any]]:
    """
    Load movie information from data/movies.json.

    Returns:
        list: Movie dictionaries.

    If the JSON file is missing or invalid,
    an empty list is returned instead of crashing
    the entire website.
    """

    if not MOVIES_FILE.exists():
        app.logger.warning(
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


    # -----------------------------------------------------
    # Support both:
    #
    # [
    #   {...},
    #   {...}
    # ]
    #
    # and:
    #
    # {
    #   "movies": [...]
    # }
    # -----------------------------------------------------

    if isinstance(data, list):

        return [
            movie
            for movie in data
            if isinstance(movie, dict)
        ]


    if isinstance(data, dict):

        movies = data.get("movies", [])

        if isinstance(movies, list):

            return [
                movie
                for movie in movies
                if isinstance(movie, dict)
            ]


    app.logger.warning(
        "Unsupported movies.json format."
    )

    return []


# =========================================================
# MOVIE HELPERS
# =========================================================

def movie_id(movie: dict[str, Any]) -> str:
    """
    Return a normalized movie ID.
    """

    value = movie.get("id")

    if value is None:
        return ""

    return str(value).strip()


def movie_title(movie: dict[str, Any]) -> str:
    """
    Return a safe movie title.
    """

    title = movie.get(
        "title",
        "Untitled",
    )

    return str(title).strip()


def movie_category(movie: dict[str, Any]) -> str:
    """
    Return movie category.
    """

    category = movie.get(
        "category",
        "Movies",
    )

    return str(category).strip()


def find_movie(
    requested_id: str,
) -> dict[str, Any] | None:
    """
    Find one movie by ID.
    """

    requested_id = str(
        requested_id
    ).strip()


    if not requested_id:
        return None


    movies = load_movies()


    for movie in movies:

        if movie_id(movie) == requested_id:

            return movie


    return None


# =========================================================
# HOME DATA
# =========================================================

def get_featured_movie(
    movies: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Select the featured movie.

    Priority:
        1. featured = true
        2. first available movie
    """

    for movie in movies:

        if movie.get("featured") is True:

            return movie


    if movies:

        return movies[0]


    return None


def get_categories(
    movies: list[dict[str, Any]],
) -> list[str]:
    """
    Return unique categories.
    """

    categories: list[str] = []


    for movie in movies:

        category = movie_category(movie)


        if (
            category
            and category not in categories
        ):

            categories.append(category)


    return categories


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    """
    M1000 homepage.
    """

    movies = load_movies()

    featured = get_featured_movie(
        movies
    )

    categories = get_categories(
        movies
    )


    return render_template(
        "index.html",

        movies=movies,

        featured=featured,

        categories=categories,

        page_title="M1000 — Watch Movies & Web Series",
    )


# =========================================================
# MOVIE DETAIL
# =========================================================

@app.route("/movie/<movie_id>")
def movie_detail(movie_id: str):
    """
    Display one movie.
    """

    movie = find_movie(movie_id)


    if movie is None:

        abort(404)


    # -----------------------------------------------------
    # Related movies
    # -----------------------------------------------------

    all_movies = load_movies()


    current_category = movie_category(
        movie
    )


    related_movies = [

        item

        for item in all_movies

        if (
            movie_id(item) != movie_id
            and
            movie_category(item)
            == current_category
        )

    ][:12]


    return render_template(
        "movie.html",

        movie=movie,

        related_movies=related_movies,

        page_title=(
            f"{movie_title(movie)} — M1000"
        ),
    )


# =========================================================
# CATEGORY
# =========================================================

@app.route("/category/<path:category_name>")
def category(category_name: str):
    """
    Display movies belonging to a category.
    """

    movies = load_movies()


    category_name = (
        category_name
        .strip()
    )


    filtered_movies = [

        movie

        for movie in movies

        if movie_category(movie).lower()
        == category_name.lower()

    ]


    return render_template(
        "search.html",

        movies=filtered_movies,

        heading=category_name,

        query=category_name,

        page_title=(
            f"{category_name} — M1000"
        ),
    )


# =========================================================
# SEARCH
# =========================================================

@app.route("/search")
def search():
    """
    Search movies by title,
    category, year, genre, and language.
    """

    query = request.args.get(
        "q",
        "",
    ).strip()


    movies = load_movies()


    # -----------------------------------------------------
    # Empty search
    # -----------------------------------------------------

    if not query:

        return render_template(
            "search.html",

            movies=[],

            heading="Search Movies",

            query="",

            page_title="Search — M1000",
        )


    search_query = query.lower()


    results: list[dict[str, Any]] = []


    for movie in movies:

        searchable_fields = [

            movie.get(
                "title",
                "",
            ),

            movie.get(
                "original_title",
                "",
            ),

            movie.get(
                "category",
                "",
            ),

            movie.get(
                "genre",
                "",
            ),

            movie.get(
                "language",
                "",
            ),

            movie.get(
                "year",
                "",
            ),

        ]


        searchable_text = " ".join(
            str(value)
            for value in searchable_fields
            if value is not None
        ).lower()


        if search_query in searchable_text:

            results.append(movie)


    return render_template(
        "search.html",

        movies=results,

        heading="Search Results",

        query=query,

        page_title=(
            f"Search: {query} — M1000"
        ),
    )


# =========================================================
# API — MOVIES
# =========================================================

@app.route("/api/movies")
def api_movies():
    """
    Return movie database as JSON.

    Useful for future AJAX features.
    """

    movies = load_movies()


    return jsonify(
        {
            "success": True,

            "count": len(movies),

            "movies": movies,
        }
    )


# =========================================================
# API — SINGLE MOVIE
# =========================================================

@app.route("/api/movie/<movie_id>")
def api_movie(movie_id: str):
    """
    Return a single movie as JSON.
    """

    movie = find_movie(movie_id)


    if movie is None:

        return jsonify(
            {
                "success": False,

                "error": "Movie not found.",
            }
        ), 404


    return jsonify(
        {
            "success": True,

            "movie": movie,
        }
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():
    """
    Simple deployment health check.
    """

    movies = load_movies()


    return jsonify(
        {
            "status": "ok",

            "app": "M1000",

            "movies": len(movies),
        }
    )


# =========================================================
# 404 ERROR
# =========================================================

@app.errorhandler(404)
def page_not_found(error):
    """
    Custom 404 page.
    """

    return render_template(
        "404.html",

        page_title="404 — M1000",
    ), 404


# =========================================================
# 500 ERROR
# =========================================================

@app.errorhandler(500)
def internal_server_error(error):
    """
    Custom 500 response.

    We keep this simple so the actual
    error remains in the server logs.
    """

    app.logger.exception(
        "Internal server error: %s",
        error,
    )


    return render_template(
        "404.html",

        page_title="Something went wrong — M1000",
    ), 500


# =========================================================
# TEMPLATE GLOBALS
# =========================================================

@app.context_processor
def inject_globals():
    """
    Variables available inside every template.
    """

    return {
        "site_name": "M1000",

        "current_year": 2026,

        "site_description": (
            "M1000 — Your cinematic movie destination."
        ),
    }


# =========================================================
# DEVELOPMENT SERVER
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000,
        )
    )


    debug = (
        os.environ.get(
            "FLASK_DEBUG",
            "0",
        )
        == "1"
    )


    app.run(
        host="0.0.0.0",

        port=port,

        debug=debug,
    )
