import base64

from openai import OpenAI

from app.api_keys_config import api_game_key

client = OpenAI(api_key=api_game_key.OPEN_AI_API_KEY)
prompt_for_openai = """Transform this photo into a stylized cartoon meme with a video game vibes.
Place the dog clearly in the center as the main character.
Make the style look like a slightly low-quality, humorous video game character,
with exaggerated features and expressive emotions.
Use vibrant but slightly distorted colors, like a buggy or poorly designed game.
Add large, bold, sloppy meme-style text at the top:
'WELCOME TO WORST GAME GENERATOR'
Optionally add smaller subtitle text at the bottom:
'Where every game is a mistake'
Make the overall tone ironic and funny, like a parody of bad video games.
Add subtle gaming elements (UI, glitch effects, pixelation, or fake HUD elements).Keep it playful,
chaotic, and meme-like."""

result = client.images.edit(
    model="gpt-image-1",
    image=open("kuroko.jpg", "rb"),  # your base image
    prompt=prompt_for_openai,
    size="1024x1024",
)

# Save result
image_base64 = result.data[0].b64_json


with open("output.png", "wb") as f:
    f.write(base64.b64decode(image_base64))
