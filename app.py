from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebasekey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

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

@app.route("/get-pets", methods=["GET"])
def get_pets():
    pets_docs = db.collection("pets").stream()
    pets_list = []
    for doc in pets_docs:
        pet_data = doc.to_dict()
        pet_name = pet_data.get("name")
        clean_pet = {
            "id": doc.id,
            "name": pet_name
        }
        pets_list.append(clean_pet)
    return jsonify(pets_list)

@app.route("/create-profile", methods=["POST"])
def create_profile():
    name = request.form.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400
        
    pet_ref = db.collection("pets").add({
        "name": name,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    return jsonify({"status": "success", "id": pet_ref[1].id, "name": name})

@app.route("/get-history/<pet_id>", methods=["GET"])
def get_history(pet_id):
    try:
        print(f"DEBUG: Request received to fetch history logs for pet ID: {pet_id}")
        logs_docs = db.collection("predictions").where("petId", "==", str(pet_id)).stream()
        
        logs_list = []
        for doc in logs_docs:
            data = doc.to_dict()
            if "timestamp" in data and data["timestamp"]:
                if isinstance(data["timestamp"], str):
                    pass 
                else:
                    data["timestamp"] = data["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                data["timestamp"] = "Date unknown"
                
            logs_list.append(data)
            
        print(f"DEBUG: Found {len(logs_list)} raw historical records matching this pet.")
        logs_list.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        print("DEBUG: History array sorted successfully. Shipping payload back to client.")
        return jsonify(logs_list)
        
    except Exception as e:
        print(f"\nCRITICAL DATABASE EXCEPTION: {str(e)}\n")
        return jsonify({"error": "Failed to look up medical logs", "details": str(e)}), 500

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/profiles")
def profiles_page():
    return render_template("profiles.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files["image"]
        pet_id = request.form.get("pet_id")

        image = Image.open(file).convert("RGB")
        image = image.resize((224, 224))
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)
        predicted_class = np.argmax(prediction[0])
        result = class_names[predicted_class]
        info = disease_info[result]
        if pet_id:
            db.collection("predictions").add({
                "petId": pet_id,
                "disease": result,
                "first_aid": info["first_aid"],
                "recommended_action": info["recommended_action"],
                "vet": info["vet"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        return jsonify({
            "prediction": result,
            "first_aid": info["first_aid"],
            "recommended_action": info["recommended_action"],
            "vet": info["vet"]
        })
    except Exception as e:
        print(f"CRITICAL BACKEND ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)