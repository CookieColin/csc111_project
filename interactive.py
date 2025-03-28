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
    length: int
    genre: str
    rating: float
    director: str
    lead_actors: List[str]
    votes: int

    def __init__(self, title: str, year: int, length: int, genre: str, rating: float,
                 director: str, lead_actors: List[str], votes: int) -> None:
        """Initialize a movie object."""
        self.title = title
        self.year = year
        self.length = length
        self.genre = genre
        self.rating = rating
        self.director = director
        self.lead_actors = lead_actors
        self.votes = votes

    def __hash__(self) -> int:
        return hash((self.title, self.year))


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
        self.watched_movies = watched_movies if watched_movies else set()


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
            with open(movies_file, 'r') as f:
                reader = csv.reader(f)
                _ = next(reader)
                for row in reader:
                    if len(row) != 16:
                        raise ValueError(f"Expected 16 columns in movies.csv, got{len(row)}")
                    _, title, year, _, length, genre, rating, _, _, director, actor1, actor2, \
                        actor3, actor4, votes, _ = row
                    if not year.strip().isdigit():
                        print(f"Skipping invalid row (year='{row[2]}'): {row[1]}")
                        continue
                    self.movies[title] = Movie(
                        title=title,
                        year=int(year),
                        length=int(str(length).replace("min", "")),
                        genre=genre,
                        rating=float(rating),
                        director=director,
                        lead_actors=[str(actor1), str(actor2), str(actor3), str(actor4)],
                        votes=int(votes)
                    )
            ratings = []
            with open(ratings_file, 'r') as f:
                reader = csv.reader(f)
                _ = next(reader)
                for row in reader:
                    if len(row) != 4:
                        raise ValueError(f"Expected 4 columns in ratings.csv, got{len(row)}")
                    user_id, movie_title, rating, _ = int(row[0]), str(row[1]), float(row[2]), row[3]
                    ratings.append((user_id, movie_title, rating))
                    if user_id not in self.users:
                        self.users[user_id] = User(user_id, set())
                    if movie_title in self.movies:
                        self.users[user_id].watched_movies.add(self.movies[movie_title])

            self.graph = user_movie_graph.build_user_movie_graph(ratings)

        except ValueError as val_err:

            print(f"Input error: {val_err}")

        except RuntimeError as rt_err:

            print(f"Runtime error: {rt_err}")

    def get_recommendations(self, current_user: Optional[User]) -> List[Tuple[Movie, float]]:
        """Return a list of tuples with personalized movie recommendations matched to their matching scores and sorted
        by descending order.

        Raises RuntimeError if no current user is set"""
        if not self.current_user:
            raise RuntimeError(f"No current user set")

        if not hasattr(current_user, 'user_id') or not hasattr(current_user, 'watched_movies'):
            raise ValueError("Invalid user object provided")

        current_id = current_user.user_id
        similar_users = user_movie_graph.find_similar_users(self.graph, str(current_id))
        movie_scores = {}

        for similar_user_id, similarity in similar_users:
            similar_users_id_int = int(similar_user_id)
            for movie in self.users[similar_users_id_int].watched_movies:
                if movie not in self.current_user.watched_movies:
                    movie_scores[movie] = movie_scores.get(movie, 0) + similarity * movie.rating

        user_genres = {m.genre for m in self.current_user.watched_movies}
        for movie in self.movies.values():
            if movie not in self.current_user.watched_movies:
                genre_bonus = 1.0 if movie.genre in user_genres else 0.3
                movie_scores[movie] = movie_scores.get(movie, 0) + movie.rating * genre_bonus

        return sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)[:10]

    def interactive_session(self) -> None:
        """Run an interactive recommendation session

        Handles user login, menu navigation, and recommendation display.
        """
        print("Movie Recommendation System")
        print("---------------------------")

        logged_in = False
        while not logged_in:
            user_input = input("Enter your user ID (or 'new' for new user): ").strip()

            if user_input.lower() == 'new':
                new_id = max(self.users.keys()) + 1
                self.users[new_id] = User(new_id, set())
                self.current_user = self.users[new_id]
                print(f"Created new user with ID: {new_id}")
                logged_in = True
            else:
                try:
                    user_id = int(user_input)
                    if user_id in self.users:
                        self.current_user = self.users[user_id]
                        logged_in = True
                    else:
                        print("User not found. Try again.")
                except ValueError:
                    print("Please enter a numeric user ID or 'new'")

        while logged_in:
            print("\nMain Menu:")
            print("1. Get recommendations")
            print("2. Add watched movie")
            print("3. Exit")
            choice = input("Choose an option (1-3): ").strip()

            if choice == '1':
                try:
                    print("\nRecommended Movies:")
                    recommendations = self.get_recommendations(self.current_user)
                    for i, (movie, score) in enumerate(recommendations, 1):
                        print(f"{i}. {movie.title} ({movie.year}) | Score: {score:.2f}")
                        print(f"   Genre: {movie.genre} | Rating: {movie.rating:.1f}")
                        print(f"   Director: {movie.director}")
                        print(f"   Stars: {', '.join(movie.lead_actors[:2])}...")
                except RuntimeError as runtime_err:
                    print(f"Error: {str(runtime_err)}")

            elif choice == '2':
                title = input("Enter movie title you've watched: ").strip()
                if title in self.movies:
                    self.current_user.watched_movies.add(self.movies[title])
                    print(f"Added {title} to your watched list!")
                else:
                    print("Movie not found. Available movies:")
                    for movie in list(self.movies.values())[:3]:
                        print(f"- {movie.title}")
                    print("... (truncated)")

            elif choice == '3':
                print("Thanks for using our system!")
                self.current_user = None
                logged_in = False
            else:
                print("Invalid choice. Please try 1-3.")


if __name__ == "__main__":
    recommender = MovieRecommender(movies={}, users={}, current_user=None)

    try:
        recommender.load_data("Movies.csv", "ratings.csv")
        recommender.interactive_session()
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
    except ValueError as e:
        print(f"Data error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
