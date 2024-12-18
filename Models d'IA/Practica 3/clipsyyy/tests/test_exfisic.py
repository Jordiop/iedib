import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.expert_system.exfisic import PhysicalActivityExpert

def test_expert_system():
    expert = PhysicalActivityExpert()
    
    # Diversos casos de prova que coincideixen amb les nostres regles
    test_cases = [
        {
            "name": "Principiant - Pèrdua de pes",
            "data": {
                "age": 30,
                "weight": 75,
                "height": 175,
                "activity_level": "low",
                "health_conditions": "none",
                "fitness_goal": "weight loss",
                "time_available": "normal"
            }
        },
        {
            "name": "Persona ocupada",
            "data": {
                "age": 35,
                "weight": 70,
                "height": 170,
                "activity_level": "moderate",
                "health_conditions": "none",
                "fitness_goal": "general fitness",
                "time_available": "limited"
            }
        },
        {
            "name": "Persona gran amb artritis",
            "data": {
                "age": 70,
                "weight": 65,
                "height": 165,
                "activity_level": "low",
                "health_conditions": "arthritis",
                "fitness_goal": "maintenance",
                "time_available": "normal"
            }
        }
    ]
    
    for case in test_cases:
        print(f"\nTestejant: {case['name']}")
        print("Dades:", case['data'])
        recommendations = expert.get_recommendation(**case['data'])
        
        if recommendations:
            print("\nRecomanacions trobades:")
            for rec in recommendations:
                print("\nTipus d'exercici:", rec['exercise_type'])
                print("Intensitat:", rec['intensity'])
                print("Freqüència:", rec['frequency'])
                print("Duració:", rec['duration'])
                print("Exercicis específics:", rec['specific_exercises'])
                print("Pla de progressió:", rec['progression_plan'])
                print("Consells nutricionals:", rec['nutrition_advice'])
                print("Precaucions:", rec['precautions'])
        else:
            print("\nNo s'han trobat recomanacions per aquest cas!")
        
        print("-" * 80)

if __name__ == "__main__":
    test_expert_system()