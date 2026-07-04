from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict

class RecommendationEngine:
    """
    Content-based recommendation engine using TF-IDF and cosine similarity.
    Recommends products based on similarity in name, category, and description.
    """
    
    def __init__(self, products: List[Dict]):
        """
        Initialize the recommendation engine with product data.
        
        Args:
            products: List of product dictionaries with keys: id, name, category, description
        """
        self.products = products
        self.product_ids = [p['id'] for p in products]
        
        # Combine product features into a single text field for TF-IDF
        # This creates a rich representation of each product
        self.product_texts = [
            f"{p['name']} {p['category']} {p['description']}"
            for p in products
        ]
        
        # Initialize TF-IDF Vectorizer
        # TF-IDF converts text into numerical vectors based on term frequency
        # and inverse document frequency, giving more weight to distinctive terms
        self.vectorizer = TfidfVectorizer(
            stop_words='english',  # Remove common words like 'the', 'is', etc.
            max_features=500,       # Limit to top 500 features to reduce dimensionality
            ngram_range=(1, 2)      # Use both single words and two-word phrases
        )
        
        # Transform product texts into TF-IDF vectors
        self.tfidf_matrix = self.vectorizer.fit_transform(self.product_texts)
        
        # Calculate cosine similarity between all products
        # Cosine similarity measures the angle between vectors (0 = different, 1 = identical)
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
    
    def get_recommendations(self, product_id: str, num_recommendations: int = 4) -> List[Dict]:
        """
        Get product recommendations based on content similarity.
        
        Args:
            product_id: ID of the product to find recommendations for
            num_recommendations: Number of recommendations to return
            
        Returns:
            List of recommended products with similarity scores
        """
        # Find the index of the product in our product list
        try:
            product_idx = self.product_ids.index(product_id)
        except ValueError:
            return []  # Product not found
        
        # Get similarity scores for this product with all other products
        similarity_scores = list(enumerate(self.similarity_matrix[product_idx]))
        
        # Sort products by similarity score (highest first)
        # Skip the first item (the product itself, which has similarity = 1.0)
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:]
        
        # Get top N recommendations
        top_recommendations = similarity_scores[:num_recommendations]
        
        # Build response with product details and similarity scores
        recommendations = []
        for idx, score in top_recommendations:
            product = self.products[idx].copy()
            product['similarity_score'] = float(score)  # Convert numpy float to Python float
            recommendations.append(product)
        
        return recommendations
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """
        Get all products in a specific category.
        
        Args:
            category: Category name to filter by
            
        Returns:
            List of products in the specified category
        """
        return [p for p in self.products if p['category'].lower() == category.lower()]