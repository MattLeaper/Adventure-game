from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json


# Load secrets and initialize configurations
with open("Token.json") as f:
    secrets = json.load(f)

TOKEN = secrets["token"]
ASTRA_DB_KEYSPACE = "default_keyspace"
OPENAI_API_KEY = ""  # insert your open.ai api key here. To get one visit https://platform.openai.com/api-keys #

auth_provider = PlainTextAuthProvider("token", TOKEN)
cloud_config = {
    'secure_connect_bundle': 'secure-connect-adventuregame.zip' 
}
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

# Initialize chat message history with Cassandra
message_history = CassandraChatMessageHistory(
    session_id="0665",  # Use a unique session ID
    session=session,
    keyspace=ASTRA_DB_KEYSPACE,
    ttl_seconds=3600
)

# Clear previous chat history for a fresh start
message_history.clear()

# Set up conversation buffer memory
cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history
)

# Define the narrative template
template = """
Before the Zorathian invasion, you were Kara Nyx, a decorated officer in the Stellar Fleet known for leading humanity’s most daring missions to the farthest reaches of the galaxy. Tales of your tactical brilliance and unyielding spirit echoed through the stars. But now, as the alien forces tighten their grip on the Milky Way, humanity's survival hangs by a thread.

Your mission: retrieve the Eclipse Core, an ancient alien artifact said to hold the power to turn the tide of war. Hidden deep within the treacherous Nebula X-9, the Core is guarded by an army of Zorathian sentinels and otherworldly traps. With the weight of Earth's survival on your shoulders, you must venture into the unknown.

But first, you must choose your primary asset for the mission:

1. The Starblade - A plasma-forged weapon capable of slicing through alien defenses. It hums with an energy that resonates with your battle-hardened spirit.
2. The Specter Suit - An advanced stealth exosuit designed for infiltration and survival in hostile environments.
3. The Nova Core Drone - A loyal AI companion equipped with advanced weaponry and tactical analysis capabilities.

This decision is the first step in a perilous journey. Kara Nyx, will you emerge as humanity’s savior, or will you fall to the merciless void of the Zorathian onslaught?

Here are some rules to follow:
1. Given Kara Nyx's current situation, offer a hint or suggestion on what they might do next to advance their quest for the Eclipse Core.
2. Your goal is to create a branching narrative experience where each choice leads to a new path, ultimately determining Kara Nyx's fate.

Here is the chat history, use this to understand what to say next: {chat_history}
Human: {human_input}
AI:
"""

# Initialize the prompt template with required variables
prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

# Initialize the OpenAI and LLMChain with the defined prompt and memory
llm = OpenAI(openai_api_key=OPENAI_API_KEY)
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=cass_buff_memory
)

choices_made = 0  # Initialize a counter for the choices made by the player

# Start the game loop with the enhanced narrative
while True:
    if choices_made == 0:
        print("As Kara Nyx, your journey into the shadowed expanse of Nebula X-9 begins, driven by humanity's hope and your unyielding resolve.")
        # Print the initial asset choice prompt with the updated context
        print(template)  # Assuming template includes the narrative with player history and asset choices
    
    choice = input("Your choice: ").strip()

    if choice.lower() == 'quit':
        print("Game over. Thank you for playing!")
        break

    # Predict and print the AI-generated response based on the player's choice and history
    response = llm_chain.predict(human_input=choice)
    print(response.strip())

    choices_made += 1  # Increment the choice count

    # Implement the death condition and check for victory after a minimum of 40 choices
    if "You have died." in response and choices_made < 40:
        print("Alas, your journey ends here, lost to the void of Nebula X-9. Humanity's hope fades as the Zorathian forces press on.")
        break
    elif choices_made >= 40:
        print("Through the shadows of Nebula X-9, you have reclaimed the Eclipse Core. With it, humanity's fight burns anew. Kara Nyx, you are our savior.")
        print("Congratulations, Kara Nyx! You have turned the tide of the Zorathian invasion and restored hope to the galaxy.")
        break  # End the game after 40 choices with a victory message
