import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

bot = commands.Bot(command_prefix='!', intents=intents)

user_balances = {}
user_wins = {}  # Track consecutive wins for each user

UPI_ID = "lalit008@fam"  # Replace with your actual UPI ID

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def deposit(ctx, amount: float):
    if amount <= 0:
        await ctx.send("❌ Please enter an amount greater than 0.")
        return
    await ctx.send(
        f"💸 To deposit ₹{amount}, please send the amount to UPI ID: **{UPI_ID}**\n"
        "After payment, please ask an admin to update your balance using `!addbalance @user <amount>`."
    )

@bot.command()
@commands.has_permissions(administrator=True)
async def addbalance(ctx, member: discord.Member, amount: float):
    if amount <= 0:
        await ctx.send("❌ Please enter an amount greater than 0.")
        return
    user_balances[member.id] = user_balances.get(member.id, 0) + amount
    await ctx.send(f"✅ Added ₹{amount} to {member.mention}'s balance.")

@bot.command()
async def balance(ctx):
    bal = user_balances.get(ctx.author.id, 0)
    await ctx.send(f"💰 {ctx.author.mention}, your balance is ₹{bal:.2f}")

class CustomHelp(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help - Commands List", color=discord.Color.blue())

        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            if not filtered:
                continue

            # Filter out 'addbalance' command for everyone
            filtered = [cmd for cmd in filtered if cmd.name != "addbalance"]

            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                embed.add_field(
                    name=cog.qualified_name if cog else "No Category",
                    value="\n".join(command_signatures),
                    inline=False,
                )

        channel = self.get_destination()
        await channel.send(embed=embed)

# Then, set your bot's help command:
bot.help_command = CustomHelp()

@bot.command()
async def cf(ctx, amount: float):
    bal = user_balances.get(ctx.author.id, 0)
    if amount <= 0:
        await ctx.send("❌ Please enter an amount greater than 0.")
        return
    if bal < amount:
        await ctx.send("❌ You don't have enough balance to bet that amount.")
        return

    user_wins.setdefault(ctx.author.id, 0)

    # Deduct bet amount
    user_balances[ctx.author.id] = bal - amount

    # Force lose if user won twice consecutively
    if user_wins[ctx.author.id] >= 2:
        user_wins[ctx.author.id] = 0
        await ctx.send(f"😞 Sorry {ctx.author.mention}, you lost ₹{amount}. New balance: ₹{user_balances[ctx.author.id]:.2f}")
        return

    # 50% chance to win or lose
    if random.choice([True, False]):
        # Win: add double the bet amount
        user_balances[ctx.author.id] += amount * 2
        user_wins[ctx.author.id] += 1
        await ctx.send(f"🎉 Congrats {ctx.author.mention}, you won ₹{amount}! New balance: ₹{user_balances[ctx.author.id]:.2f}")
    else:
        # Lose: reset win count
        user_wins[ctx.author.id] = 0
        await ctx.send(f"😞 Sorry {ctx.author.mention}, you lost ₹{amount}. New balance: ₹{user_balances[ctx.author.id]:.2f}")

import os
token = os.getenv("DISCORD_TOKEN")
bot.run(token)






