"""Movie recommendation system using user-movie graph with NetworkX and Plotly."""

import csv
import networkx as nx
from plotly.graph_objs import Scatter, Figure


def load_user_movie_data(file_path: str = "ratings.csv") -> list[dict]:
    """Read user-movie rating data from a CSV file.

    Each row in the CSV should contain: User_ID, Movie_Title, Rating, Genre
    Returns a list of dictionaries.
    """
    movie_data = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                user_id = row[0]
                movie_title = row[1]
                rating = float(row[2])
                genre = row[3]
                movie_data.append({
                    "user": user_id,
                    "movie": movie_title,
                    "rating": rating,
                    "genre": genre
                })
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
    return movie_data


def build_user_movie_graph(user_movie_data: list[dict]) -> nx.Graph:
    """Construct a user-movie graph using networkx."""
    graph = nx.Graph()
    for entry in user_movie_data:
        user_id = entry["user"]
        movie_title = entry["movie"]
        rating = entry["rating"]
        genre = entry["genre"]

        if not graph.has_node(user_id):
            graph.add_node(user_id, type="user")
        if not graph.has_node(movie_title):
            graph.add_node(movie_title, type="movie", genre=genre)
        graph.add_edge(user_id, movie_title, weight=rating)
    return graph


def find_similar_users(graph: nx.Graph, target_user: str, top_n: int = 3) -> list[tuple[str, float]]:
    """Find top N users most similar to the target user using Jaccard similarity."""
    if target_user not in graph:
        return []
    target_movies = set(graph.neighbors(target_user))
    similarity_scores = []

    for node in graph.nodes:
        if graph.nodes[node].get("type") == "user" and node != target_user:
            other_movies = set(graph.neighbors(node))
            intersection = target_movies & other_movies
            union = target_movies | other_movies
            if not union:
                continue
            similarity = len(intersection) / len(union)
            if similarity > 0:
                similarity_scores.append((node, similarity))
    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    return similarity_scores[:top_n]


def recommend_movies(graph: nx.Graph, target_user: str, top_n: int = 3) -> list[tuple[str, float]]:
    """Recommend movies based on ratings from similar users."""
    similar_users = find_similar_users(graph, target_user)
    if not similar_users:
        return []

    target_movies = set(graph.neighbors(target_user))
    movie_scores = {}

    for user_id, similarity in similar_users:
        for movie_title in graph.neighbors(user_id):
            if graph.nodes[movie_title]["type"] != "movie" or movie_title in target_movies:
                continue
            rating = graph[user_id][movie_title]["weight"]
            if movie_title not in movie_scores:
                movie_scores[movie_title] = 0
            movie_scores[movie_title] += similarity * rating
    sorted_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_movies[:top_n]


def visualize_graph_plotly(graph: nx.Graph, target_user: str = None, output_file: str = "") -> None:
    """Visualize the user-movie graph using Plotly."""
    pos = nx.spring_layout(graph, seed=42)

    x_nodes = []
    y_nodes = []
    labels = []
    colors = []

    for node in graph.nodes:
        x, y = pos[node]
        x_nodes.append(x)
        y_nodes.append(y)
        labels.append(node)

        if node == target_user:
            colors.append("red")
        elif graph.nodes[node]["type"] == "user":
            colors.append("blue")
        else:
            colors.append("green")

    x_edges = []
    y_edges = []

    for u, v in graph.edges:
        x_edges += [pos[u][0], pos[v][0], None]
        y_edges += [pos[u][1], pos[v][1], None]

    edge_trace = Scatter(
        x=x_edges,
        y=y_edges,
        line={"width": 1, "color": "lightgray"},
        hoverinfo="none",
        mode="lines"
    )

    node_trace = Scatter(
        x=x_nodes,
        y=y_nodes,
        mode="markers",
        marker={
            "size": 10,
            "color": colors,
            "line": {"width": 1, "color": "black"}
        },
        text=labels,
        hoverinfo="text"
    )

    fig = Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="🎬 User-Movie Recommendation Graph",
        showlegend=False,
        xaxis={"showgrid": False, "zeroline": False, "visible": False},
        yaxis={"showgrid": False, "zeroline": False, "visible": False},
        margin={"t": 40, "l": 10, "r": 10, "b": 10}
    )

    if output_file:
        fig.write_html(output_file)
    else:
        fig.show()


if __name__ == "__main__":
    movie_data = load_user_movie_data("ratings.csv")
    user_graph = build_user_movie_graph(movie_data)

    print("✅ Graph built!")
    print("📊 Number of nodes:", user_graph.number_of_nodes())
    print("🔗 Number of edges:", user_graph.number_of_edges())

    target = input("🔍 Enter a user ID (e.g., 1): ").strip()
    similar_users = find_similar_users(user_graph, target)

    print(f"\n👥 Top similar users to {target}:")
    for user, score in similar_users:
        print(f"  {user} (similarity: {score:.2f})")

    recommendations = recommend_movies(user_graph, target)
    print(f"\n🎬 Recommended movies for {target}:")
    for movie, score in recommendations:
        print(f"  {movie} (score: {score:.2f})")

    visualize_graph_plotly(user_graph, target)

    import python_ta

    python_ta.check_all(config={
        "max-line-length": 100,
        "extra-imports": ["csv", "networkx", "plotly.graph_objs"],
        "allowed-io": ["load_user_movie_data", "print", "input", "visualize_graph_plotly"],
        "disable": ["E1101"]
    })