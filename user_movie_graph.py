import csv
import networkx as nx
from plotly.graph_objs import Scatter, Figure   


def load_user_movie_data(file_path="user_movie_ratings.csv"):
    """Read user-movie rating data from a CSV file.
    Each row in the CSV should contain: User_ID, Movie_Title, Rating, Genre
    Returns a list of dictionaries.
    """
    data = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                user = row[0]
                movie = row[1]
                rating = float(row[2])
                genre = row[3]
                data.append({
                    "user": user,
                    "movie": movie,
                    "rating": rating,
                    "genre": genre
                })
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
    return data

def build_user_movie_graph(user_movie_data):
    """Construct a user-movie graph using networkx."""
    G = nx.Graph()
    for entry in user_movie_data:
        user = entry["user"]
        movie = entry["movie"]
        rating = entry["rating"]
        genre = entry["genre"]
        if not G.has_node(user):
            G.add_node(user, type="user")
        if not G.has_node(movie):
            G.add_node(movie, type="movie", genre=genre)
        G.add_edge(user, movie, weight=rating)
    return G

def find_similar_users(G, target_user, top_n=3):
    """Find top N users most similar to the target user using Jaccard similarity."""
    if target_user not in G:
        print(f"User '{target_user}' not found in the graph.")
        return []
    target_movies = set(G.neighbors(target_user))
    similarity_scores = []
    for node in G.nodes:
        if G.nodes[node].get("type") == "user" and node != target_user:
            other_movies = set(G.neighbors(node))
            intersection = target_movies & other_movies
            union = target_movies | other_movies
            if not union:
                continue
            similarity = len(intersection) / len(union)
            if similarity > 0:
                similarity_scores.append((node, similarity))
    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    return similarity_scores[:top_n]

def recommend_movies(G, target_user, top_n=3):
    """Recommend movies based on ratings from similar users."""
    similar_users = find_similar_users(G, target_user)
    if not similar_users:
        return []
    target_movies = set(G.neighbors(target_user))
    movie_scores = {}
    for user, similarity in similar_users:
        for movie in G.neighbors(user):
            if G.nodes[movie]["type"] != "movie" or movie in target_movies:
                continue
            rating = G[user][movie]["weight"]
            if movie not in movie_scores:
                movie_scores[movie] = 0
            movie_scores[movie] += similarity * rating
    sorted_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_movies[:top_n]
def visualize_graph_plotly(G: nx.Graph, target_user=None, output_file=''):
    pos = nx.spring_layout(G, seed=42)

    x_nodes = []
    y_nodes = []
    labels = []
    colors = []

    for node in G.nodes:
        x, y = pos[node]
        x_nodes.append(x)
        y_nodes.append(y)
        labels.append(node)

        if node == target_user:
            colors.append('red')
        elif G.nodes[node]['type'] == 'user':
            colors.append('blue')
        else:
            colors.append('green')

    x_edges = []
    y_edges = []

    for u, v in G.edges:
        x_edges += [pos[u][0], pos[v][0], None]
        y_edges += [pos[u][1], pos[v][1], None]

    edge_trace = Scatter(
        x=x_edges,
        y=y_edges,
        line=dict(width=1, color='lightgray'),
        hoverinfo='none',
        mode='lines'
    )

    node_trace = Scatter(
        x=x_nodes,
        y=y_nodes,
        mode='markers',
        marker=dict(
            size=10,
            color=colors,
            line=dict(width=1, color='black')
        ),
        text=labels,
        hoverinfo='text'
    )

    fig = Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title='🎬 User-Movie Recommendation Graph',
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        margin=dict(t=40, l=10, r=10, b=10)
    )

    if output_file:
        fig.write_html(output_file)
        print(f"📄 Saved plot as {output_file}")
    else:
        fig.show()

if __name__ == "__main__":
    data = load_user_movie_data("user_movie_ratings.csv")
    G = build_user_movie_graph(data)

    print("✅ Graph built!")
    print("📊 Number of nodes:", G.number_of_nodes())
    print("🔗 Number of edges:", G.number_of_edges())

    target_user = input("🔍 Enter a user ID (e.g., 1): ").strip()
    similar = find_similar_users(G, target_user)
    print(f"\n👥 Top similar users to {target_user}:")
    for user, score in similar:
        print(f"  {user} (similarity: {score:.2f})")

    recommendations = recommend_movies(G, target_user)
    print(f"\n🎬 Recommended movies for {target_user}:")
    for movie, score in recommendations:
        print(f"  {movie} (score: {score:.2f})")
        
visualize_graph_plotly(G, target_user)     


