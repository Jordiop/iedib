from flask import Flask, request, jsonify
import joblib
import numpy as np
import traceback
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS

# Load preprocessors and models
try:
    print("Loading models and preprocessors...")
    dv = joblib.load('models/dict_vectorizer.joblib')
    scaler = joblib.load('models/scaler.joblib')
    le = joblib.load('models/label_encoder.joblib')
    models = {
        'logistic': joblib.load('models/logistic_model.joblib'),
        'svm': joblib.load('models/svm_model.joblib'),
        'decision_tree': joblib.load('models/decision_tree_model.joblib'),
        'knn': joblib.load('models/knn_model.joblib')
    }
    print("All models and preprocessors loaded successfully!")
except Exception as e:
    print(f"Error loading models: {e}")
    print("Make sure you've run train.py first to create the models")
    raise

@app.route('/predict/<model_name>', methods=['POST', 'OPTIONS'])
def predict(model_name):
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
            
        if model_name not in models:
            return jsonify({'error': f'Model {model_name} not found. Available models: {list(models.keys())}'}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
        
        required_fields = ['island', 'sex', 'bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
        
        # Prepare categorical features
        cat_features = {
            'island': data['island'],
            'sex': data['sex']
        }
        X_cat = dv.transform([cat_features])
        
        # Prepare numerical features
        num_features = np.array([[
            data['bill_length_mm'],
            data['bill_depth_mm'],
            data['flipper_length_mm'],
            data['body_mass_g']
        ]])
        X_num = scaler.transform(num_features)
        
        # Combine features
        X = np.hstack((X_num, X_cat))
        
        # Make prediction
        prediction = models[model_name].predict(X)
        species = le.inverse_transform(prediction)
        
        return jsonify({'species': species[0]})
    except Exception as e:
        print(f"Error processing request: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(port=5000, debug=True)