from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np

app = Flask(__name__)
model = load_model("pet_disease_model.keras")

class_names = ["Dental Disease", "Ear Mites", "Eye Infection", "Fungal Infection", "Hot Spots",
               "Mange", "Ringworm", "Scabies", "Tick Infestation"]

disease_info = {
    "Dental Disease": {
        "first_aid": "Provide soft food and clean drinking water.",
        "recommended_action": "Brush teeth regularly and monitor eating habits.",
        "vet": "See a vet within a few days if pain or bleeding occurs."
    },

    "Ear Mites": {
        "first_aid": "Clean ears gently with pet-safe cleaner.",
        "recommended_action": "Prevent scratching and isolate from other pets.",
        "vet": "Visit vet soon for anti-mite medication."
    },

    "Eye Infection": {
        "first_aid": "Wipe discharge using clean warm cloth.",
        "recommended_action": "Prevent rubbing or scratching eyes.",
        "vet": "See vet immediately if swelling or cloudiness appears."
    },

    "Fungal Infection": {
        "first_aid": "Keep infected area dry and clean.",
        "recommended_action": "Avoid sharing bedding with other pets.",
        "vet": "Vet visit recommended for antifungal treatment."
    },

    "Hot Spots": {
        "first_aid": "Trim fur around affected area carefully.",
        "recommended_action": "Prevent licking or scratching.",
        "vet": "See vet if area becomes swollen or produces pus."
    },

    "Mange": {
        "first_aid": "Wash bedding and isolate infected pet.",
        "recommended_action": "Maintain hygiene and avoid contact with others.",
        "vet": "Vet treatment strongly recommended."
    },

    "Ringworm": {
        "first_aid": "Keep skin dry and clean.",
        "recommended_action": "Disinfect environment frequently.",
        "vet": "See vet for antifungal medication."
    },

    "Scabies": {
        "first_aid": "Reduce scratching and clean affected skin.",
        "recommended_action": "Wash blankets and pet items.",
        "vet": "Immediate vet treatment recommended."
    },

    "Tick Infestation": {
        "first_aid": "Remove visible ticks carefully using tweezers.",
        "recommended_action": "Use tick prevention products.",
        "vet": "See vet if fever or weakness appears."
    }
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    file = request.files["image"]

    image = Image.open(file).convert("RGB")
    image = image.resize((224, 224))
    img_array = np.array(image) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction[0])
    result = class_names[predicted_class]
    info = disease_info[result]
    return jsonify({
        "prediction": result,
        "first_aid": info["first_aid"],
        "recommended_action": info["recommended_action"],
        "vet": info["vet"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)