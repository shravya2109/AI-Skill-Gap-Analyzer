import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ No API key found!")
    exit(1)

genai.configure(api_key=api_key)

print("🔍 Listing available Gemini models...")
try:
    models = genai.list_models()
    generate_content_models = []
    
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            generate_content_models.append(model.name)
            print(f"✅ {model.name}")
    
    print(f"\n📊 Found {len(generate_content_models)} models supporting generateContent")
    
    # Test the first available model
    if generate_content_models:
        test_model_name = generate_content_models[0].replace('models/', '')
        print(f"\n🧪 Testing model: {test_model_name}")
        
        model = genai.GenerativeModel(test_model_name)
        response = model.generate_content("Hello, this is a test. Please respond with 'Test successful!'")
        print(f"✅ Test response: {response.text}")
        
        print(f"\n🎯 Recommended model to use: {test_model_name}")
    
except Exception as e:
    print(f"❌ Error: {e}")