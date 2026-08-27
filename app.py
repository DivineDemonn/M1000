"""
=============================================================
M1000 — CINEMATIC MOVIE WEBSITE
=============================================================

Main Flask application.

Architecture:
    Flask
    ├── Home
    ├── Movie details
    ├── Categories
    ├── Search
    ├── 404 handling
    └── JSON movie catalogue

Theme:
    Black + Gold / Yellow
    Premium cinematic streaming UI

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
# APPLICATION CONFIGURATION
# =============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

MOVIES_FILE = DATA_DIR / "movies.json"


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)


# =============================================================
# APPLICATION SETTINGS
# =============================================================

app.config.update(
    SECRET_KEY="change-this-secret-key",

    # Prevent unnecessary caching while developing.
    SEND_FILE_MAX_AGE_DEFAULT=0,

    # Maximum search query length.
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,
)


# =============================================================
# AD CONFIGURATION
# =============================================================
#
# These are ONLY placement identifiers/settings.
#
# Put your actual Adsterra publisher code inside the
# corresponding template later.
#
# Recommended placements:
#
#   TOP       → between hero and latest movies
#   MIDDLE    → between movie sections
#   BOTTOM    → before footer
#
# Keep advertisements visually separated from navigation
# and download/watch controls.
# =============================================================

ADS = {
    "enabled": True,

    "top": True,

    "middle": True,

    "bottom": True,

    "mobile": True,
}


# =============================================================
# MOVIE DATA
# =============================================================

def load_movies() -> list[dict[str, Any]]:
    """
    Load movie information from data/movies.json.

    Returns:
        list:
            A list of movie dictionaries.

    If the JSON file does not exist or contains invalid JSON,
    an empty list is returned instead of crashing the website.
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


    except json.JSONDecodeError as exc:

        app.logger.error(
            "Invalid movies.json: %s",
            exc,
        )

        return []


    except OSError as exc:

        app.logger.error(
            "Unable to read movies.json: %s",
            exc,
        )

        return []


    if not isinstance(data, list):

        app.logger.error(
            "movies.json must contain a JSON array."
        )

        return []


    # Only keep valid dictionary objects.
    movies = [
        movie
        for movie in data
        if isinstance(movie, dict)
    ]


    return movies


# =============================================================
# FIND MOVIE
# =============================================================

def find_movie(movie_id: str) -> dict[str, Any] | None:
    """
    Find one movie by its unique ID.
    """

    movies = load_movies()


    for movie in movies:

        if str(movie.get("id", "")) == str(movie_id):

            return movie


    return None


# =============================================================
# NORMALIZE TEXT
# =============================================================

