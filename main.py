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

@bot.command(name="trivia")
async def trivia(ctx, difficulty, category):

	# get from trivia api

	difficulty = difficulty.lower()
	category = category.lower()

	valid_difficulties = ["easy", "medium", "hard"]
	valid_categories = ["arts_and_literature", "film_and_tv", "food_and_drink", "general_knowledge", "geography", "history", "music", "science", "society_and_culture", "sport_and_culture"]

	if difficulty not in valid_difficulties or category not in valid_categories:
		await ctx.send("Sorry, invalid difficulty/category! Please try again :P")
		return

	response = requests.get(f"https://the-trivia-api.com/api/questions?limit=1&categories={category}&difficulty={difficulty}")

	# print(response.json())
	# print(response.json()[0]["question"])

	# format + send embed

	category = category.capitalize()
	difficulty = difficulty.upper()

	correctAnswer = response.json()[0]["correctAnswer"]

	answers = response.json()[0]['incorrectAnswers']
	answers.append(correctAnswer)
	random.shuffle(answers)

	embed = discord.Embed(
			title=f"{category} ({difficulty})", 
			description=f"{response.json()[0]['question']}\n\n[1] {answers[0]}\n[2] {answers[1]}\n[3] {answers[2]}\n[4] {answers[3]}")
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