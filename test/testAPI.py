from google import genai

client = genai.Client(api_key="AIzaSyDPG8G6gUJSZ5J1qewGsBtm85bAplBA3CE")

print("Checking your model access...")
try:
    for model in client.models.list():
        # This will show you the exact strings you can use
        print(f"✅ Available: {model.name}")
except Exception as e:
    print(f"❌ Could not list models: {e}")




