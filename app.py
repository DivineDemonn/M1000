# ============================================================
# M1000 — FLASK APPLICATION
# Premium Movie & Web Series Website
# Yellow + Black Cinematic Edition
#
# File: app.py
# ============================================================

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import (
    Flask,
    abort,
    render_template,
    request,
)


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
# CONSTANTS
# ============================================================

SITE_NAME = "M1000"

SITE_TAGLINE = (
    "Movies. Series. Endless Entertainment."
)

CURRENT_YEAR = datetime.now().year


# ============================================================
# DATA LOADING
# ============================================================

def load_movies() -> list[dict[str, Any]]:
    """
    Load movies from:

        data/movies.json

    Supported formats:

    FORMAT 1
    --------
    [
        {
            "id": "movie-001",
            "title": "Toxic"
        }
    ]

    FORMAT 2
    --------
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
            f"[ERROR] Invalid movies.json: {error}"
        )

        return []


    except OSError as error:

        print(
            f"[ERROR] Unable to read movies.json: {error}"
        )

        return []


    # --------------------------------------------------------
    # Detect JSON format
    # --------------------------------------------------------

    if isinstance(data, dict):

        movies = data.get(
            "movies",
            [],
        )

    elif isinstance(data, list):

        movies = data

    else:

        print(
            "[ERROR] movies.json must contain "
            "a list or an object containing 'movies'."
        )

        return []


    if not isinstance(movies, list):

        print(
            "[ERROR] 'movies' must be a list."
        )

        return []


    # --------------------------------------------------------
    # Keep dictionary entries only
    # --------------------------------------------------------

    valid_movies: list[dict[str, Any]] = []

    for movie in movies:

        if isinstance(movie, dict):

            valid_movies.append(movie)


    print(
        f"[INFO] Loaded {len(valid_movies)} movies."
    )

    return valid_movies


# ============================================================
# MOVIE DATABASE
# ============================================================

def get_movies() -> list[dict[str, Any]]:
    """
    Reload movies.json on every request.

    This is useful during development because
    editing movies.json does not require restarting Flask.
    """

    return load_movies()


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value: Any) -> str:
    """
    Convert any value into normalized lowercase text.

    Example:

        "  Tamil   New Movies "

    becomes:

        "tamil new movies"
    """

    if value is None:

        return ""


    if isinstance(value, list):

        return " ".join(
            normalize_text(item)
            for item in value
        )


    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


# ============================================================
# CATEGORY NORMALIZATION
# ============================================================

def normalize_category(value: Any) -> str:
    """
    Normalize category values.

    Supports:

        "Tamil New Movies"

    and also:

        ["Tamil New Movies"]

    and:

        " Tamil   New   Movies "
    """

    if value is None:

        return ""


    if isinstance(value, list):

        return " ".join(
            normalize_text(item)
            for item in value
        ).strip()


    return normalize_text(value)


# ============================================================
# GENRE SEARCH HELPER
# ============================================================

def searchable_genre(
    movie: dict[str, Any],
) -> str:
    """
    Supports genre as either:

        "Action, Thriller"

    or:

        ["Action", "Thriller"]
    """

    genre = movie.get(
        "genre",
        "",
    )


    if isinstance(genre, list):

        return " ".join(
            normalize_text(item)
            for item in genre
        )


    return normalize_text(genre)


# ============================================================
# IMAGE / MEDIA HELPERS
# ============================================================

def normalize_movie(movie: dict[str, Any]) -> dict[str, Any]:
    """
    Make movie data more tolerant of common JSON field names.

    Supported poster fields:

        poster
        poster_url
        image
        image_url
        poster_image

    Supported backdrop fields:

        backdrop
        backdrop_url
        backdrop_image
        background
        background_image

    The original data is preserved.
    """

    movie = dict(movie)


    # --------------------------------------------------------
    # POSTER
    # --------------------------------------------------------

    if not movie.get("poster"):

        poster_candidates = [
            movie.get("poster_url"),
            movie.get("image"),
            movie.get("image_url"),
            movie.get("poster_image"),
        ]

        for value in poster_candidates:

            if value:

                movie["poster"] = value

                break


    # --------------------------------------------------------
    # BACKDROP
    # --------------------------------------------------------

    if not movie.get("backdrop"):

        backdrop_candidates = [
            movie.get("backdrop_url"),
            movie.get("backdrop_image"),
            movie.get("background"),
            movie.get("background_image"),
        ]

        for value in backdrop_candidates:

            if value:

                movie["backdrop"] = value

                break


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    if not movie.get("title"):

        movie["title"] = (
            movie.get("name")
            or movie.get("movie_name")
            or "Untitled"
        )


    # --------------------------------------------------------
    # ID
    # --------------------------------------------------------

    if movie.get("id") is None:

        movie["id"] = (
            movie.get("slug")
            or movie.get("movie_id")
            or ""
        )


    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    if movie.get("category") is None:

        movie["category"] = ""


    return movie


# ============================================================
# PREPARE MOVIES
# ============================================================

def prepare_movies(
    movies: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Normalize every movie before sending it to templates.
    """

    prepared: list[dict[str, Any]] = []

    for movie in movies:

        if not isinstance(movie, dict):
            continue

        prepared.append(
            normalize_movie(movie)
        )

    return prepared


