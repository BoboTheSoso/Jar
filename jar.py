#dependencies needed to code:
#discord.py
# python-dotenv
#SQLite3 (for database interactions)


#import necessary libraries for python discord bot
import os
import discord 
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
import sqlite3

from jarDB import get_connection, add_dollar, initialize_database, pull_user_dollars, pull_submitted_dollars, get_dollar_amount, get_top_5_dollars
initialize_database() #initialize the database when the bot starts

#get token and guild from .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#initialize discord client with intents
intents = discord.Intents.default()
intents.members = True #enable member intents
intents.message_content = True #enable message content intents

bot = commands.Bot(command_prefix='!', intents=intents) #create bot instance with command prefix '!'

#create discord client
#client = discord.Client(intents=intents)

    
@bot.event #For Emily my love <3
async def on_message(message):
    #ignore messages sent by the bot itself
    if message.author == bot.user:
        return
    
    #check if the message content is "amongus" (case-insensitive)
    if message.content.lower() == 'amongus':
        await message.channel.send(f'3(\\_)x(\\_)E') #reply with a gift

    await bot.process_commands(message) #process commands after handling the message event

#Create a bot command for the bot to respond to "!ding" with Janice
@bot.command(name='bing')
async def ping(ctx):
    await ctx.send('Bing bong, Janice!') #reply with Janice when the command is used

#Database functions for the dollar jar feature:
#Pull stats for specific user $ amount in the jar:
@bot.tree.command(name='jar_stats', description = "Get stats about a specific user's dollars in the jar")
async def jar_stats(interaction: discord.Interaction, user: discord.Member):
    guild_id = interaction.guild_id #get the guild ID from the interaction
    assigned_to = user.id #get the user ID of the specified user
    amount = get_dollar_amount(interaction.guild_id, assigned_to) #get the dollar amount for the specified user in the guild
    await interaction.response.send_message(f'{user.name} has {amount} dollars in the jar!') #reply with the dollar amount for the specified user

#Pull last 5 dollars and labels for a specific user:
@bot.tree.command(name='jar_recent', description = "Get the last 5 dollars added for a specific user")
async def jar_recent(interaction: discord.Interaction, user: discord.Member):
    guild_id = interaction.guild_id #get the guild ID from the interaction
    assigned_to = user.id #get the user ID of the specified user
    dollars = pull_user_dollars(guild_id, assigned_to) #pull all dollars for the specified user in the guild
    recent_dollars = dollars[-5:] #get the last 5 dollars from the list
    if not recent_dollars:
        await interaction.response.send_message(f'{user.name} has no dollars in the jar!') #reply if the user has no dollars in the jar
        return
    response = f'Last 5 dollars for {user.name}:\n' #start building the response message with a header
    for dollar in recent_dollars: #iterate through the recent dollars and add them to the response message
        submission_by = dollar[3] #get the submission_by field from the dollar record
        label = dollar[4] #get the label field from the dollar record
        response += f'- {label} (submitted by <@{submission_by}>)\n' #add each dollar's label and submitter to the response message
    await interaction.response.send_message(response) #reply with the list of recent dollars for the specified user
    
#Pull all dollars and labels for a specific user:
@bot.tree.command(name='jar_all', description = "Get all dollars and labels for a specific user")
async def jar_all(interaction: discord.Interaction, user: discord.Member):
    guild_id = interaction.guild_id #get the guild ID from the interaction
    assigned_to = user.id #get the user ID of the specified user
    dollars = pull_user_dollars(guild_id, assigned_to) #pull all dollars for the specified user in the guild
    if not dollars:
        await interaction.response.send_message(f'{user.name} has no dollars in the jar!') #reply if the user has no dollars in the jar
        return
    response = f'All dollars for {user.name}:\n' #start building the response message with a header
    for dollar in dollars: #iterate through all dollars and add them to the response message
        submission_by = dollar[3] #get the submission_by field from the dollar record
        label = dollar[4] #get the label field from the dollar record
        response += f'- {label} (submitted by <@{submission_by}>)\n' #add each dollar's label and submitter to the response message
    await interaction.response.send_message(response) #reply with the list of all dollars for the specified user

#Pull top 5 users with the most dollars in the jar for the guild:
@bot.tree.command(name='jar_leaderboard', description = "Get the top 5 users with the most dollars in the jar for the guild")
async def jar_leaderboard(interaction: discord.Interaction):
    guild_id = interaction.guild_id #get the guild ID from the interaction
    top_users = get_top_5_dollars(guild_id) #get the top 5 users with the most dollars in the jar for the guild
    if not top_users:
        await interaction.response.send_message('No dollars in the jar yet!') #reply if there are no dollars in the jar
        return
    response = 'Jar Leaderboard:\n' #start building the response message with a header
    for user in top_users: #iterate through the top users and add them to the response message
        user_id = user[0] #get the user ID from the query result
        amount = user[1] #get the dollar amount from the query result
        response += f'- <@{user_id}>: {amount} dollars\n' #add each user's mention and dollar amount to the response message
    await interaction.response.send_message(response) #reply with the leaderboard of top users in the jar

