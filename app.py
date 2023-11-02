import streamlit as st
import pandas as pd
import pickle
import requests

API_KEY = st.secrets(['API_KEY'])

# Load the trained model
with open('best_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

# Set up a Streamlit app with some styling
st.set_page_config(page_title="Agricultural Supply Chain Management", layout="wide")

# Add custom CSS for styling
st.markdown(
    """
    <style>
    /* Add your custom CSS code here */
    body {
        font-family: Arial, sans-serif;
        background-color: #f7f7f7;
    }
    .stApp {
        padding: 2rem;
    }
    .custom-header {
        font-size: 36px;
        font-weight: bold;
        color: #333333;
        margin-bottom: 1rem;
    }
    .custom-subheader {
        font-size: 20px;
        color: #666666;
        margin-bottom: 0.5rem;
    }
    .custom-result {
        font-size: 18px;
        color: #333333;
        margin-bottom: 0.5rem;
    }
    .fancy-button {
        background-color: #ff4081;
        color: #ffffff;
        border: none;
        padding: 0.5rem 1rem;
        font-size: 18px;
        border-radius: 4px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .fancy-button:hover {
        background-color: #f50057;
    }
    .your-logo {
        width: 100%;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Define the sidebar
st.sidebar.title("Dashboard")
dashboard_page = st.sidebar.selectbox("Page", ("Crop Yield Prediction", "Carbon Emissions"))

# Crop Yield Prediction Page
if dashboard_page == "Crop Yield Prediction":
    st.title("Crop Yield Prediction")
    #st.image("your_logo.png", use_column_width=True, class="your-logo")

    st.header("Custom Input Data")

    # User input for custom data
    state_name = st.text_input("State Name")
    crop_type = st.text_input("Crop Type")
    rainfall = st.number_input("Rainfall (mm)", 0.0)
    temperature = st.number_input("Temperature (°C)", 0.0)
    production = st.number_input("Production in Tons", 0)
    area = st.number_input("Area in Hectares", 0.0)

    # Button to trigger the prediction
    if st.button("Predict Crop", "fancy-button"):
        # Create a DataFrame from user input
        custom_input = {
            'State_Name': [state_name],
            'Crop_Type': [crop_type],
            'rainfall': [rainfall],
            'temperature': [temperature],
            'Production_in_tons': [production],
            'Area_in_hectares': [area],
        }
        custom_input_df = pd.DataFrame(custom_input)

        with open('label_encoder.pkl', 'rb') as label_encoder_file:
            label_encoder = pickle.load(label_encoder_file)

        with open('preprocessor.pkl', 'rb') as preprocessor_file:
            preprocessor = pickle.load(preprocessor_file)

        # Preprocess the custom input data
        custom_input_features = preprocessor.transform(custom_input_df)

        # Use the trained model to predict the probabilities for all classes (crops)
        predicted_probabilities = model.predict_proba(custom_input_features)

        # Get the top 5 predicted crops
        top_crops_indices = predicted_probabilities.argsort()[0][::-1][:5]
        top_crops = label_encoder.inverse_transform(top_crops_indices)

        # Display the custom input data
        st.header("Custom Input Data")
        st.write(custom_input_df)

        # Display the predicted crops
        st.header("Top 5 Predicted Crops")
        for i, crop in enumerate(top_crops, 1):
            st.write(f"{i}. {crop}")

# Carbon Emissions Page
elif dashboard_page == "Carbon Emissions":
    st.title("Carbon Emissions")
    #st.image("your_logo.png", use_column_width=True, class="your-logo")

    st.header("Route Information")

    # User input for route details
    # origin = st.text_input("Origin")
    # destination = st.text_input("Destination")
    distance = st.number_input("Distance (km)", 0.0)
    vehicle = st.selectbox("Vehicle Type", (
        "SmallDieselCar", "MediumDieselCar", "LargeDieselCar", "MediumHybridCar", "LargeHybridCar", "MediumLPGCar",
        "LargeLPGCar", "MediumCNGCar", "LargeCNGCar", "SmallPetrolVan", "LargePetrolVan", "SmallDielselVan",
        "MediumDielselVan", "LargeDielselVan", "LPGVan", "CNGVan", "SmallPetrolCar", "MediumPetrolCar",
        "LargePetrolCar", "SmallMotorBike", "MediumMotorBike", "LargeMotorBike"
    ))

    # Button to calculate emissions
    if st.button("Calculate Emissions", "fancy-button"):
        # Build the request parameters
        querystring = {"distance": str(distance), "vehicle": vehicle}

        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "carbonfootprint1.p.rapidapi.com"
        }

        # Make the API request
        url = "https://carbonfootprint1.p.rapidapi.com/CarbonFootprintFromCarTravel"

        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            data = response.json()
            emissions = data["carbonEquivalent"]

            # Display the results
            st.header("Emissions Calculation")
            st.subheader("Results:")
            st.write(f"Carbon Emissions: {emissions} kg CO2e")
            st.write(f"Distance: {distance} km")
        else:
            st.error("Error occurred during API request. Please try again.")
    
# Run the Streamlit app
if __name__ == '__main__':
    st.markdown("<p style='text-align:center;'><b>Welcome to the Agricultural Supply Chain Management App</b></p>",
                unsafe_allow_html=True)
