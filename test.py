from sentence_transformers import SentenceTransformer, util
import pandas as pd

# Sample Property Data
properties = pd.DataFrame({
    "Apartment Code": ["A00001", "A00002", "A00003", "A00004", "A00005"],
    "City": ["Tabuk", "Tabuk", "Riyadh", "Tabuk", "Jeddah"],
    "Bedrooms": [3, 3, 4, 5, 3],
    "Price": [330190, 376638, 410000, 310000, 350000],
    "Construction Status": ["Not started - selling on map", 
                            "Not started - selling on map", 
                            "Completed", 
                            "Not started - selling on map", 
                            "Under construction"]
})

# Concatenate property features into a single text description
properties['Description'] = properties.apply(
    lambda row: f"Property in {row['City']} with {row['Bedrooms']} bedrooms, price {row['Price']}, status: {row['Construction Status']}.", axis=1
)

# User Preferences
user_preference = "Looking for a property in Tabuk with 3+ bedrooms, price range 300000-400000, status: Not started."

# Load pre-trained embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Compute embeddings
property_embeddings = model.encode(properties['Description'].tolist(), convert_to_tensor=True)
user_embedding = model.encode(user_preference, convert_to_tensor=True)

# Compute cosine similarity
similarities = util.cos_sim(user_embedding, property_embeddings).squeeze(0).tolist()

# Add similarity scores to the properties DataFrame
properties['Similarity'] = similarities

# Sort properties by similarity
recommended_properties = properties.sort_values(by='Similarity', ascending=False)

# Display recommendations
print(recommended_properties[['Apartment Code', 'City', 'Bedrooms', 'Price', 'Similarity']])