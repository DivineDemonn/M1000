# ============================================================
# M1000 — FLASK APPLICATION
# Netflix-inspired Movie Website
# ============================================================

from flask import (
    Flask,
    render_template,
    request,
    abort,
)

from pathlib import Path
import json


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "data" / "movies.json"


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)


app.config.update(
    SECRET_KEY="m1000-change-this-secret-key",

    # Prevent unnecessary JSON caching while developing.
    JSON_SORT_KEYS=False,

    # Keep templates easier to update during development.
    TEMPLATES_AUTO_RELOAD=True,
)


# ============================================================
# DATA HELPERS
# ============================================================

def load_movies():
    """
    Load movie information from data/movies.json.

    Expected JSON structure:

    {
        "movies": [
            {
                "id": "movie-id",
                "title": "Movie Title",
                "year": 2026,
                "poster": "https://...",
                "backdrop": "https://...",
                "category": "Tamil HD Movies",
                "type": "Movie",
                "quality": ["720p", "480p"],
                "description": "..."
            }
        ]
    }
    """

    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return []

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        movies = data.get("movies", [])

        if isinstance(movies, list):
            return movies

    return []


def get_movie_by_id(movie_id):
    """
    Find one movie using its unique ID.
    """

    movies = load_movies()

    for movie in movies:

        if str(movie.get("id", "")) == str(movie_id):
            return movie

    return None


# ============================================================
# DATA NORMALIZATION
# ============================================================

def normalize_movie(movie):
    """
    Make sure templates always receive predictable values.
    """

    movie = dict(movie)

    movie.setdefault(
        "id",
        "",
    )

    movie.setdefault(
        "title",
        "Untitled",
    )

    movie.setdefault(
        "year",
        "",
    )

    movie.setdefault(
        "category",
        "Movies",
    )

    movie.setdefault(
        "type",
        "Movie",
    )

    movie.setdefault(
        "description",
        "No description available.",
    )

    movie.setdefault(
        "poster",
        "",
    )

    movie.setdefault(
        "backdrop",
        movie.get("poster", ""),
    )

    movie.setdefault(
        "quality",
        [],
    )

    movie.setdefault(
        "screenshots",
        [],
    )

    movie.setdefault(
        "downloads",
        [],
    )

    return movie


def normalized_movies():
    """
    Return all movies in a template-safe format.
    """

    return [
        normalize_movie(movie)
        for movie in load_movies()
    ]


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    """
    M1000 homepage.
    """

    movies = normalized_movies()

    featured = movies[:1]

    latest = movies[:12]

    tamil_hd = [
        movie
        for movie in movies
        if movie.get("category") == "Tamil HD Movies"
    ][:12]

    new_movies = [
        movie
        for movie in movies
        if movie.get("category") == "Tamil New Movies"
    ][:12]

    dubbed = [
        movie
        for movie in movies
        if movie.get("category") == "Tamil Dubbed Movies"
    ][:12]

    web_series = [
        movie
        for movie in movies
        if movie.get("category") == "Web Series"
    ][:12]

    return render_template(
        "home.html",

        movies=movies,

        featured=featured,

        latest=latest,

        tamil_hd=tamil_hd,

        new_movies=new_movies,

        dubbed=dubbed,

        web_series=web_series,
    )


# ============================================================
# MOVIE DETAIL
# ============================================================

@app.route("/movie/<movie_id>")
def movie_detail(movie_id):
    """
    Display an individual movie/series page.
    """

    movie = get_movie_by_id(movie_id)

    if movie is None:
        abort(404)

    movie = normalize_movie(movie)

    return render_template(
        "movie.html",
        movie=movie,
    )


# ============================================================
# CATEGORY
# ============================================================

@app.route("/category/<path:category_name>")
def category(category_name):
    """
    Display movies belonging to a category.

    Example:

    /category/Tamil%20HD%20Movies
    """

    movies = [
        movie
        for movie in normalized_movies()
        if str(
            movie.get("category", "")
        ).casefold()
        == category_name.casefold()
    ]

    return render_template(
        "category.html",

        movies=movies,

        category_name=category_name,
    )


# ============================================================
# SEARCH
# ============================================================

@app.route("/search")
def search():
    """
    Search movies by title, category,
    year, genre, or description.
    """

    query = request.args.get(
        "q",
        "",
        type=str,
    ).strip()

    results = []

    if query:

        search_text = query.casefold()

        for movie in normalized_movies():

            searchable = " ".join(
                [
                    str(movie.get("title", "")),
                    str(movie.get("category", "")),
                    str(movie.get("genre", "")),
                    str(movie.get("year", "")),
                    str(movie.get("description", "")),
                ]
            ).casefold()

            if search_text in searchable:
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
def movies():
    """
    Display the complete movie catalogue.
    """

    all_movies = normalized_movies()

    return render_template(
        "category.html",

        movies=all_movies,

        category_name="All Movies",
    )


# ============================================================
# LEGAL PAGES
# ============================================================

@app.route("/about")
def about():

    return render_template(
        "legal.html",
        page_title="About M1000",
    )


@app.route("/privacy")
def privacy():

    return render_template(
        "legal.html",
        page_title="Privacy Policy",
    )


@app.route("/terms")
def terms():

    return render_template(
        "legal.html",
        page_title="Terms & Conditions",
    )


@app.route("/dmca")
def dmca():

    return render_template(
        "legal.html",
        page_title="Copyright / DMCA",
    )


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(500)
def internal_server_error(error):

    return render_template(
        "500.html"
    ), 500


# ============================================================
# TEMPLATE GLOBALS
# ============================================================

@app.context_processor
def inject_globals():
    """
    Variables available inside every template.
    """

    return {
        "site_name": "M1000",

        "site_description":
            "Discover movies and web series on M1000.",

        "current_year":
            __import__("datetime")
            .datetime
            .now()
            .year,
    }


# ============================================================
# DEVELOPMENT SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
