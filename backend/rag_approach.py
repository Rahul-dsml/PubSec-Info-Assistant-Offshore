import streamlit as st
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import json

# Load Embedding Model
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def generating_project_level_table():
    df = pd.read_csv(r"C:\Users\rahul\Desktop\Offshore\PubSec-Info-Assistant-Offshore\PubSec-Info-Assistant-Offshore-1\backend\df_english_v2.csv")
    # Define aggregation functions for each column
    agg_dict = {
        'Apartment_code': 'size',  # Count the number of apartments
        'allow_payment_by_cash': 'max',  # Check if cash payment is allowed
        'allow_payment_by_loan': 'max',  # Check if loan payment is allowed
        'publish_date': 'first',  # Use the first publish date (can modify if needed)
        'Construction_Completion_Percentage': 'max',  # Maximum completion percentage
        'sakani_beneficiary_price': ['min', 'max'],  # Price range for Sakani beneficiaries
        'non_sakani_beneficiary_price': ['min', 'max'],  # Price range for non-Sakani beneficiaries
        'apartment_area_meter': ['min', 'max'],  # Apartment area range
        'living_area': ['min', 'max', 'mean'],  # Living area range and average
        'floor': lambda x: list(np.unique(x)),  # Unique floor levels as a list
        'bathroom_count': ['min', 'max'],  # Minimum and maximum bathroom counts
        'apartment_type_eng': lambda x: list(np.unique(x)),  # Unique apartment types as a list
        'number_of_rooms': ['min', 'max'],  # Range of room counts
        'master_bedroom_size': ['min', 'max'],  # Master bedroom size range
        'living_room_size': ['min', 'max'],  # Living room size range
        'kitchen_size': ['min', 'max'],  # Kitchen size range
        'guestroom_size': ['min', 'max'],  # Guest room size range
        'apartment_for_sakani_beneficiary': 'sum',  # Count of Sakani beneficiary apartments
        'apartment_for_non_sakani_beneficiary': 'sum',  # Count of non-Sakani beneficiary apartments
        'construction_status_eng': 'first',  # First unique construction status (can modify if needed)
    }

    # Group the DataFrame and apply the aggregation
    result = df.groupby(
        by=[
            'project_id', 'Project URL', 'project_name_eng', 'city_id_eng', 
            'region_id_eng', 'District_Residential_area_eng', 
            'project_latitude', 'project_longitude', 'publish_date'
        ]
    ).agg(agg_dict)

    # Flatten multi-level column index to generate readable column names
    result.columns = [
        f"{col[0]}_{col[1]}" if isinstance(col, tuple) else col for col in result.columns
    ]

    # Reset the index to make it a flat DataFrame
    result = result.reset_index()

    # Rename columns to make them consistent and clean
    result.rename(columns={
        'apartment_type_eng_<lambda>': 'unit_type_available',
        'floor_<lambda>': 'number_of_floors_available'
    }, inplace=True)

    return result


# Generate Embeddings
def generate_embeddings(data: pd.DataFrame, model) -> np.ndarray:
    meta = data.to_dict(orient="records")
    text_list = []
    for record in meta:
        # Concatenate relevant fields to create a meaningful context
        text = f"""Project Name: {record['project_name_eng']} is located in the district of {record['District_Residential_area_eng']}, 
        within the city of {record['city_id_eng']}, in the {record['region_id_eng']} region. The project latitude and longitude are 
        {record['project_latitude']}, {record['project_longitude']}. This project was published on {record['publish_date_first']}, 
        and its current construction status is: {record['construction_status_eng_first']}. The completion percentage is 
        {record['Construction_Completion_Percentage_max']}%.
        The available unit type is {', '.join(record['unit_type_available'])}, with floor options: 
        {', '.join(map(str, record['number_of_floors_available']))}.
        The price range for Sakani beneficiaries is {record['sakani_beneficiary_price_min']} - {record['sakani_beneficiary_price_max']} SAR, 
        and for non-Sakani beneficiaries, it is {record['non_sakani_beneficiary_price_min']} - {record['non_sakani_beneficiary_price_max']} SAR. 
        The apartment area ranges from {record['apartment_area_meter_min']}m² to {record['apartment_area_meter_max']}m², with an average living area of 
        {record['living_area_mean']:.2f}m². Payment options available include: 
        {'Cash' if record['allow_payment_by_cash_max'] else ''} 
        {'and Loan' if record['allow_payment_by_loan_max'] else ''}. 
        The project consists of a total of {record['Apartment_code_size']} units."""
        text_list.append(text)
  
    embeddings = model.encode(text_list, convert_to_tensor=True).cpu().detach().numpy()
    return embeddings

