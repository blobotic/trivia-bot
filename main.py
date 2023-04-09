import os
import requests
import random
import asyncio
import discord
from discord.ext import commands

with open("token.txt", "r") as f:
	TOKEN = f.read().rstrip()

bot = commands.Bot(command_prefix=">", intents=discord.Intents.all())


@bot.event
async def on_ready():
	print(f"Logged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n")


# alternative trivia api:
# https://opentdb.com/api_config.php


async def triviaapi(ctx, difficulty, category):

	difficulty = difficulty.lower()
	category = category.lower()

	replacements = {
		"e": "easy",
		"m": "medium",
		"h": "hard",
		"art": "arts_and_literature",
		"tv": "films_and_tv",
		"food": "food_and_drink",
		"gen": "general_knowledge",
		"geo": "geography",
		"hist": "history",
		"mus": "music",
		"sci": "science",
		"soc": "society_and_culture",
		"sport": "sport_and_culture"
	}

	if difficulty in replacements.keys():
		difficulty = replacements[difficulty]
	if category in replacements.keys():
		category = replacements[category]

	valid_difficulties = ["easy", "medium", "hard"]
	valid_categories = ["arts_and_literature", "film_and_tv", "food_and_drink", "general_knowledge", "geography", "history", "music", "science", "society_and_culture", "sport_and_culture"]

	if difficulty not in valid_difficulties or category not in valid_categories:
		await ctx.send("Sorry, invalid difficulty/category! Please try again :P")
		return

	response = requests.get(f"https://the-trivia-api.com/api/questions?limit=1&categories={category}&difficulty={difficulty}")

	return response.json()[0]


@bot.command(name="triviaapi_help")
async def triviaapihelp(ctx):
	await ctx.send("```Difficulties:\n- easy/e\n- medium/m\n- hard/h\n\nCategories:\n- arts_and_literature/art\n- film_and_tv/tv\n- food_and_drink/food\n- general_knowledge/gen\n- geography/geo\n- history/hist\n- music/mus\n- science/sci\n- society_and_culture/soc\n- sport_and_culture/sport```")

@bot.command(name="opentdb_help")
async def opentdbhelp(ctx):
	await ctx.send("```\nDifficulties:\n- easy/e\n- medium/m\n- hard/h\n\nCategories:\n- general_knowledge/gen\n- books\n- music\n- musicals_and_theatres/theatre\n- television/tv\n- video_games/vg\n- board_games/bg\n- science_and_nature/sci\n- computers/cs\n- mathematics/math\n- mythology/myth\n- sports\n- geography/geo\n- history/hist\n- politics/pol\n- art\n- celebrities/cel\n- animals\n- vehicles\n comics\n- gadgets\n- anime_and_manga/anime/manga\n- cartoons_and_animations/cartoons```")

async def opentdb(ctx, difficulty, category):

	difficulty = difficulty.lower()
	category = category.lower()

	replacements = {
		"e": "easy",
		"m": "medium",
		"h": "hard",
		"gen": "general_knowledge",
		"theatre": "musicals_and_theatres",
		"tv": "television",
		"vg": "video_games",
		"bg": "board_games",
		"sci": "science_and_nature",
		"cs": "computers",
		"math": "mathematics",
		"myth": "mythology",
		"geo": "geography",
		"hist": "history",
		"pol": "politics",
		"cel": "celebrities",
		"anime": "anime_and_manga",
		"manga": "anime_and_manga",
		"cartoons": "cartoons_and_animations"
	}

	valid_difficulties = ["easy", "medium", "hard"]
	valid_categories = {
		"general_knowledge": 9, 
		"books": 10,
		"film": 11,
		"music": 12,
		"musicals_and_theatres": 13,
		"television": 14,
		"video_games": 15,
		"board_games": 16,
		"science_and_nature": 17,
		"computers": 18,
		"mathematics": 19,
		"mythology": 20,
		"sports": 21,
		"geography": 22,
		"history": 23,
		"politics": 24,
		"art": 25,
		"celebrities": 26,
		"animals": 27,
		"vehicles": 28,
		"comics": 29,
		"gadgets": 30,
		"anime_and_manga": 31,
		"cartoons_and_animations": 32}

	if difficulty not in valid_difficulties or category not in valid_categories:
		await ctx.send("Sorry, invalid difficulty/category! Please try again :P")
		return

	categoryNum = valid_categories[category]

	response = requests.get(f"https://opentdb.com/api.php?amount=1&category={categoryNum}&difficulty={difficulty}&type=multiple")

	info = response.json()["results"][0]
	info['correctAnswer'] = info.pop("correct_answer")
	info["incorrectAnswers"] = info.pop("incorrect_answers")

	return info

@bot.command(name="trivia", help="Queries a trivia API. \n\nDifficulty: easy/medium/hard\nCategory: history/music/science/etc, try >triviaapi_help or >opentdb_help for more detail\nAPI: triviaapi/opentdb, defaults to triviaapi, you can abbreviate with the first letter instead of the full word")
async def trivia(ctx, difficulty="hard", category="history", api="trivia"):

	# get from trivia api

	info = {}

	if api == "opentdb" or api == "o":
		info = await opentdb(ctx, difficulty, category)
	else:
		info = await triviaapi(ctx, difficulty, category)
	
	# print(response.json())
	# print(response.json()[0]["question"])

	# format + send embed

	category = category.capitalize()
	difficulty = difficulty.upper()

	correctAnswer = info["correctAnswer"]

	answers = info['incorrectAnswers']
	answers.append(correctAnswer)
	random.shuffle(answers)

	embed = discord.Embed(
			title=f"{category} ({difficulty})", 
			description=f"{info['question']}\n\n[1] {answers[0]}\n[2] {answers[1]}\n[3] {answers[2]}\n[4] {answers[3]}")
	embed.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar)
	embed.set_footer(text="Type the number of the correct answer.")

	await ctx.send(embed=embed)

	# get user input

	def check(msg):
		return msg.author == ctx.author and msg.channel == ctx.channel and msg.content in ["1", "2", "3", "4"]
	
	try:
		msg = await bot.wait_for("message", check=check, timeout=10)
	except asyncio.TimeoutError:
		await ctx.send("Sorry, reply faster next time :P")
		return

	userAns = int(msg.content)

	# validate + send results

	if (answers[userAns-1] == correctAnswer):
		await ctx.send("✅ Correct!")
	else:
		await ctx.send(f"❌ Incorrect! The correct answer is **[{answers.index(correctAnswer)+1}] {correctAnswer}**")


bot.run(TOKEN)