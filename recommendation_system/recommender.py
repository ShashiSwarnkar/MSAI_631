import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sys

def load_data(filepath):
    """
    Loads the movie data from the CSV file.
    """
    try:
        movies = pd.read_csv(filepath)
        print("✔ Movie data loaded successfully.")
        return movies
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while loading the data: {e}")
        sys.exit(1)

def build_tfidf_matrix(movies_df):
    """
    Builds and returns the TF-IDF vectorizer and matrix.
    This is memory-efficient as it ONLY builds the TF-IDF matrix (features).
    """
    # Replace '|' with a space and fill missing genres
    movies_df['genres'] = movies_df['genres'].str.replace('|', ' ', regex=False)
    movies_df['genres'] = movies_df['genres'].fillna('')

    # Initialize the TF-IDF Vectorizer
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')

    # Fit and transform the 'genres' data
    tfidf_matrix = tfidf_vectorizer.fit_transform(movies_df['genres'])
    
    print("✔ TF-IDF matrix built successfully.")
    return tfidf_matrix, tfidf_vectorizer

def get_recommendations(title, movies_df, tfidf_matrix, indices):
    """
    Calculates similarity ON THE FLY for only the requested movie.
    This avoids the MemoryError.
    """
    try:
        # Get the index of the movie that matches the title
        idx = indices[title]

        # Get the TF-IDF vector for *only* the movie we care about
        movie_vector = tfidf_matrix[idx]

        # Calculate the cosine similarity between THIS movie and ALL other movies
        sim_scores = cosine_similarity(movie_vector, tfidf_matrix)

        # sim_scores is a 2D array, so we grab the first (and only) row
        sim_scores = list(enumerate(sim_scores[0]))

        # Sort the movies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the scores of the 10 most similar movies (skip index 0, it's the movie itself)
        sim_scores = sim_scores[1:11]

        # Get the movie indices
        movie_indices = [i[0] for i in sim_scores]

        # Return the titles
        return movies_df['title'].iloc[movie_indices]
        
    except KeyError:
        # This is a fallback, but our new main() should prevent this.
        return None

def main():
    """
    The main function to run the program.
    
    *** This function is now more robust ***
    It performs a case-insensitive search and helps the user
    pick a movie if their query is ambiguous.
    """
    # Load the data
    movies = load_data('recommendation_system\movies.csv')
    
    # Build the TF-IDF matrix (this is fast)
    tfidf_matrix, vectorizer = build_tfidf_matrix(movies)
    
    # Create a helper Series to map movie titles to their index
    indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()
    
    print("\n--- Movie Recommendation System ---")
    print("This system uses Content-Based Filtering based on movie genres.")
    print("Type 'exit' at any time to quit.")
    
    while True:
        print("\n-------------------------------------")
        # Ask for a search term, not an exact title
        search_term = input("Enter a movie title (e.g., 'Toy Story'): ")

        if search_term.lower() == 'exit':
            print("Thank you for using the recommender. Goodbye!")
            break
        
        # --- NEW ROBUST SEARCH LOGIC ---
        
        # 1. Perform a case-insensitive search for the user's term
        # .str.contains() finds the substring
        # na=False prevents errors on empty rows
        matches = movies[movies['title'].str.contains(search_term, case=False, na=False)]
        
        exact_title = None
        
        # 2. Handle the (3) possible outcomes
        
        if matches.empty:
            # --- Outcome 1: No Matches ---
            print(f"Movie not found: '{search_term}'")
            print("Please try a different search term.")
            continue # Go back to the start of the 'while' loop
            
        elif len(matches) == 1:
            # --- Outcome 2: Exactly One Match ---
            # This is the ideal case. We found it.
            exact_title = matches.iloc[0]['title']
            print(f"Found: '{exact_title}'. Getting recommendations...")
        
        else:
            # --- Outcome 3: Multiple Matches ---
            # This is your 'toy story' scenario. We ask the user to clarify.
            print(f"Found {len(matches)} matches. Please select one:")
            matches_list = list(matches['title'])
            
            # Print a numbered list for the user
            for i, title in enumerate(matches_list):
                print(f"  {i+1}. {title}")
            
            try:
                # Ask the user for their choice
                choice_str = input(f"Enter a number (1-{len(matches_list)}) or 'c' to cancel: ")
                
                if choice_str.lower() == 'c':
                    continue # Cancel and go back to the start
                
                choice_idx = int(choice_str) - 1 # Convert 1-based to 0-based
                
                # Check if the choice is valid
                if 0 <= choice_idx < len(matches_list):
                    exact_title = matches_list[choice_idx]
                else:
                    print("Invalid number. Please try again.")
                    continue
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

        # --- END OF NEW LOGIC ---
        
        # 3. If we have a valid 'exact_title', get recommendations
        if exact_title:
            recommendations = get_recommendations(exact_title, movies, tfidf_matrix, indices)
            
            if recommendations is None:
                # This should not happen now, but it's good practice to check
                print(f"Error: Could not get recommendations for '{exact_title}'.")
            else:
                print(f"\nRecommendations based on '{exact_title}':")
                for i, rec_title in enumerate(recommendations):
                    print(f"  {i+1}. {rec_title}")

if __name__ == "__main__":
    main()