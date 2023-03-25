import os
import re

import discord
import markovify

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('API_KEY')
TARGET_ID = os.getenv('TARGET_ID')
ADMIN_ID = os.getenv('ADMIN_ID') 
TEXTFILE_PATH = os.getenv('TEXTFILE_PATH')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
        print("Logged on as", client.user)
        await client.change_presence(activity=discord.Game(name="!predict"))

@client.event
async def on_message(message):
    # Crude checks for image, links or embeds:
    # checks if contains, does not check if it is the only thing in the message
    if "http" in message.content or message.embeds or message.attachments:
        return
    
    print(message.author.id)
    """
    Core prediction logic
    """ 
    if message.content == "!predict":
        try:
            with open(TEXTFILE_PATH, "r") as f:
                text = f.read()
                # 2 or 3 state size
                text_model = markovify.Text(text, state_size=2)
                # sentence = text_model.make_short_sentence(min_chars=0, max_chars=100)
                sentence = text_model.make_sentence()
                while sentence is None:
                    sentence = text_model.make_sentence()
                await message.channel.send(sentence)
        except Exception as e:
            print(e)
            await message.channel.send("ya (something fuckin broke)")
        
    # Logic to append any message from the target user to the data file
    # Used to collect message for the training data
    elif str(message.author.id) == str(TARGET_ID):
        if message.content[0] == "<":
            return
        with open(TEXTFILE_PATH, "a+") as f:
            f.write(message.content + "\n")
    
    #  """_summary_ : This is the code for retrieving all of the target's messages from a channel. 
    #    It is not currently in use, but it is here for future reference. Appends to a file called located in DATA_PATH
    #   Collects x messages from the discord channel it's typed in and checks if the user id is the target id """
    
    elif message.content == "!retrieve" and str(message.author.id) == str(ADMIN_ID):
        print("Retrieve received")
        user_messages = []
        async for msg in message.channel.history(limit=100000):
            if msg.author.id == TARGET_ID:
                if not msg.embeds:
                    if not msg.attachments:
                        http_regex = re.sub(r"http\S+", "", msg.content)
                        embeds_regex = re.sub(r"<.*?>", "", http_regex)
                        if embeds_regex != "":
                            user_messages.append(msg)
        
        if user_messages:
            with open(TEXTFILE_PATH, "a+") as f:
                for msg in user_messages:
                    try:
                        f.write(msg.content + "\n")
                    except:
                        pass
            print("Retrieval Complete!")
        else:
            print("No messages found")
    


def main():
    client.run(TOKEN)
    # print(TOKEN)

if __name__ == "__main__":
    main()
    