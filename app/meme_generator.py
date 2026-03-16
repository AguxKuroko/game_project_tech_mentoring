from openai import OpenAI

from app.api_keys_config import api_game_key

client = OpenAI(api_key=api_game_key.OPEN_AI_API_KEY)

result = client.images.generate(
    model="gpt-image-1",
    prompt="A funny meme of a sad video game controller",
    size="1024x1024",
    quality="low",
)
