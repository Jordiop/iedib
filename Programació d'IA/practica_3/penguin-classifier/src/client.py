import requests
import json
import sys
import time

def test_prediction(model_name, data):
    url = f'http://localhost:8026/predict/{model_name}'
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(
            url, 
            json=data,
            headers=headers
        )
        response.raise_for_status()
        
        result = response.json()
        print(f"\n{model_name.upper()} Prediction:")
        print(f"Input: {json.dumps(data, indent=2)}")
        print(f"Predicted species: {result['species']}")
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to server at {url}")
        print("Make sure the Flask server is running (python src/app.py)")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {response.text}")
        print(f"Request headers: {headers}")
        print(f"Request body: {json.dumps(data, indent=2)}")
    except json.JSONDecodeError:
        print(f"Error: Could not parse server response as JSON")
        print(f"Response content: {response.text}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    # Test data
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
    
    print("Starting predictions...")
    for test_case in test_cases:
        print("\n" + "="*50)
        for model in models:
            test_prediction(model, test_case)
            time.sleep(0.1)  # Small delay between requests

if __name__ == "__main__":
    main()