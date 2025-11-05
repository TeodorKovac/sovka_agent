from openai import OpenAI
from settings.config_settings import settings

def get_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)

def test_openai_api(client: OpenAI):
    """Test the OpenAI API connection"""
    try:
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "user", "content": "Say hello, this is a test!"}
            ],
        )
        print("✅ API connection successful!")
        print("Response:", response.choices[0].message.content)
    except Exception as e:
        print("❌ API test failed!")
        print(e)

if __name__ == "__main__":
    client = get_client()
    test_openai_api(client)