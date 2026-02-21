import google.generativeai as genai

# Test with your API key
api_key = "AIzaSyDg5T18bwuIzk8n-YDgfhqyEkVup88iZtY"
genai.configure(api_key=api_key)

print("Available models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(model.name)