# Build FAISS Index
def build_faiss_index(embeddings: np.ndarray):
    d = embeddings.shape[1]  # Dimension of embeddings
    index = faiss.IndexFlatIP(d)
    index.add(embeddings)
    return index

# Search FAISS Index
def search_faiss(index, query_embedding, top_k=5):
    distances, indices = index.search(query_embedding, top_k)
    return distances, indices

# Backend Logic
def backend_pipeline():
    st.title("Real Estate Assistant")

    # Load Data
    st.write("Loading data...")
    # project_data = pd.DataFrame({"project_id": [1, 2, 3],
    #                              "description": ["Luxury villa in Riyadh", 
    #                                              "Affordable apartment in Riyadh",
    #                                              "Spacious villa in Jeddah"],
    #                              "region": ["Riyadh", "Riyadh", "Jeddah"],
    #                              "sakani_price": [1200000, 900000, 1600000]})
    
    project_data = generating_project_level_table()
    
    unit_data = pd.DataFrame({"unit_id": [101, 102, 103],
                              "project_id": [1, 1, 2],
                              "description": ["3BHK Villa", "4BHK Villa", "2BHK Apartment"]})

    # Load Embedding Model
    model = load_embedding_model()

    # Generate Embeddings
    st.write("Generating embeddings...")
    project_embeddings = generate_embeddings(project_data, model)
    # unit_embeddings = generate_embeddings(unit_data, "description", model)

    # Build FAISS Index
    project_index = build_faiss_index(project_embeddings)
    # unit_index = build_faiss_index(unit_embeddings)

    # User Input
    st.write("Please enter your preferences:")
    region = st.text_input("Region (e.g., Riyadh)")
    price = st.number_input("Maximum Price", min_value=500_000, max_value=5_000_000, value=1_500_000)
    user_query = st.text_area("Describe your property preference (e.g., villa with 4 bedrooms)")

    if st.button("Search"):
        # Generate Query Embedding
        query_embedding = model.encode([user_query], convert_to_tensor=True).cpu().detach().numpy()

        # Determine Table to Query
        if "project_id" not in st.session_state.get("filters", {}).keys():
            # Project-Level Search
            st.write("Searching project-level data...")
            distances, indices = search_faiss(project_index, query_embedding)
            st.write("Top Projects:")
            for i in indices[0]:
                st.write(f"Project ID: {project_data.iloc[i]['project_id']}, "
                         f"Project Name: {project_data.iloc[i]['project_name_eng']}",
                         f"Project city: {project_data.iloc[i]['city_id_eng']}",
                         f"Project district: {project_data.iloc[i]['District_Residential_area_eng']}",
                         f"Project region: {project_data.iloc[i]['region_id_eng']}",
                         f"Project min price: {project_data.iloc[i]['sakani_beneficiary_price_min']}",
                         f"Project max price: {project_data.iloc[i]['sakani_beneficiary_price_max']}")
        # else:
        #     # Unit-Level Search
        #     st.write("Searching unit-level data...")
        #     distances, indices = search_faiss(unit_index, query_embedding)
        #     st.write("Top Units:")
        #     for i in indices[0]:
        #         st.write(f"Unit ID: {unit_data.iloc[i]['unit_id']}, "
        #                  f"Description: {unit_data.iloc[i]['description']}")

        # Dynamic Filters
        st.write("Filters:")
        filters = {"Region": region, "sakani_price": price}
        st.session_state["filters"] = filters
        st.json(filters)

# Run Streamlit App
if __name__ == "__main__":
    backend_pipeline()
