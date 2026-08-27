```python
# ============================================================
# M1000 — FLASK APPLICATION
# Netflix-Inspired Movie Website
# Yellow + Black Edition
# ============================================================

from __future__ import annotations

import json
import os
import re
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

    Supports BOTH formats:

    1. Array format:

    [
        {
            "id": "movie-001",
            "title": "Toxic"
        }
    ]

    2. Object format:

    {
        "movies": [
            {
                "id": "movie-001",
                "title": "Toxic"
            }
        ]
    ]
    """

    if not MOVIES_FILE.exists():

        print(
            f"[ERROR] Movie database not found: "
            f"{MOVIES_FILE}"
        )

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
    # Support:
    #
    # [...]
    #
    # OR
    #
    # {"movies": [...]}
    # --------------------------------------------------------

    if isinstance(data, list):

        movies = data

    elif isinstance(data, dict):

        movies = data.get("movies", [])

    else:

        movies = []

    if not isinstance(movies, list):

        print(
            "[ERROR] movies.json must contain "
            "a list of movies."
        )

        return []

    # --------------------------------------------------------
    # Keep valid dictionary records only.
    # --------------------------------------------------------

    valid_movies = []

    for movie in movies:

        if isinstance(movie, dict):

            # Movie must have an ID.
            if movie.get("id"):

                valid_movies.append(movie)

    return valid_movies


# ============================================================
# MOVIE DATABASE
# ============================================================

def get_movies() -> list[dict[str, Any]]:
    """
    Reload movies.json every request.

    This means you can update movies.json and refresh
    the website without restarting Flask during development.
    """

    return load_movies()


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value: Any) -> str:
    """
    Convert text into a search-friendly format.

    Example:

        "  TOXIC  "
        -> "toxic"

        "Spider-Man"
        -> "spider man"
    """

    if value is None:

        return ""

    text = str(value)

    text = text.lower().strip()

    # Replace punctuation with spaces.
    text = re.sub(
        r"[^a-z0-9\u0B80-\u0BFF]+",
        " ",
        text,
    )

    # Remove duplicate spaces.
    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


# ============================================================
# SEARCH TEXT HELPER
# ============================================================

def value_to_search_text(value: Any) -> str:
    """
    Convert strings, lists and other values into searchable
    text.
    """

    if value is None:

        return ""

    if isinstance(value, list):

        return " ".join(
            value_to_search_text(item)
            for item in value
        )

    if isinstance(value, dict):

        return " ".join(
            value_to_search_text(item)
            for item in value.values()
        )

    return normalize_text(value)


# ============================================================
# MOVIE SEARCH
# ============================================================

def search_movies(
    movies: list[dict[str, Any]],
    query: str,
) -> list[dict[str, Any]]:

    query = normalize_text(query)

    if not query:

        return []

    # --------------------------------------------------------
    # Search each word separately.
    #
    # Example:
    #
    # "Toxic 2026"
    #
    # searches for both "toxic" and "2026".
    # --------------------------------------------------------

    query_words = query.split()

    results = []

    for movie in movies:

        searchable_values = [

            movie.get("title", ""),

            movie.get("original_title", ""),

            movie.get("description", ""),

            movie.get("category", ""),

            movie.get("language", ""),

            movie.get("genre", ""),

            movie.get("year", ""),

            movie.get("type", ""),

            movie.get("certificate", ""),

        ]

        combined_text = " ".join(
            value_to_search_text(value)
            for value in searchable_values
        )

        # ----------------------------------------------------
        # Match complete query.
        # ----------------------------------------------------

        if query in combined_text:

            results.append(movie)

            continue

        # ----------------------------------------------------
        # Match individual words.
        #
        # This makes searches such as:
        #
        # "toxic"
        # "toxic 2026"
        # "action toxic"
        #
        # more flexible.
        # ----------------------------------------------------

        if all(
            word in combined_text
            for word in query_words
        ):

            results.append(movie)

    return results


# ============================================================
# MOVIE HELPERS
# ============================================================

def get_movie_by_id(
    movie_id: str,
) -> dict[str, Any] | None:

    requested_id = str(
        movie_id
    ).strip()

    for movie in get_movies():

        current_id = str(
            movie.get("id", "")
        ).strip()

        if current_id == requested_id:

            return movie

    return None


# ============================================================
# CATEGORIES
# ============================================================

def get_categories(
    movies: list[dict[str, Any]],
) -> list[str]:

    categories: set[str] = set()

    for movie in movies:

        category_value = movie.get(
            "category"
        )

        if isinstance(
            category_value,
            str,
        ):

            category_value = (
                category_value.strip()
            )

            if category_value:

                categories.add(
                    category_value
                )

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

    categories = get_categories(
        movies
    )

    # --------------------------------------------------------
    # FEATURED
    # --------------------------------------------------------

    featured = None

    for movie in movies:

        if movie.get("featured") is True:

            featured = movie

            break

    if featured is None and movies:

        featured = movies[0]

    # --------------------------------------------------------
    # NEWEST
    # --------------------------------------------------------

    newest_movies = sorted(
        movies,
        key=lambda movie: str(
            movie.get(
                "added_date",
                "",
            )
        ),
        reverse=True,
    )

    # --------------------------------------------------------
    # POPULAR
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

        # Your current home.html supports this.
        featured=featured,

        # Also provide featured_movie for templates
        # that use that variable.
        featured_movie=featured,

        newest_movies=newest_movies[:12],

        popular_movies=popular_movies[:12],

        categories=categories,
    )


# ============================================================
# MOVIE DETAIL
#
# IMPORTANT:
# endpoint="movie"
#
# Your templates use:
#
# url_for('movie', movie_id=movie.id)
#
# So we explicitly name this endpoint "movie".
# ============================================================

@app.route(
    "/movie/<movie_id>",
    endpoint="movie",
)
def movie_detail(movie_id: str):

    movie = get_movie_by_id(
        movie_id
    )

    if movie is None:

        abort(404)

    # --------------------------------------------------------
    # SIMILAR MOVIES
    # --------------------------------------------------------

    current_category = normalize_text(
        movie.get("category")
    )

    similar_movies = []

    for item in get_movies():

        item_id = str(
            item.get("id", "")
        ).strip()

        if item_id == str(movie_id).strip():

            continue

        item_category = normalize_text(
            item.get("category")
        )

        if (
            current_category
            and item_category == current_category
        ):

            similar_movies.append(item)

    return render_template(
        "movie.html",

        movie=movie,

        similar_movies=similar_movies[:8],
    )


# ============================================================
# CATEGORY PAGE
# ============================================================

@app.route(
    "/category/<path:category_name>"
)
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

    # --------------------------------------------------------
    # Preserve original capitalization.
    # --------------------------------------------------------

    display_category = category_name

    for movie in movies:

        original_category = movie.get(
            "category"
        )

        if normalize_text(
            original_category
        ) == requested_category:

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
# SEARCH PAGE
# ============================================================

@app.route("/search")
def search():

    # --------------------------------------------------------
    # Read ?q=
    # --------------------------------------------------------

    query = request.args.get(
        "q",
        "",
    )

    query = query.strip()

    # Limit query length.
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
    # SEARCH
    # --------------------------------------------------------

    results = search_movies(
        movies,
        query,
    )

    print(
        f"[SEARCH] '{query}' -> "
        f"{len(results)} result(s)"
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
# 404 ERROR PAGE
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


# ============================================================
# 500 ERROR PAGE
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

        "site_name":
            "M1000",

        "site_tagline":
            "Movies. Series. Endless Entertainment.",

        "current_year":
            2026,

    }


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print(
        "M1000 — Yellow & Black Streaming UI"
    )

    print("=" * 60)

    print(
        f"Database: {MOVIES_FILE}"
    )

    print(
        f"Database exists: "
        f"{MOVIES_FILE.exists()}"
    )

    loaded_movies = get_movies()

    print(
        f"Movies loaded: "
        f"{len(loaded_movies)}"
    )

    print("=" * 60)

    print()

    # --------------------------------------------------------
    # PORT
    #
    # Heroku provides PORT automatically.
    # Local development falls back to 5000.
    # --------------------------------------------------------

    port = int(
        os.environ.get(
            "PORT",
            5000,
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )
```
