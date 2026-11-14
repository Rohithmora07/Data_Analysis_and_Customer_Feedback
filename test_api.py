import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Testing API Connections")
print("=" * 60)

# Test Groq
print("\n🔵 Testing Groq...")
try:
    from groq import Groq
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        client = Groq(api_key=groq_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'Hello from Groq' in 5 words"}],
            max_tokens=100
        )
        print("✅ Groq works!")
        print(f"Response: {response.choices[0].message.content}")
    else:
        print("❌ GROQ_API_KEY not set")
except Exception as e:
    print(f"❌ Groq failed: {e}")

# Test Mistral
print("\n🟣 Testing Mistral...")
try:
    from mistralai import Mistral  # ✅ CORRECT NEW IMPORT
    mistral_key = os.getenv("MISTRAL_API_KEY")
    if mistral_key:
        client = Mistral(api_key=mistral_key)
        response = client.chat.complete(  # ✅ Changed from .chat()
            model="mistral-small-latest",  # ✅ Use -latest version
            messages=[{"role": "user", "content": "Say 'Hello from Mistral' in 5 words"}]
        )
        print("✅ Mistral works!")
        print(f"Response: {response.choices[0].message.content}")
    else:
        print("❌ MISTRAL_API_KEY not set")
except Exception as e:
    print(f"❌ Mistral failed: {e}")

print("\n" + "=" * 60)
print("Testing Complete")
print("=" * 60)


from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

for model in client.models.list().data:
    print(model.id)