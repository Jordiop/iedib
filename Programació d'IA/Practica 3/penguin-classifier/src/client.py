import requests
import json

def test_prediction(model_name, data):
    url = f'http://localhost:5000/predict/{model_name}'
    response = requests.post(url, json=data)
    result = response.json()
    print(f"\n{model_name.upper()} Prediction:")
    print(f"Input: {json.dumps(data, indent=2)}")
    print(f"Predicted species: {result['species']}")

def main():
    test_cases = [
        {
            'island': 'Biscoe',
            'bill_length_mm': 50.0,
            'bill_depth_mm': 15.0,
            'flipper_length_mm': 220,
            'body_mass_g': 5000,
            'sex': 'Male'
        },
        {
            'island': 'Dream',
            'bill_length_mm': 35.0,
            'bill_depth_mm': 17.0,
            'flipper_length_mm': 185,
            'body_mass_g': 3400,
            'sex': 'Female'
        }
    ]
    
    models = ['logistic', 'svm', 'decision_tree', 'knn']
    
    for test_case in test_cases:
        print("\n" + "="*50)
        for model in models:
            test_prediction(model, test_case)

if __name__ == "__main__":
    main()