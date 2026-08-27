# ============================================================
# M1000 — FLASK APPLICATION
# Netflix-Inspired Movie Website
# Yellow + Black Edition
# ============================================================

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from flask import Flask, abort, render_template, request


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
MOVIES_FILE = DATA_DIR / "movies.json"


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)


app.config.update(
    JSON_AS_ASCII=False,
    TEMPLATES_AUTO_RELOAD=True,
)


# ============================================================
# DATA LOADING
# ============================================================

def load_movies() -> list[dict[str, Any]]:
    """
    Load movie information from data/movies.json.

    Expected format:

    {
        "movies": [
            {
                "id": "movie-id",
                "title": "Movie Title",
                "poster": "https://example.com/poster.jpg",
                "backdrop": "https://example.com/backdrop.jpg",
                "year": 2026,
                "category": "Tamil HD Movies",
                "description": "...",
                "downloads": []
            }
        ]
    }
    """

    if not MOVIES_FILE.exists():
        print(f"[ERROR] Movie database not found: {MOVIES_FILE}")
        return []

    try:
        with MOVIES_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

    except json.JSONDecodeError as error:
        print(
            "[ERROR] Invalid movies.json:",
            error,
        )
        return []

    except OSError as error:
        print(
            "[ERROR] Unable to read movies.json:",
            error,
        )
        return []

    # --------------------------------------------------------
    # Support both:
    #
    # { "movies": [...] }
    #
    # and:
    #
    # [...]
    # --------------------------------------------------------

    if isinstance(data, dict):

        movies = data.get("movies", [])

    elif isinstance(data, list):

        movies = data

    else:

        movies = []

    if not isinstance(movies, list):
        return []

    # Keep only valid dictionary records.
    return [
        movie
        for movie in movies
        if isinstance(movie, dict)
    ]


# ============================================================
# MOVIE DATABASE
# ============================================================

def get_movies() -> list[dict[str, Any]]:
    """
    Return the current movie collection.

    The JSON file is loaded per request so you can update
    movies.json without restarting the application during
    development.
    """

    return load_movies()


# ============================================================
# MOVIE HELPERS
# ============================================================

def get_movie_by_id(
    movie_id: str,
) -> dict[str, Any] | None:

    movie_id = str(movie_id).strip()

    for movie in get_movies():

        current_id = str(
            movie.get("id", "")
        ).strip()

        if current_id == movie_id:
            return movie

    return None


def get_categories(
    movies: list[dict[str, Any]],
) -> list[str]:

    categories: set[str] = set()

    for movie in movies:

        category = movie.get("category")

        if isinstance(category, str):

            category = category.strip()

            if category:
                categories.add(category)

    return sorted(
        categories,
        key=str.lower,
    )


def normalize_text(value: Any) -> str:

    if value is None:
        return ""

    return str(value).strip().lower()


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    movies = get_movies()

    categories = get_categories(movies)

    # --------------------------------------------------------
    # Featured movie
    # --------------------------------------------------------

    featured = None

    for movie in movies:

        if movie.get("featured") is True:
            featured = movie
            break

    # If no featured movie is defined,
    # use the first movie.
    if featured is None and movies:
        featured = movies[0]

    # --------------------------------------------------------
    # Newest movies
    # --------------------------------------------------------

    newest_movies = sorted(
        movies,
        key=lambda movie: str(
            movie.get("added_date", "")
        ),
        reverse=True,
    )

    # --------------------------------------------------------
    # Popular movies
    # --------------------------------------------------------

    popular_movies = [
        movie
        for movie in movies
        if movie.get("popular") is True
    ]

    # Fallback when no movies are marked popular.
    if not popular_movies:
        popular_movies = movies[:12]

    return render_template(
        "home.html",
        movies=movies,
        featured=featured,
        newest_movies=newest_movies[:12],
        popular_movies=popular_movies[:12],
        categories=categories,
    )


# ============================================================
# MOVIE DETAIL
# ============================================================

@app.route("/movie/<movie_id>")
def movie_detail(movie_id: str):

    movie = get_movie_by_id(movie_id)

    if movie is None:
        abort(404)

    # --------------------------------------------------------
    # Similar movies
    # --------------------------------------------------------

    category = normalize_text(
        movie.get("category")
    )

    similar_movies = []

    for item in get_movies():

        if str(item.get("id", "")) == str(movie_id):
            continue

        if normalize_text(
            item.get("category")
        ) == category:

            similar_movies.append(item)

    return render_template(
        "movie.html",
        movie=movie,
        similar_movies=similar_movies[:8],
    )


# ============================================================
# CATEGORY PAGE
# ============================================================

@app.route("/category/<path:category_name>")
def category(category_name: str):

    movies = get_movies()

    requested_category = normalize_text(
        category_name
    )

    filtered_movies = [
        movie
        for movie in movies
        if normalize_text(
            movie.get("category")
        ) == requested_category
    ]

    # Keep the original display name when possible.
    display_category = category_name

    for movie in movies:

        category_value = movie.get("category")

        if normalize_text(
            category_value
        ) == requested_category:

            display_category = str(
                category_value
            )

            break

    return render_template(
        "category.html",
        movies=filtered_movies,
        category_name=display_category,
    )


# ============================================================
# SEARCH
# ============================================================

@app.route("/search")
def search():

    query = request.args.get(
        "q",
        "",
    ).strip()

    movies = get_movies()

    if not query:

        return render_template(
            "search.html",
            movies=[],
            query="",
        )

    # Prevent unnecessarily large queries.
    query = query[:100]

    search_text = query.lower()

    results = []

    for movie in movies:

        searchable_fields = [

            movie.get("title", ""),

            movie.get("description", ""),

            movie.get("category", ""),

            movie.get("language", ""),

            movie.get("genre", ""),

            movie.get("year", ""),
        ]

        combined_text = " ".join(
            str(value)
            for value in searchable_fields
        ).lower()

        if search_text in combined_text:

            results.append(movie)

    return render_template(
        "search.html",
        movies=results,
        query=query,
    )


# ============================================================
# ALL MOVIES
# ============================================================

@app.route("/movies")
def all_movies():

    movies = get_movies()

    return render_template(
        "category.html",
        movies=movies,
        category_name="All Movies",
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    movies = get_movies()

    return {
        "status": "ok",
        "movies": len(movies),
    }


# ============================================================
# 404 ERROR
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


# ============================================================
# 500 ERROR
# ============================================================

@app.errorhandler(500)
def internal_server_error(error):

    return render_template(
        "404.html"
    ), 500


# ============================================================
# TEMPLATE GLOBALS
# ============================================================

@app.context_processor
def inject_globals():

    return {
        "site_name": "M1000",
        "site_tagline": "Movies. Series. Endless Entertainment.",
        "current_year": 2026,
    }


# ============================================================
# DEVELOPMENT SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("M1000 — Yellow & Black Streaming UI")
    print("=" * 60)
    print(f"Database: {MOVIES_FILE}")
    print(f"Database exists: {MOVIES_FILE.exists()}")
    print(f"Movies loaded: {len(get_movies())}")
    print("=" * 60)
    print()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
