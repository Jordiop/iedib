from flask import Flask, request, jsonify
import joblib
import numpy as np

app = Flask(__name__)

dv = joblib.load('models/dict_vectorizer.joblib')
scaler = joblib.load('models/scaler.joblib')
le = joblib.load('models/label_encoder.joblib')
models = {
    'logistic': joblib.load('models/logistic_model.joblib'),
    'svm': joblib.load('models/svm_model.joblib'),
    'decision_tree': joblib.load('models/decision_tree_model.joblib'),
    'knn': joblib.load('models/knn_model.joblib')
}

@app.route('/predict/<model_name>', methods=['POST'])
def predict(model_name):
    if model_name not in models:
        return jsonify({'error': 'Model not found'}), 404
        
    data = request.json
    
    cat_features = {
        'island': data['island'],
        'sex': data['sex']
    }
    X_cat = dv.transform([cat_features])
    
    num_features = np.array([[
        data['bill_length_mm'],
        data['bill_depth_mm'],
        data['flipper_length_mm'],
        data['body_mass_g']
    ]])
    X_num = scaler.transform(num_features)
    
    X = np.hstack((X_num, X_cat))
    
    prediction = models[model_name].predict(X)
    species = le.inverse_transform(prediction)
    
    return jsonify({'species': species[0]})

if __name__ == '__main__':
    app.run(port=5000)