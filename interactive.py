"""The user interactive system for movie recommendations."""
from __future__ import annotations
import csv
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
import user_movie_graph


class _Vertex:
    """A vertex in a graph.

    Instance Attributes:
        - item: The data stored in this vertex.
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """
    item: Any
    neighbours: set[_Vertex]

    def __init__(self, item: Any, neighbours: set[_Vertex]) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.item = item
        self.neighbours = neighbours


class Graph:
    """A graph.

    Representation Invariants:
        - all(item == self._vertices[item].item for item in self._vertices)
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}


@dataclass
class Movie:
    """Represents a Movie in the movie recommendation system.

    Instance Attributes:
      - title: The title of a movie.
      - year: The release year of the movie.
      - certificate: The certificate of the movie.
      - length: The length of the movie in minutes.
      - genre: The genre of the movie.
      - rating: IMDb user rating of the movie.
      - meta_score: The weighted average given to movies.
      - director: The movie director's full name.
      - lead_actors: A list of the main actors' names.
      - votes: The number of votes that the movie got.
      - gross: The gross revenue of the movie.
    """
    title: str
    year: int
    certificate: str
    length: int
    genre: str
    rating: float
    meta_score: float
    director: str
    lead_actors: list[str]
    votes: int
    gross: int

    def __init__(self, title: str, year: int, certificate: str, length: int, genre: str, rating: float,
                 meta_score: float, director: str, lead_actors: list[str], votes: int, gross: int) -> None:
        """Initialize a movie object."""
        self.title = title
        self.year = year
        self.certificate = certificate
        self.length = length
        self.genre = genre
        self.rating = rating
        self.meta_score = meta_score
        self.director = director
        self.lead_actors = lead_actors
        self.votes = votes
        self.gross = gross


@dataclass
class User:
    """Represents a user with their preferences.

    Instance Attributes:
      - user_id: The id of the user
      - watched_movies: A set of movies that the user had watched
    """
    user_id: int
    watched_movies: Set[Movie]

    def __init__(self, user_id, watched_movies: Set[Movie]) -> None:
        """Initialize a user object."""
        self.user_id = user_id
        self.watched_movies = watched_movies


class MovieRecommender:
    """A hybrid movie recommendation system combining collaborative and content-based filtering.

    Instance Attributes:
      - movies: A dictionary mapping movie titles to movie objects.
      - users: A dictionary mapping user_ids to user objects.
      - current_user: The currently active user (None if no user logged in).
    """
    movies: Dict[str, Movie]
    users: Dict[int, User]
    current_user: Optional[User]
    graph: Optional[Graph]

    def __init__(self, movies: Dict[str, Movie], users: Dict[int, User], current_user: Optional[User]) -> None:
        """Initalize the movie recommender system with existing data."""
        self.movies = movies
        self.users = users
        self.current_user = current_user
        self.graph = None

    def load_data(self, movies_file: str, ratings_file: str) -> None:
        """Load movie and rating datas from csv files.

        Raise FileNotFound Error if either input file don't exist and ValueError if csv data is malformed.
        """
        try:
            with open(movies_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    if len(row) != 16:
                        raise ValueError(f"Expected 16 columns in movies.csv, got{len(row)}")
                    _, title, year, certificate, length, genre, rating, _, meta_score, director, actor1, actor2, \
                        actor3, actor4, votes, gross = row
                    self.movies[title] = Movie(title=title, year=int(year), certificate=str(certificate),
                                               length=int(length), genre=genre, rating=float(rating),
                                               meta_score=int(meta_score), director=director, lead_actors=[str(actor1),
                                               str(actor2), str(actor3), str(actor4)], votes=int(votes),
                                               gross=int(gross))

            ratings = []
            with open(ratings_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    if len != 2:
                        raise ValueError(f"Expected 2 columns in ratings.csv, got{len(row)}")
                    user_id, movie_title = int(row[0]), row[1]
                    ratings.append((user_id, movie_title, float(row[2])))
                    if user_id not in self.users:
                        self.users[user_id] = User(user_id, set())
                    if movie_title in self.movies:
                        self.users[user_id].watched_movies.add(self.movies[movie_title])

            self.graph = user_movie_graph.build_user_movie_graph(ratings)

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Missing file: {e.filename}")
        except ValueError as e:
            raise ValueError(f"Invalid data: {str(e)}")
