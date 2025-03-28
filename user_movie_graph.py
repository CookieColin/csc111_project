import csv
import networkx as nx

def load_user_movie_data(file_path="data/user_movie_ratings.csv"):
    """   Read user-movie rating data from a CSV file.
    Each row in the CSV should contain: User_ID, Movie_Title, Rating, Genre

    Returns:
        A list of dictionaries, each with the keys:
        - 'user': User ID
        - 'movie': Movie title
        - 'rating': Numeric rating (float)
        - 'genre': Movie genre"""
    data = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row

            for row in reader:
                user = row[0]  # User ID
                movie = row[1]  # Movie title
                rating = float(row[2])  # Movie rating (convert to float)
                genre = row[3]  # Movie genre (e.g. Action, Drama)

                # Store each row as a dictionary
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
    """
    Construct a user-movie graph using networkx.

    Nodes:
        - Users (type="user")
        - Movies (type="movie", genre=movie genre)

    Edges:
        - Between user and movie
        - Edge attribute 'weight' is the user's rating for the movie

    Returns:
        networkx.Graph object
    """
    G = nx.Graph()  # Step 1: Initialize empty graph

    for entry in user_movie_data:
        user = entry["user"]
        movie = entry["movie"]
        rating = entry["rating"]
        genre = entry["genre"]

        # Step 2: Add user node (if not already present)
        if not G.has_node(user):
            G.add_node(user, type="user")

        # Step 3: Add movie node (with genre attribute)
        if not G.has_node(movie):
            G.add_node(movie, type="movie", genre=genre)

        # Step 4: Add edge between user and movie with rating as weight
        G.add_edge(user, movie, weight=rating)

    return G  # Step 5: Return the complete graph

def find_similar_users(G, target_user, top_n=3):
    """
    Find the top N users most similar to the target user,
    based on overlap in watched movies (Jaccard similarity).

    Parameters:
        G (nx.Graph): The user-movie graph
        target_user (str): The user to compare others against
        top_n (int): Number of similar users to return

    Returns:
        List of (user_id, similarity_score) tuples
    """
    if target_user not in G:
        print(f"User '{target_user}' not found in the graph.")
        return []

    # Step 1: Get movies the target user has watched
    target_movies = set(G.neighbors(target_user))

    similarity_scores = []

    # Step 2: Loop through all other user nodes
    for node in G.nodes:
        # Check if the node is a user and not the target user
        if G.nodes[node].get("type") == "user" and node != target_user:
            other_movies = set(G.neighbors(node))

            # Step 3: Compute similarity
            intersection = target_movies & other_movies
            union = target_movies | other_movies
            if not union:  # Avoid division by zero
                continue
            similarity = len(intersection) / len(union)

            # Step 4: Add to list if similarity > 0
            if similarity > 0:
                similarity_scores.append((node, similarity))

    # Step 5: Sort by similarity (highest first)
    similarity_scores.sort(key=lambda x: x[1], reverse=True)

    return similarity_scores[:top_n]

def recommend_movies(G, target_user, top_n=3):
    """
    Recommend movies to the target user based on ratings from similar users.
    The scoring uses: similarity × rating

    Parameters:
        G (nx.Graph): The user-movie graph
        target_user (str): The user to make recommendations for
        top_n (int): Number of movie recommendations to return

    Returns:
        List of (movie_title, score) tuples
    """
    # Step 1: Get similar users
    similar_users = find_similar_users(G, target_user)

    if not similar_users:
        return []

    # Step 2: Get movies the target user has already seen
    target_movies = set(G.neighbors(target_user))

    # Step 3: Dictionary to store recommended movie scores
    movie_scores = {}

    for user, similarity in similar_users:
        for movie in G.neighbors(user):
            # Only consider movie nodes the target user hasn't seen
            if G.nodes[movie]["type"] != "movie" or movie in target_movies:
                continue

            # Get the rating this user gave to the movie
            rating = G[user][movie]["weight"]

            # Calculate score = similarity * rating
            if movie not in movie_scores:
                movie_scores[movie] = 0
            movie_scores[movie] += similarity * rating

    # Step 4: Sort and return top N recommended movies
    sorted_movies = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_movies[:top_n]


if __name__ == "__main__":
    # 1. Load user-movie rating data
    data = load_user_movie_data("data/user_movie_ratings.csv")

    # 2. Build user-movie graph
    G = build_user_movie_graph(data)

    print("✅ Graph built!")
    print("📊 Number of nodes:", G.number_of_nodes())
    print("🔗 Number of edges:", G.number_of_edges())

    # 3. Select a target user
    target_user = "U1"  # Or use input("Enter target user ID: ")

    # 4. Find similar users
    similar = find_similar_users(G, target_user)
    print(f"\n👥 Top similar users to {target_user}:")
    for user, score in similar:
        print(f"  {user} (similarity: {score:.2f})")

    # 5. Recommend movies
    recommendations = recommend_movies(G, target_user)
    print(f"\n🎬 Recommended movies for {target_user}:")
    for movie, score in recommendations:
        print(f"  {movie} (score: {score:.2f})")