# ============================================================
# MOVIE LOOKUP
# ============================================================

def get_movie_by_id(
    movie_id: str,
) -> dict[str, Any] | None:

    requested_id = normalize_text(
        movie_id
    )


    if not requested_id:

        return None


    for movie in get_movies():

        movie = normalize_movie(movie)


        current_id = normalize_text(
            movie.get(
                "id",
                "",
            )
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
    """
    Return unique categories while preserving
    their original display names.

    Example:

        Tamil HD Movies
        Tamil New Movies
        Tamil Dubbed Movies
        Web Series
    """

    categories: dict[str, str] = {}


    for movie in movies:

        movie = normalize_movie(movie)


        category_value = movie.get(
            "category"
        )


        if isinstance(
            category_value,
            list,
        ):

            values = category_value

        else:

            values = [
                category_value
            ]


        for category in values:

            if category is None:
                continue


            display_category = str(
                category
            ).strip()


            if not display_category:
                continue


            normalized = normalize_category(
                display_category
            )


            if normalized not in categories:

                categories[
                    normalized
                ] = display_category


    return sorted(
        categories.values(),
        key=str.lower,
    )


# ============================================================
# FILTER BY CATEGORY
# ============================================================

def movies_by_category(
    movies: list[dict[str, Any]],
    category_name: str,
) -> list[dict[str, Any]]:

    requested_category = normalize_category(
        category_name
    )


    results: list[dict[str, Any]] = []


    for movie in movies:

        movie = normalize_movie(movie)


        movie_category = movie.get(
            "category",
            "",
        )


        # ----------------------------------------------------
        # Category can be a string
        # ----------------------------------------------------

        if isinstance(
            movie_category,
            str,
        ):

            if (
                normalize_category(
                    movie_category
                )
                == requested_category
            ):

                results.append(movie)


        # ----------------------------------------------------
        # Category can also be a list
        # ----------------------------------------------------

        elif isinstance(
            movie_category,
            list,
        ):

            normalized_categories = [
                normalize_category(item)
                for item in movie_category
            ]


            if requested_category in normalized_categories:

                results.append(movie)


    return results


# ============================================================
# FEATURED MOVIE
# ============================================================

def get_featured_movie(
    movies: list[dict[str, Any]],
) -> dict[str, Any] | None:

    # --------------------------------------------------------
    # First look for featured=true
    # --------------------------------------------------------

    for movie in movies:

        movie = normalize_movie(movie)


        featured_value = movie.get(
            "featured",
            False,
        )


        if (
            featured_value is True
            or normalize_text(
                featured_value
            ) in {
                "true",
                "yes",
                "1",
            }
        ):

            return movie


    # --------------------------------------------------------
    # Fallback to first movie
    # --------------------------------------------------------

    if movies:

        return normalize_movie(
            movies[0]
        )


    return None


# ============================================================
# SORT MOVIES BY DATE
# ============================================================

def sort_newest(
    movies: list[dict[str, Any]],
) -> list[dict[str, Any]]:

    return sorted(
        movies,
        key=lambda movie: str(
            movie.get(
                "added_date",
                ""
            )
        ),
        reverse=True,
    )


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    movies = prepare_movies(
        get_movies()
    )


    # --------------------------------------------------------
    # Categories
    # --------------------------------------------------------

    categories = get_categories(
        movies
    )


    # --------------------------------------------------------
    # Featured movie
    # --------------------------------------------------------

    featured = get_featured_movie(
        movies
    )


    # --------------------------------------------------------
    # Newest movies
    # --------------------------------------------------------

    newest_movies = sort_newest(
        movies
    )


    # --------------------------------------------------------
    # Popular movies
    # --------------------------------------------------------

    popular_movies = [

        movie

        for movie in movies

        if (
            movie.get("popular") is True
            or normalize_text(
                movie.get("popular")
            ) in {
                "true",
                "yes",
                "1",
            }
        )

    ]


    if not popular_movies:

        popular_movies = movies[:12]


    # --------------------------------------------------------
    # Individual homepage categories
    #
    # These are passed to home.html so the template does
    # not have to repeatedly filter the complete database.
    # --------------------------------------------------------

    tamil_hd_movies = movies_by_category(
        movies,
        "Tamil HD Movies",
    )


    tamil_new_movies = movies_by_category(
        movies,
        "Tamil New Movies",
    )


    tamil_dubbed_movies = movies_by_category(
        movies,
        "Tamil Dubbed Movies",
    )


    web_series = movies_by_category(
        movies,
        "Web Series",
    )


    print()
    print("[HOME]")
    print(
        f"Total movies: {len(movies)}"
    )
    print(
        f"Categories: {categories}"
    )
    print(
        f"Tamil HD Movies: "
        f"{len(tamil_hd_movies)}"
    )
    print(
        f"Tamil New Movies: "
        f"{len(tamil_new_movies)}"
    )
    print(
        f"Tamil Dubbed Movies: "
        f"{len(tamil_dubbed_movies)}"
    )
    print(
        f"Web Series: "
        f"{len(web_series)}"
    )
    print()


    return render_template(
        "home.html",

        # Main database
        movies=movies,

        # Featured
        featured=featured,
        featured_movie=featured,

        # Lists
        newest_movies=newest_movies[:12],
        popular_movies=popular_movies[:12],

        # Categories
        categories=categories,

        # Homepage category lists
        tamil_hd_movies=tamil_hd_movies[:6],
        tamil_new_movies=tamil_new_movies[:6],
        tamil_dubbed_movies=tamil_dubbed_movies[:6],
        web_series=web_series[:6],
    )


# ============================================================
# MOVIE DETAIL VIEW
# ============================================================

def movie_detail_view(
    movie_id: str,
):

    movie = get_movie_by_id(
        movie_id
    )


    if movie is None:

        abort(404)


    movies = prepare_movies(
        get_movies()
    )


    # --------------------------------------------------------
    # Similar movies
    # --------------------------------------------------------

    movie_category = normalize_category(
        movie.get(
            "category",
            "",
        )
    )


    similar_movies: list[
        dict[str, Any]
    ] = []


    for item in movies:

        item_id = normalize_text(
            item.get(
                "id",
                "",
            )
        )


        if item_id == normalize_text(
            movie_id
        ):

            continue


        item_category = normalize_category(
            item.get(
                "category",
                "",
            )
        )


        if (
            movie_category
            and item_category
            == movie_category
        ):

            similar_movies.append(
                item
            )


    return render_template(
        "movie.html",
        movie=movie,
        similar_movies=similar_movies[:8],
    )


# ============================================================
# MOVIE DETAIL ROUTES
# ============================================================
#
# Both endpoint names work:
#
#     url_for('movie_detail', movie_id=...)
#
# and:
#
#     url_for('movie', movie_id=...)
#
# This prevents BuildError problems if old templates
# still use endpoint "movie".
# ============================================================

app.add_url_rule(
    "/movie/<movie_id>",
    endpoint="movie_detail",
    view_func=movie_detail_view,
)

app.add_url_rule(
    "/movie/<movie_id>",
    endpoint="movie",
    view_func=movie_detail_view,
)


# ============================================================
# CATEGORY PAGE
# ============================================================

@app.route(
    "/category/<path:category_name>"
)
def category(category_name: str):

    movies = prepare_movies(
        get_movies()
    )


    requested_category = normalize_category(
        category_name
    )


    filtered_movies = movies_by_category(
        movies,
        category_name,
    )


    # --------------------------------------------------------
    # Find original category capitalization
    # --------------------------------------------------------

    display_category = category_name


    for movie in movies:

        original_category = movie.get(
            "category",
            "",
        )


        if isinstance(
            original_category,
            list,
        ):

            for category_value in original_category:

                if (
                    normalize_category(
                        category_value
                    )
                    == requested_category
                ):

                    display_category = str(
                        category_value
                    ).strip()

                    break

            else:

                continue

            break


        else:

            if (
                normalize_category(
                    original_category
                )
                == requested_category
            ):

                display_category = str(
                    original_category
                ).strip()

                break


    print(
        f"[CATEGORY] "
        f"{display_category}: "
        f"{len(filtered_movies)} movies"
    )


    return render_template(
        "category.html",
        movies=filtered_movies,
        category_name=display_category,
        categories=get_categories(movies),
    )


# ============================================================
# ALL MOVIES
# ============================================================

@app.route("/movies")
def all_movies():

    movies = prepare_movies(
        get_movies()
    )


    return render_template(
        "category.html",
        movies=movies,
        category_name="All Movies",
        categories=get_categories(movies),
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

    query = str(
        query
    ).strip()


    # Prevent excessively large search strings
    query = query[:100]


    movies = prepare_movies(
        get_movies()
    )


    # --------------------------------------------------------
    # Empty search
    # --------------------------------------------------------

    if not query:

        return render_template(
            "search.html",
            movies=[],
            query="",
        )


    search_text = normalize_text(
        query
    )


    results: list[
        dict[str, Any]
    ] = []


    search_words = search_text.split()


    # --------------------------------------------------------
    # Search every movie
    # --------------------------------------------------------

    for movie in movies:

        title = normalize_text(
            movie.get(
                "title",
                "",
            )
        )


        original_title = normalize_text(
            movie.get(
                "original_title",
                "",
            )
        )


        description = normalize_text(
            movie.get(
                "description",
                "",
            )
        )


        category_value = normalize_category(
            movie.get(
                "category",
                "",
            )
        )


        language = normalize_text(
            movie.get(
                "language",
                "",
            )
        )


        year = normalize_text(
            movie.get(
                "year",
                "",
            )
        )


        genre = searchable_genre(
            movie
        )


        movie_id = normalize_text(
            movie.get(
                "id",
                "",
            )
        )


        # ----------------------------------------------------
        # Additional searchable fields
        # ----------------------------------------------------

        director = normalize_text(
            movie.get(
                "director",
                "",
            )
        )


        cast = normalize_text(
            movie.get(
                "cast",
                "",
            )
        )


        # ----------------------------------------------------
        # Combine all searchable fields
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
                director,
                cast,
            ]
        )


        # ----------------------------------------------------
        # Direct search
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
        # matches a movie containing both words.
        # ----------------------------------------------------

        if search_words:

            if all(
                word in searchable_text
                for word in search_words
            ):

                results.append(movie)


    print(
        f"[SEARCH] "
        f"Query='{query}' "
        f"Results={len(results)}"
    )


    return render_template(
        "search.html",
        movies=results,
        query=query,
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
        "database": str(
            MOVIES_FILE
        ),
        "database_exists": MOVIES_FILE.exists(),
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
        "site_name": SITE_NAME,

        "site_tagline": SITE_TAGLINE,

        "current_year": CURRENT_YEAR,

        # Useful category names for templates
        "category_tamil_hd": "Tamil HD Movies",

        "category_tamil_new": "Tamil New Movies",

        "category_tamil_dubbed": "Tamil Dubbed Movies",

        "category_web_series": "Web Series",

        "category_all": "All Movies",
    }


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("M1000 — PREMIUM STREAMING WEBSITE")
    print("=" * 65)

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

    print(
        f"Categories: "
        f"{get_categories(loaded_movies)}"
    )

    print("=" * 65)
    print()


    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
