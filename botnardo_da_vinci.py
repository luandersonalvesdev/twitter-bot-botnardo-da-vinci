import os
import json
import tweepy
from openai import OpenAI
import requests
import time
import schedule
import random
from datetime import datetime

def read_data_json():
    script_dir = os.path.dirname(__file__)
    json_path = os.path.join(script_dir, "keys.json")
    with open(json_path) as file:
        return json.load(file)

data = read_data_json()

bearer_token = data["BEARER_TOKEN"]
access_token = data["ACCESS_TOKEN"]
access_token_secret = data["ACCESS_TOKEN_SECRET"]
api_key = data["API_KEY"]
api_key_secret = data["API_KEY_SECRET"]
open_ia_key = data["OPEN_IA_KEY"]

client_twitter = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=api_key,
    consumer_secret=api_key_secret,
    access_token=access_token,
    access_token_secret=access_token_secret,
)

client_openia = OpenAI(api_key=open_ia_key)

auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

limit_credits_date = datetime(2024, 5, 10)

def main():
    days_left = (limit_credits_date - datetime.now()).days

    print("Botnardo Da Vinci começou a pintar 🖌️...")
    try:
        response = client_openia.chat.completions.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {
                    "role": "user",
                    "content": "You have at your disposal an AI that generates the image you want. Generate a completely random but very detailed prompt to create an image. It can contain anything, for example: animals, people, places, fruits, objects, life forms, etc. Literally anything. But do not exceed 230 characters."
                }
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        prompt_text = response.choices[0].message.content

        print(f"🤖 - Já tive minha ideia: {prompt_text}")

        image_response = client_openia.images.generate(
            model="dall-e-2",
            prompt=prompt_text,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = image_response.data[0].url

        print(f"🤖 - Pintura finalizada! Caso queira ver uma prévia está aqui: {image_url}")

        image = requests.get(image_url)

        with open("image.png", "wb") as image_file:
            image_file.write(image.content)

        media_id = api.media_upload("image.png").media_id_string

        tweet_text = f"Me Restam {days_left} dias de vida. Prompt: {prompt_text}"

        if len(tweet_text) > 279:
            tweet_text = f"Me Restam {days_left} dias de vida. O prompt desta obra excedeu o limite de caracteres de um post, por esse motivo não será exibido."

        client_twitter.create_tweet(text=tweet_text, media_ids=[media_id])

        os.remove("image.png")

        client_twitter.create_tweet(text="🤖 - Próxima obra a ser pintada já está em andamento...")

        print(f"🤖 - Pintura publicada com sucesso! Até amanhã.")
        print("_______________________________________________________________________________")
    except Exception as e:
        print(e)

def generate_random_time():
    return f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}"

def wait_until_next_execution(next_execution_time):
    current_time = datetime.now().time()
    scheduled_time = datetime.strptime(next_execution_time, '%H:%M').time()

    time_diff = datetime.combine(datetime.today(), scheduled_time) - datetime.combine(datetime.today(), current_time)
    time_diff_seconds = time_diff.total_seconds()

    wakeup_time = time_diff_seconds - (5 * 60)

    if wakeup_time > 0:
        print(f"Script dormindo até perto do horário agendado ({next_execution_time}). Acordará em {wakeup_time/60:.2f} minutos.")
        time.sleep(wakeup_time)

def schedule_main():
    # next_random_time = generate_random_time()
    # next_execution_time = f"{next_random_time[:2]}:{next_random_time[3:]}"
    print('__________________________########################__________________________________')
    # print(f"Horário agendado da próxima arte: {next_random_time} 🕑 do dia {datetime.now().strftime('%d/%m/%Y')} 📅")
    schedule.every(2).minutes.do(main)
    print('EXECUTOU E SERÁ EXECUTADO A CADA 2 MINUTOS')
    # wait_until_next_execution(next_execution_time)

schedule_main()

while True:
    schedule.run_pending()
    time.sleep(30)
    print('Pensando... 💭')
