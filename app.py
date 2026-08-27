```python
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
    Load movies from:

        data/movies.json

    Supported formats:

    1. Direct list:

        [
            {
                "id": "movie-001",
                "title": "Toxic"
            }
        ]

    2. Object containing movies:

        {
            "movies": [
                {
                    "id": "movie-001",
                    "title": "Toxic"
                }
            ]
        }
    """

    if not MOVIES_FILE.exists():
        print(f"[ERROR] Movie database not found: {MOVIES_FILE}")
        return []

    try:
        with MOVIES_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        print(f"[ERROR] Invalid movies.json: {error}")
        return []

    except OSError as error:
        print(f"[ERROR] Unable to read movies.json: {error}")
        return []

    # --------------------------------------------------------
    # Accept both:
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
        print("[ERROR] movies.json must contain a list or a movies object.")
        return []

    if not isinstance(movies, list):
        print("[ERROR] 'movies' must be a list.")
        return []

    valid_movies = []

    for movie in movies:
        if isinstance(movie, dict):
            valid_movies.append(movie)

    print(f"[INFO] Loaded {len(valid_movies)} movies.")

    return valid_movies


# ============================================================
# MOVIE DATABASE
# ============================================================

def get_movies() -> list[dict[str, Any]]:
    """
    Reload movies.json every request.

    This means updating movies.json does not require
    restarting Flask during development.
    """

    return load_movies()


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(value: Any) -> str:
    """
    Convert any value to clean lowercase searchable text.
    """

    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


def searchable_genre(movie: dict[str, Any]) -> str:
    """
    Handle genre when it is either:

        ["Action", "Thriller"]

    or:

        "Action, Thriller"
    """

    genre = movie.get("genre", "")

    if isinstance(genre, list):
        return " ".join(
            normalize_text(item)
            for item in genre
        )

    return normalize_text(genre)


# ============================================================
# MOVIE HELPERS
# ============================================================

def get_movie_by_id(
    movie_id: str,
) -> dict[str, Any] | None:

    requested_id = normalize_text(movie_id)

    for movie in get_movies():

        current_id = normalize_text(
            movie.get("id", "")
        )

        if current_id == requested_id:
            return movie

    return None


# ============================================================
# CATEGORY HELPERS
# ============================================================

def get_categories(
    movies: list[dict[str, Any]],
) -> list[str]:

    categories: set[str] = set()

    for movie in movies:

        category_value = movie.get("category")

        if isinstance(category_value, str):

            category_value = category_value.strip()

            if category_value:
                categories.add(category_value)

    return sorted(
        categories,
        key=str.lower,
    )


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

    if not popular_movies:
        popular_movies = movies[:12]

    return render_template(
        "home.html",

        movies=movies,

        # Your current home.html uses both names
        # in different versions, so provide both.
        featured=featured,
        featured_movie=featured,

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

    movie_category = normalize_text(
        movie.get("category")
    )

    similar_movies = []

    for item in get_movies():

        item_id = normalize_text(
            item.get("id", "")
        )

        if item_id == normalize_text(movie_id):
            continue

        item_category = normalize_text(
            item.get("category")
        )

        if (
            movie_category
            and item_category == movie_category
        ):
            similar_movies.append(item)

    return render_template(
        "movie.html",
        movie=movie,
        similar_movies=similar_movies[:8],
    )


# ============================================================
# MOVIE ROUTE ALIAS
# ============================================================
#
# IMPORTANT:
#
# Your templates currently use:
#
#     url_for('movie', movie_id=movie.id)
#
# But the original Flask function was:
#
#     movie_detail
#
# This alias prevents BuildError problems.
# ============================================================

@app.route(
    "/movie/<movie_id>",
    endpoint="movie",
)
def movie_route_alias(movie_id: str):

    movie = get_movie_by_id(movie_id)

    if movie is None:
        abort(404)

    movie_category = normalize_text(
        movie.get("category")
    )

    similar_movies = []

    for item in get_movies():

        item_id = normalize_text(
            item.get("id", "")
        )

        if item_id == normalize_text(movie_id):
            continue

        if normalize_text(
            item.get("category")
        ) == movie_category:

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

    filtered_movies = []

    for movie in movies:

        movie_category = normalize_text(
            movie.get("category")
        )

        if movie_category == requested_category:
            filtered_movies.append(movie)

    # --------------------------------------------------------
    # Keep original capitalization
    # --------------------------------------------------------

    display_category = category_name

    for movie in movies:

        original_category = movie.get(
            "category",
            ""
        )

        if (
            normalize_text(original_category)
            == requested_category
        ):

            display_category = str(
                original_category
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
    )

    # --------------------------------------------------------
    # Clean query
    # --------------------------------------------------------

    query = str(query).strip()

    # Prevent huge search requests.
    query = query[:100]

    movies = get_movies()

    # --------------------------------------------------------
    # Empty search
    # --------------------------------------------------------

    if not query:

        return render_template(
            "search.html",
            movies=[],
            query="",
        )

    # --------------------------------------------------------
    # Normalize search
    # --------------------------------------------------------

    search_text = normalize_text(query)

    results = []

    # --------------------------------------------------------
    # Search every movie
    # --------------------------------------------------------

    for movie in movies:

        title = normalize_text(
            movie.get("title", "")
        )

        original_title = normalize_text(
            movie.get("original_title", "")
        )

        description = normalize_text(
            movie.get("description", "")
        )

        category_value = normalize_text(
            movie.get("category", "")
        )

        language = normalize_text(
            movie.get("language", "")
        )

        year = normalize_text(
            movie.get("year", "")
        )

        genre = searchable_genre(movie)

        movie_id = normalize_text(
            movie.get("id", "")
        )

        # ----------------------------------------------------
        # Combine searchable fields
        # ----------------------------------------------------

        searchable_text = " ".join(
            [
                title,
                original_title,
                description,
                category_value,
                language,
                genre,
                year,
                movie_id,
            ]
        )

        # ----------------------------------------------------
        # Direct substring search
        # ----------------------------------------------------

        if search_text in searchable_text:
            results.append(movie)
            continue

        # ----------------------------------------------------
        # Multi-word search
        #
        # Example:
        #
        # "Toxic 2026"
        #
        # will match Toxic + 2026.
        # ----------------------------------------------------

        search_words = search_text.split()

        if search_words:

            if all(
                word in searchable_text
                for word in search_words
            ):
                results.append(movie)

    print(
        f"[SEARCH] Query='{query}' Results={len(results)}"
    )

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
# APPLICATION START
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
```
