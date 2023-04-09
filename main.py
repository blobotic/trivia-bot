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
		"al": "arts_and_literature",
		"ft": "films_and_tv",
		"fd": "food_and_drink",
		"gk": "general_knowledge",
		"geo": "geography",
		"hist": "history",
		"mus": "music",
		"sci": "science",
		"soc": "society_and_culture",
		"sports": "sport_and_culture"
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


async def opentdb(ctx, difficulty, category):

	difficulty = difficulty.lower()
	category = category.lower()

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

@bot.command(name="trivia")
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