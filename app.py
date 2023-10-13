from flask import Flask, render_template, request
import tensorflow as tf
import joblib
import numpy as np
import cv2
import base64
import mysql.connector
import datetime

try:

    connection = mysql.connector.connect(
        host = "localhost",
        username = "root",
        password = "Bercha213",
        database = "userMessageData"
    )
except Exception as e:
    print(e)

app = Flask(__name__)

disease_info = {
    "Actinic Keratosis": {
        "Symptoms": "Actinic Keratosis may present with rough, scaly patches on the skin, often in sun-exposed areas. These patches may be red or brown and may itch or burn.",
        "Precautions": "To prevent Actinic Keratosis, avoid excessive sun exposure, wear sunscreen, and protective clothing when outdoors."
    },
    "Basal Cell Carcinoma and other Malignant Lesions": {
        "Symptoms": "Basal Cell Carcinoma typically appears as a shiny, translucent bump or a pearly nodule on the skin. It may bleed easily and form an open sore.",
        "Precautions": "To reduce the risk of Basal Cell Carcinoma, protect your skin from UV radiation, avoid tanning beds, and perform regular skin checks."
    },
    "Atopic Dermatitis Photos": {
        "Symptoms": "Atopic Dermatitis, also known as eczema, may cause dry, itchy, and inflamed skin. It can result in red or brown patches, blisters, and scaling of the skin.",
        "Precautions": "Managing Atopic Dermatitis involves keeping the skin moisturized, avoiding triggers like allergens and irritants, and using prescribed medications as directed."
    }
}











model1 = tf.keras.models.load_model('model.h5')
encoder1 = joblib.load("encoder.pkl")
   

labels = {i: label for i, label in enumerate(encoder1.classes_)}
def preprocessing(image):
    # input_img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    resized_input_image = cv2.resize(image, (224, 224))
    
    return np.array(resized_input_image) / 10

@app.route('/')
def main():
    Sucess = False
    Unsucess = False

    return render_template("index.html" , submitSucess= Sucess, submitUnsucess= Unsucess)






@app.route('/predict', methods=['POST', 'GET'])
def upload():
    Sucess = False
    Unsucess = False

    img = request.files["skinImage"].read()
    img_array = np.frombuffer(img, np.uint8)
    uploaded_image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    prediction = model1.predict(preprocessing(uploaded_image).reshape(1,224,224,3))
    predicted_label = labels[np.argmax(prediction)]

    symptoms = ""
    precautions = ""
    predicted_diseases = {
        'Acne and Rosacea Photos': 'Acne and Rosacea',
        'Actinic Keratosis Basal Cell Carcinoma and other Malignant Lesions': 'Basal Cell Carcinoma and other Malignant Lesions',
        'Atopic Dermatitis Photos': 'Atopic Dermatitis'
    }
    
    predicted_disease = predicted_diseases.get(predicted_label)
    
    if predicted_disease == 'Acne and Rosacea':
        symptoms = "Acne and Rosacea may have symptoms such as redness, visible blood vessels, and the appearance of acne-like bumps. Additionally, individuals may experience flushing or blushing easily, and in more severe cases, eye symptoms."
        precautions = "Treatment for Acne and Rosacea often includes topical creams, antibiotics, and lifestyle changes to manage symptoms. It is important to consult a dermatologist for a personalized treatment plan."
    elif predicted_disease == 'Basal Cell Carcinoma and other Malignant Lesions':
        symptoms = "Basal Cell Carcinoma typically appears as a shiny, translucent bump or a pearly nodule on the skin. It may bleed easily and form an open sore."
        precautions = "To reduce the risk of Basal Cell Carcinoma, protect your skin from UV radiation, avoid tanning beds, and perform regular skin checks."
    elif predicted_disease == 'Atopic Dermatitis':
        symptoms = "Atopic Dermatitis, also known as eczema, may cause dry, itchy, and inflamed skin. It can result in red or brown patches, blisters, and scaling of the skin."
        precautions = "Managing Atopic Dermatitis involves keeping the skin moisturized, avoiding triggers like allergens and irritants, and using prescribed medications as directed."

    
    _, img_encoded = cv2.imencode(".jpg", uploaded_image)
    img_base64 = base64.b64encode(img_encoded).decode("utf-8")

    return render_template("predicted.html", predicted=predicted_label, symptoms=symptoms, precautions=precautions, image=img_base64, submitSucess= Sucess, submitUnsucess= Unsucess)





@app.route('/submit', methods=['POST', 'GET'])
def contactUs():
    Sucess = False
    Unsucess = False
    if request.method == 'POST':
        try:
            #
            #  Get the values from the form
            name = request.form['name']
            email = request.form['email']
            msg = request.form['message']

            current_datetime = datetime.datetime.now()
    
            # Convert the datetime object to a string for display or storage
            fd = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

            # Now you can work with these values in your Python code
            print(f"Name: {name}")
            print(f"Email: {email}")
            print(f"Message: {msg}")

            
            cursor = connection.cursor()

            # Corrected SQL query with proper string formatting
            query = f'''INSERT INTO messages (userName, userEmail, userMessage ,msgTime) VALUES ('{name}', '{email}', '{msg}' ,'{fd}');'''

            # Execute the query
            cursor.execute(query)

            # Commit the changes to the database
            connection.commit()
            Sucess = True
            
            
            
            
        except Exception as e:
            print(e)
            Unsucess = True


    return render_template("index.html" , submitSucess= Sucess, submitUnsucess= Unsucess)

if __name__ == "__main__":
    app.run(port = 3000 ,debug =True)