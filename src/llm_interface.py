#from sentence_transformers import sampler

user = "Find the best cafe to take my best friend in Karlsruhe, Germany next weekend."

prompt = f"""
Consider the following prompt and answer this question: Is the user asking for a location? 
If so return the name of the location and if known any other information
provided by the user (eg. activity, number of people, time, etc.)
Answer in JSON object format. If the location does not exist return an empty dictionary. 
Do not include anything else in the answer.
The prompt is {user}
""".replace("\n", "")

