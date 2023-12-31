import discord
import os
import requests
import re
import nltk
if not nltk.data.find('tokenizers/punkt'):
    nltk.download('punkt')
from nltk.tokenize import word_tokenize
from discord.ext import commands
from dotenv import main
import aiohttp

main.load_dotenv()
bot_token=os.getenv("BOT_TOKEN")

ETHEREUM_ADDRESS_PATTERN = r'\b0x[a-fA-F0-9]{40}\b'
BITCOIN_ADDRESS_PATTERN = r'\b(1|3)[1-9A-HJ-NP-Za-km-z]{25,34}\b|bc1[a-zA-Z0-9]{25,90}\b'
LITECOIN_ADDRESS_PATTERN = r'\b(L|M)[a-km-zA-HJ-NP-Z1-9]{26,34}\b'
DOGECOIN_ADDRESS_PATTERN = r'\bD{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}\b'
XRP_ADDRESS_PATTERN = r'\br[a-zA-Z0-9]{24,34}\b'
COSMOS_ADDRESS_PATTERN = r'\bcosmos[0-9a-z]{38,45}\b'
SOLANA_ADDRESS_PATTERN= r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


async def answer_question(ctx, question):
    url = 'http://127.0.0.1:8800/gpt'
    data = {'user_input': question, 'user_id': str(ctx.author.id), 'user_locale':'fr'}
    headers = {'Content-Type': 'application/json', "Authorization": f"Bearer {os.getenv('BACKEND_API_KEY')}"}

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    response_json = await response.json()
                    if 'output' in response_json:
                        await ctx.reply(f"{response_json['output']}")
                    else:
                        await ctx.reply(f"The 'output' key was not found in the API response.")
                else:
                    await ctx.reply(f"*Sad beep* - I'm sorry I couldn't reach my knowledge base. Please try again later.")
        except Exception as e:
            print(f"Error occurred while sending request: {e}")
            await ctx.reply(f"*Sad beep* - I'm sorry I couldn't reach my knowledge base. Please try again later.")

@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        question = message.content.replace(f'<@!{bot.user.id}>', '').strip()  # extract question
        if re.search(ETHEREUM_ADDRESS_PATTERN, question, re.IGNORECASE) or \
           re.search(BITCOIN_ADDRESS_PATTERN, question, re.IGNORECASE) or \
           re.search(LITECOIN_ADDRESS_PATTERN, question, re.IGNORECASE) or \
           re.search(DOGECOIN_ADDRESS_PATTERN, question, re.IGNORECASE) or \
           re.search(COSMOS_ADDRESS_PATTERN, question, re.IGNORECASE) or \
           re.search(SOLANA_ADDRESS_PATTERN, question, re.IGNORECASE) or \
           re.search(XRP_ADDRESS_PATTERN, question, re.IGNORECASE) :
            await message.reply("I'm sorry, but I can't assist with questions that crypto addresses. Please remove the address and ask again.")
        else:
            await answer_question(message, question)
    await bot.process_commands(message)

@bot.command()
@commands.cooldown(1, 20, commands.BucketType.user)
async def ask(ctx, *, question):
    if re.search(ETHEREUM_ADDRESS_PATTERN, question, re.IGNORECASE) or re.search(BITCOIN_ADDRESS_PATTERN, question, re.IGNORECASE):
        await ctx.reply("I'm sorry, but I can't assist with questions that include Ethereum or Bitcoin addresses. Please remove the address and ask again.")
    else:
        await answer_question(ctx, question)

@ask.error
async def ask_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'Not too fast! Please ask me again in {:.0f}s.'.format(error.retry_after)
        await ctx.reply(msg)
    else:
        raise error

bot.run(bot_token)