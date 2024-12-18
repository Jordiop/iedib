from clips import Environment, Symbol

class PhysicalActivityExpert:
    def __init__(self):
        self.env = Environment()
        
        # Template per a la persona
        self.env.build("""
            (deftemplate person
                (slot age)
                (slot weight)
                (slot height)
                (slot activity-level)
                (slot health-conditions)
                (slot fitness-goal)
                (slot time-available))
        """)

        # Template per a recomanacions
        self.env.build("""
            (deftemplate recommendation
                (slot exercise-type)
                (slot intensity)
                (slot frequency)
                (slot duration)
                (slot precautions)
                (slot specific-exercises)
                (slot progression-plan)
                (slot nutrition-advice))
        """)

        # Regla per a principiants que volen perdre pes
        self.env.build("""
            (defrule beginner-weight-loss
                (person 
                    (age ?age&:(>= ?age 18)&:(<= ?age 65))
                    (activity-level low)
                    (health-conditions none)
                    (fitness-goal "weight loss"))
                =>
                (assert (recommendation 
                    (exercise-type "Mixed Cardio and Strength Training")
                    (intensity "Low to Moderate")
                    (frequency "3-4 times per week")
                    (duration "30-45 minutes")
                    (specific-exercises "Walking (15 min), Light jogging (10 min), Bodyweight squats (10 reps x 3 sets), Push-ups (5-10 reps x 3 sets)")
                    (progression-plan "Week 1-2: Focus on form and building habit. Week 3-4: Increase duration by 5 min. Week 5-6: Add resistance training.")
                    (nutrition-advice "Focus on protein intake and reducing processed foods. Aim for caloric deficit of 500 kcal/day.")
                    (precautions "Start slowly, focus on proper form, stay hydrated"))))
        """)

        # Regla per a nivell intermig que vol guanyar múscul
        self.env.build("""
            (defrule intermediate-muscle-gain
                (person 
                    (age ?age&:(>= ?age 18)&:(<= ?age 65))
                    (activity-level moderate)
                    (health-conditions none)
                    (fitness-goal "muscle gain"))
                =>
                (assert (recommendation 
                    (exercise-type "Progressive Strength Training")
                    (intensity "Moderate to High")
                    (frequency "4-5 times per week")
                    (duration "45-60 minutes")
                    (specific-exercises "Compound exercises: Squats (4x8-12), Deadlifts (4x6-8), Bench Press (4x8-12), Rows (4x8-12)")
                    (progression-plan "Week 1-4: Focus on compound movements. Week 5-8: Increase weight by 2.5-5kg when able to complete all reps.")
                    (nutrition-advice "Increase protein intake to 1.6-2.0g/kg bodyweight. Maintain slight caloric surplus (300-500 kcal/day).")
                    (precautions "Ensure proper form, use spotter when needed, adequate rest between sets"))))
        """)

        # Regla per a gent gran o amb problemes articulars
        self.env.build("""
            (defrule senior-low-impact
                (person 
                    (age ?age&:(> ?age 65))
                    (activity-level ?level)
                    (health-conditions "arthritis"))
                =>
                (assert (recommendation 
                    (exercise-type "Low Impact Training")
                    (intensity "Low")
                    (frequency "2-3 times per week")
                    (duration "20-30 minutes")
                    (specific-exercises "Water aerobics, Tai Chi, Chair yoga, Light resistance band exercises")
                    (progression-plan "Week 1-2: Start with 10-15 min sessions. Gradually increase duration and resistance as comfortable.")
                    (nutrition-advice "Focus on anti-inflammatory foods, adequate calcium and vitamin D intake.")
                    (precautions "Avoid high-impact movements, listen to body, stop if pain occurs"))))
        """)

        # Regla per a persones molt ocupades
        self.env.build("""
            (defrule busy-schedule
                (person 
                    (time-available "limited")
                    (activity-level ?level)
                    (health-conditions none))
                =>
                (assert (recommendation 
                    (exercise-type "High-Intensity Interval Training (HIIT)")
                    (intensity "Moderate to High")
                    (frequency "2-3 times per week")
                    (duration "15-20 minutes")
                    (specific-exercises "Circuit training: Burpees, Mountain climbers, Jump rope, Bodyweight exercises")
                    (progression-plan "Start with 30s work/30s rest intervals. Progress to 40s work/20s rest as fitness improves.")
                    (nutrition-advice "Plan meals in advance, focus on whole foods and meal prep.")
                    (precautions "Proper warm-up essential, maintain good form even when tired"))))
        """)

    def get_recommendation(self, age, weight, height, activity_level, health_conditions, fitness_goal, time_available="normal"):
        self.env.reset()
        
        # Afegir els fets
        fact_string = f"""
            (assert (person
                (age {age})
                (weight {weight})
                (height {height})
                (activity-level "{activity_level}")
                (health-conditions "{health_conditions}")
                (fitness-goal "{fitness_goal}")
                (time-available "{time_available}")))
        """
        
        self.env.eval(fact_string)
        self.env.run()
        
        # Obtenir recomanacions
        recommendations = []
        for fact in self.env.facts():
            if fact.template.name == 'recommendation':
                recommendations.append({
                    'exercise_type': fact['exercise-type'],
                    'intensity': fact['intensity'],
                    'frequency': fact['frequency'],
                    'duration': fact['duration'],
                    'specific_exercises': fact['specific-exercises'],
                    'progression_plan': fact['progression-plan'],
                    'nutrition_advice': fact['nutrition-advice'],
                    'precautions': fact['precautions']
                })
        
        return recommendations