#Pull all dollars submitted by a specific user:
@bot.tree.command(name='jar_submissions', description = "Get all dollars submitted by a specific user in the guild")
async def jar_submissions(interaction: discord.Interaction, user: discord.Member):
    guild_id = interaction.guild_id #get the guild ID from the interaction
    submission_by = user.id #get the user ID of the specified user
    dollars = pull_submitted_dollars(guild_id, submission_by) #pull all dollars submitted by the specified user in the guild
    if not dollars:
        await interaction.response.send_message(f'{user.name} has not submitted any dollars to the jar!') #reply if the user has not submitted any dollars to the jar
        return
    response = f'Dollars submitted by {user.name}:\n' #start building the response message with a header
    for dollar in dollars: #iterate through the submitted dollars and add them to the response message
        assigned_to = dollar[2] #get the assigned_to field from the dollar record
        label = dollar[4] #get the label field from the dollar record
        response += f'- {label} (assigned to <@{assigned_to}>)\n' #add each dollar's label and assigned user to the response message
    await interaction.response.send_message(response) #reply with the list of dollars submitted by the specified user

#Add a dollar for self or someone else with label and optional user mention using a modal form
class AddDollarModal(discord.ui.Modal, title="Add a dollar to the jar"):
    def __init__(self, assigned_to=None):
        super().__init__()
        self.assigned_to = assigned_to

        # Text input for the label
        self.label_input = discord.ui.TextInput(
            label="What did they do?",
            placeholder="Describe the flavor of harassment...",
            required=True,
            max_length=200
        )
        self.add_item(self.label_input)

    async def on_submit(self, interaction: discord.Interaction):
        # Save to DB
        add_dollar(
            guild_id=interaction.guild_id,
            assigned_to=self.assigned_to,
            submission_by=interaction.user.id,
            label=self.label_input.value
        )

        await interaction.response.send_message(
            f"Dollar added for <@{self.assigned_to}>: {self.label_input.value}",
            ephemeral=False
        )

class JarView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) #set timeout to None to keep the view active indefinitely
        #self.value = None

    @discord.ui.button(label='Self-report', style=discord.ButtonStyle.green)
    async def self_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AddDollarModal(assigned_to=interaction.user.id)) #open the modal to add a dollar when the button is clicked

    @discord.ui.button(label='Report for someone else', style=discord.ButtonStyle.blurple)
    async def report_other(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = UserSelectView(callback=lambda user_id: AddDollarModal(assigned_to=user_id))
        await interaction.response.send_message('Select user assignment:', view=view) #open the user select view to choose a user to assign the dollar to when the button is clicked

#User select view for choosing a userID to call into another view (like the AddDollarModal) that needs a userID passed in
class UserSelectView(discord.ui.View):
    def __init__(self, callback):
        super().__init__(timeout=None)
        self.callback = callback

        # Add a UserSelect to the view
        self.user_select = discord.ui.UserSelect(
            placeholder="Select a user",
            min_values=1,
            max_values=1,
            custom_id="user_select"
        )
        self.user_select.callback = self.user_selected #set the callback for when a user is selected
        self.add_item(self.user_select)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Cancelled", view=None)

    async def user_selected(self, interaction: discord.Interaction):
        from typing import Any, cast

        data = cast(dict[str, Any], interaction.data or {})  # type: ignore
        values = data.get("values")
        if not values:
            await interaction.response.send_message("No user selected.", ephemeral=True)
            return

        selected_user_id = int(values[0]) #get the selected user ID from the interaction data
        modal_class = self.callback(selected_user_id)  # pass ID to your modal
        await interaction.response.send_modal(modal_class)

    async def on_timeout(self):
        for item in self.children:
            setattr(item, 'disabled', True) #disable all items in the view when it times out
        # optionally update the message if you stored it as self.message


@bot.tree.command(name='jar', description = "Open the dollar jar")
async def jar(interaction: discord.Interaction):
    view = JarView()
    await interaction.response.send_message('Dollar jar', view=view, ephemeral=False)
    

#event handler for when the bot is ready
@bot.event
async def on_ready():
    await bot.tree.sync() #sync the command tree to register slash commands
    print('slash commands synced!')
    #get the guild by name
    guild = discord.utils.get(bot.guilds, name=GUILD)
    #check if guild is found
    if guild is None:
        print(f'{GUILD} not found!')
        return
    #print guild and member information
    print(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'
    )
    #list all members in the guild
    members = '\n - '.join([member.name for member in guild.members]) #create list of member names
    print(f'Guild Members:\n - {members}') #print list of members

if TOKEN is None:
    raise RuntimeError("DISCORD_TOKEN not found in environment variables. Please set it in the .env file.")
bot.run(TOKEN) #run the bot with the specified token
