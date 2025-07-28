
import os
from georag.pipeline import multi_pipeline

example_questions = [
    "I am looking for the best sushi restaurant in Europaplatz.",
    "I want to buy a new washing machine and where can I go to check in the city?",
    "Where can I bring my 2 kids to visit in Karlsruhe?",
    "Suggest a vegan and gluten-free falafel shop that is open on saturday evening.",
    "Which cafe has the fastest internet connection?",
]
place = "Karlsruhe"

answers = multi_pipeline(place, example_questions, verbose=True, name="example")