def normalize_text(value: Any) -> str:
    """
    Convert arbitrary values into searchable lowercase text.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


# =============================================================
# SEARCH MOVIES
# =============================================================

def search_movies(query: str) -> list[dict[str, Any]]:
    """
    Search the movie catalogue.

    Searches through:
        title
        description
        language
        type
        genre
        year
    """

    query = normalize_text(query)

    if not query:
        return []


    movies = load_movies()

    results: list[dict[str, Any]] = []


    for movie in movies:

        searchable_parts: list[str] = []


        # -----------------------------------------------------
        # Basic fields
        # -----------------------------------------------------

        for field in (
            "title",
            "description",
            "language",
            "type",
            "year",
            "rating",
        ):

            value = movie.get(field)

            if value is not None:

                searchable_parts.append(
                    normalize_text(value)
                )


        # -----------------------------------------------------
        # Genre
        # -----------------------------------------------------

        genres = movie.get("genre", [])


        if isinstance(genres, list):

            searchable_parts.extend(
                normalize_text(genre)
                for genre in genres
            )

        else:

            searchable_parts.append(
                normalize_text(genres)
            )


        # -----------------------------------------------------
        # Final searchable text
        # -----------------------------------------------------

        searchable_text = " ".join(
            searchable_parts
        )


        if query in searchable_text:

            results.append(movie)


    return results


# =============================================================
# CATEGORY MOVIES
# =============================================================

def get_category_movies(
    category_name: str,
) -> list[dict[str, Any]]:
    """
    Return movies belonging to a category.

    Category matching is intentionally flexible.

    Examples:
        Tamil
        Tamil Movies
        Web Series
        Tamil Dubbed
        Action
    """

    category = normalize_text(category_name)

    if not category:
        return []


    movies = load_movies()

    results: list[dict[str, Any]] = []


    for movie in movies:

        searchable_parts: list[str] = []


        for field in (
            "title",
            "language",
            "type",
        ):

            value = movie.get(field)

            if value is not None:

                searchable_parts.append(
                    normalize_text(value)
                )


        genres = movie.get("genre", [])


        if isinstance(genres, list):

            searchable_parts.extend(
                normalize_text(genre)
                for genre in genres
            )

        else:

            searchable_parts.append(
                normalize_text(genres)
            )


        searchable_text = " ".join(
            searchable_parts
        )


        if category in searchable_text:

            results.append(movie)


    return results


# =============================================================
# FEATURED MOVIE
# =============================================================

def get_featured_movie(
    movies: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """
    Return the first movie marked as featured.

    If no movie is marked featured, use the first movie.
    """

    if not movies:
        return None


    for movie in movies:

        if movie.get("featured") is True:

            return movie


    return movies[0]


# =============================================================
# GLOBAL TEMPLATE DATA
# =============================================================

@app.context_processor
def inject_global_data() -> dict[str, Any]:
    """
    Variables available inside every Jinja template.
    """

    return {
        "site_name": "M1000",

        "site_tagline": (
            "Your cinematic destination."
        ),

        "current_year": 2026,

        "ads": ADS,
    }


# =============================================================
# HOME PAGE
# =============================================================

@app.route("/")
def home():
    """
    Main M1000 homepage.
    """

    movies = load_movies()


    featured = get_featured_movie(
        movies
    )


    # ---------------------------------------------------------
    # Latest
    # ---------------------------------------------------------

    latest_movies = movies[:12]


    # ---------------------------------------------------------
    # Featured / Popular
    # ---------------------------------------------------------

    popular_movies = sorted(
        movies,
        key=lambda movie: float(
            movie.get("rating", 0) or 0
        ),
        reverse=True,
    )[:12]


    # ---------------------------------------------------------
    # Tamil
    # ---------------------------------------------------------

    tamil_movies = [
        movie
        for movie in movies
        if "tamil"
        in normalize_text(
            movie.get("language")
        )
    ][:12]


    # ---------------------------------------------------------
    # Web Series
    # ---------------------------------------------------------

    web_series = [
        movie
        for movie in movies
        if (
            "web"
            in normalize_text(
                movie.get("type")
            )
            or
            "series"
            in normalize_text(
                movie.get("type")
            )
        )
    ][:12]


    return render_template(
        "home.html",

        movies=movies,

        featured=featured,

        latest_movies=latest_movies,

        popular_movies=popular_movies,

        tamil_movies=tamil_movies,

        web_series=web_series,
    )


# =============================================================
# MOVIE DETAIL PAGE
# =============================================================

@app.route("/movie/<movie_id>")
def movie_detail(movie_id: str):
    """
    Display a single movie/series.
    """

    movie = find_movie(movie_id)


    if movie is None:

        abort(404)


    # ---------------------------------------------------------
    # Related movies
    # ---------------------------------------------------------

    all_movies = load_movies()


    movie_genres = movie.get(
        "genre",
        [],
    )


    if not isinstance(
        movie_genres,
        list,
    ):

        movie_genres = [
            movie_genres
        ]


    movie_genres_normalized = {
        normalize_text(genre)
        for genre in movie_genres
    }


    related_movies: list[
        dict[str, Any]
    ] = []


    for item in all_movies:

        if item.get("id") == movie.get("id"):
            continue


        item_genres = item.get(
            "genre",
            [],
        )


        if not isinstance(
            item_genres,
            list,
        ):

            item_genres = [
                item_genres
            ]


        item_genres_normalized = {
            normalize_text(genre)
            for genre in item_genres
        }


        if (
            movie_genres_normalized
            & item_genres_normalized
        ):

            related_movies.append(item)


        if len(related_movies) >= 6:
            break


    return render_template(
        "movie.html",

        movie=movie,

        related_movies=related_movies,
    )


# =============================================================
# CATEGORY PAGE
# =============================================================

@app.route("/category/<path:category_name>")
def category(category_name: str):
    """
    Display movies belonging to a category.
    """

    movies = get_category_movies(
        category_name
    )


    return render_template(
        "category.html",

        movies=movies,

        category_name=category_name,
    )


# =============================================================
# SEARCH PAGE
# =============================================================

@app.route("/search")
def search():
    """
    Search M1000 movie catalogue.
    """

    query = request.args.get(
        "q",
        "",
        type=str,
    ).strip()


    # ---------------------------------------------------------
    # Protect against extremely long queries.
    # ---------------------------------------------------------

    query = query[:100]


    results = search_movies(query)


    return render_template(
        "search.html",

        results=results,

        query=query,
    )


# =============================================================
# OPTIONAL HEALTH CHECK
# =============================================================

@app.route("/health")
def health():
    """
    Simple health endpoint.

    Useful for deployment monitoring.
    """

    return {
        "status": "ok",
        "site": "M1000",
    }


# =============================================================
# 404 ERROR
# =============================================================

@app.errorhandler(404)
def page_not_found(error):
    """
    Custom 404 page.
    """

    return (
        render_template(
            "404.html"
        ),
        404,
    )


# =============================================================
# 500 ERROR
# =============================================================

@app.errorhandler(500)
def internal_server_error(error):
    """
    Custom 500 page.
    """

    app.logger.exception(
        "Internal server error"
    )


    return (
        render_template(
            "404.html"
        ),
        500,
    )


# =============================================================
# APPLICATION START
# =============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
