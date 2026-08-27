```python
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from flask import Flask, abort, render_template, request


# ============================================================
# CONFIGURATION
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
# LOAD MOVIES
# ============================================================

def load_movies() -> list[dict[str, Any]]:
    """Load movie data from data/movies.json."""

    if not MOVIES_FILE.exists():
        print(f"[ERROR] File not found: {MOVIES_FILE}")
        return []

    try:
        with MOVIES_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError as error:
        print(f"[ERROR] Invalid JSON: {error}")
        return []

    except OSError as error:
        print(f"[ERROR] Cannot read movies.json: {error}")
        return []

    # Support:
    #
    # [
    #   {...}
    # ]
    #
    # and:
    #
    # {
    #   "movies": [...]
    # }

    if isinstance(data, list):
        movies = data

    elif isinstance(data, dict):
        movies = data.get("movies", [])

    else:
        print("[ERROR] movies.json must contain a list or object.")
        return []

    if not isinstance(movies, list):
        print("[ERROR] 'movies' must be a list.")
        return []

    valid_movies = []

    for movie in movies:
        if isinstance(movie, dict):
            if movie.get("id"):
                valid_movies.append(movie)

    return valid_movies


def get_movies() -> list[dict[str, Any]]:
    """Return the latest movie database."""
    return load_movies()


# ============================================================
# TEXT HELPERS
# ============================================================

def normalize_text(value: Any) -> str:
    """Normalize text for reliable searching."""

    if value is None:
        return ""

    text = str(value).lower().strip()

    # Keep English and Tamil characters.
    text = re.sub(
        r"[^a-z0-9\u0B80-\u0BFF]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def searchable_value(value: Any) -> str:
    """Convert strings/lists/dicts into searchable text."""

    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(
            searchable_value(item)
            for item in value
        )

    if isinstance(value, dict):
        return " ".join(
            searchable_value(item)
            for item in value.values()
        )

    return normalize_text(value)


# ============================================================
# SEARCH
# ============================================================

def search_movies(
    movies: list[dict[str, Any]],
    query: str,
) -> list[dict[str, Any]]:

    query = normalize_text(query)

    if not query:
        return []

    words = query.split()

    results = []

    for movie in movies:

        fields = [
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

        combined = " ".join(
            searchable_value(value)
            for value in fields
        )

        # Full query match.
        if query in combined:
            results.append(movie)
            continue

        # Individual word match.
        if all(word in combined for word in words):
            results.append(movie)

    return results


# ============================================================
# MOVIE HELPERS
# ============================================================

def get_movie_by_id(
    movie_id: str,
) -> dict[str, Any] | None:

    requested_id = str(movie_id).strip()

    for movie in get_movies():

        current_id = str(
            movie.get("id", "")
        ).strip()

        if current_id == requested_id:
            return movie

    return None


def get_categories(
    movies: list[dict[str, Any]],
) -> list[str]:

    categories = set()

    for movie in movies:

        category_name = movie.get("category")

        if isinstance(category_name, str):

            category_name = category_name.strip()

            if category_name:
                categories.add(category_name)

    return sorted(
        categories,
        key=str.lower,
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    movies = get_movies()

    categories = get_categories(movies)

    # --------------------------------------------------------
    # Featured
    # --------------------------------------------------------

    featured = None

    for movie in movies:

        if movie.get("featured") is True:

            featured = movie
            break

    if featured is None and movies:
        featured = movies[0]

    # --------------------------------------------------------
    # Newest
    # --------------------------------------------------------

    newest_movies = sorted(
        movies,
        key=lambda movie: str(
            movie.get("added_date", "")
        ),
        reverse=True,
    )

    # --------------------------------------------------------
    # Popular
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
        featured=featured,
        featured_movie=featured,
        newest_movies=newest_movies[:12],
        popular_movies=popular_movies[:12],
        categories=categories,
    )


# ============================================================
# MOVIE DETAIL
# ============================================================

@app.route(
    "/movie/<movie_id>",
    endpoint="movie",
)
def movie_detail(movie_id: str):

    movie = get_movie_by_id(movie_id)

    if movie is None:
        abort(404)

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
# CATEGORY
# ============================================================

@app.route(
    "/category/<path:category_name>"
)
def category(category_name: str):

    movies = get_movies()

    requested = normalize_text(
        category_name
    )

    filtered_movies = [
        movie
        for movie in movies
        if normalize_text(
            movie.get("category")
        ) == requested
    ]

    display_name = category_name

    for movie in movies:

        original = movie.get("category")

        if normalize_text(original) == requested:

            display_name = str(original)
            break

    return render_template(
        "category.html",
        movies=filtered_movies,
        category_name=display_name,
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

    query = query[:100]

    movies = get_movies()

    if not query:

        return render_template(
            "search.html",
            movies=[],
            query="",
        )

    results = search_movies(
        movies,
        query,
    )

    print(
        f"[SEARCH] {query!r} -> "
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
# 404
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


# ============================================================
# 500
# ============================================================

@app.errorhandler(500)
def internal_server_error(error):

    return render_template(
        "404.html"
    ), 500


# ============================================================
# GLOBAL TEMPLATE VARIABLES
# ============================================================

@app.context_processor
def inject_globals():

    return {
        "site_name": "M1000",
        "site_tagline": (
            "Movies. Series. Endless Entertainment."
        ),
        "current_year": 2026,
    }


# ============================================================
# START SERVER
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
