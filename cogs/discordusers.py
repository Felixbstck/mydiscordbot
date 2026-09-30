import discord
import os
from discord.ext import commands, tasks
import random
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

async def setup(bot):
    await bot.add_cog(users(bot))


class users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.connection = get_connection()
        self.cursor = self.connection.cursor()   
        self.reconnect_if_disconnected.start()
  
        
    @tasks.loop(seconds=12000.0)
    
    async def reconnect_if_disconnected(self):
        if self.connection.is_connected():
            return
        self.connection = get_connection()
        self.cursor = self.connection.cursor()
        print("Successfully reconnected to database !")
      
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        try:
            self.cursor.execute("""INSERT INTO users VALUES
            (%s,%s,%s,%s) """, (message.author.id, message.author.name, message.author.discriminator, 100))
            self.connection.commit()
            print(f'added user {message.author}')
        except mysql.connector.errors.IntegrityError:
            pass

    @commands.command(name='usercount')
    async def userlist_command(self, ctx):
        self.cursor.execute("SELECT count(*) FROM users")
        print(self.cursor.fetchall())
        print('fetched!')

    ##GAMBLE COMMAND

    @commands.command()

    async def gamble(self, ctx, amount: int = None):
        if amount <= 0:
            await ctx.send("You need to gamble a positive number!!")
            return
        
        money = self.cursor.execute("""
        SELECT currency
        FROM users
        WHERE id = %s""", (ctx.author.id,))
        money = self.cursor.fetchone() #fetchone is compulsory

        if amount is not None:
            if  amount > money[0] : #checks if i can afford the bet
                await ctx.send(embed = discord.Embed(title = "Oops...", description = "You're too broke to gamble that much !", colour = discord.Colour.red()))
                return
            number = random.randint(0, 100)
            botnumb = random.randint(0, 100)
            if number > botnumb: 
                self.cursor.execute("UPDATE users SET currency = currency + %s WHERE id = %s", (amount, ctx.author.id))
                self.connection.commit()
                
                temp_money = money[0] + amount
                
                embed = discord.Embed(title = "You won !", description = f"You rolled {str(number)} and the computer rolled {str(botnumb)}. You now have £{str(temp_money)}.", colour = discord.Colour.green())
                await ctx.send(embed=embed)
                
            elif number == botnumb:
                await ctx.send("It's a draw. Nothing happens.") 
            else:
                self.cursor.execute("UPDATE users SET currency = currency - %s WHERE id = %s", (amount, ctx.author.id))
                self.connection.commit()
                
                temp_money = money[0] - amount
                
                embed = discord.Embed(title = "You lost...", description = f"You rolled {str(number)} and the computer rolled {str(botnumb)}. You now have £{str(temp_money)}.", colour = discord.Colour.red())
                await ctx.send(embed=embed)
                
                
        if amount is None:
            embed = discord.Embed(title = 'You need to enter an amount to bet !', colour = discord.Colour.red())
            await ctx.send(embed=embed)  

    @commands.command()

    async def work(self, ctx):
        earned = random.randint(0, 100)
        balance = self.cursor.execute("SELECT currency FROM users WHERE id = %s", (ctx.author.id,))
        balance = self.cursor.fetchone()[0]
        if balance > 100: # if money over 100 cant work
            await ctx.send(embed=discord.Embed(title='Oops', description = "You're too rich to work !", colour = discord.Colour.red()))
            return

        self.cursor.execute("UPDATE users SET currency = currency + %s WHERE id = %s", (earned, ctx.author.id)) #have to format
        self.connection.commit()
        
        embed = discord.Embed(
            title = "Good job",
            description = f'You earned £{str(earned)}',
            colour = discord.Colour.green())

        await ctx.send(embed=embed)
    
    @commands.command()

    async def bal(self, ctx):
        balance = self.cursor.execute("SELECT currency FROM users WHERE id = %s", (ctx.author.id,))
        balance = self.cursor.fetchone()
        balance = balance[0]
        if balance is None:
            balance = 100
        
        embed = discord.Embed(
            title = f"{ctx.author.name}#{ctx.author.discriminator}'s Balance",
            description = f'You have £{balance}',
            colour = discord.Colour.green()
        )
        await ctx.send(embed=embed)
            
    @commands.command()

    async def rich(self, ctx):
        rich_list = self.cursor.execute("SELECT name, discriminator, currency FROM users ORDER BY currency DESC LIMIT 5")
        rich_list = self.cursor.fetchall()
        embed = discord.Embed(
            colour = discord.Colour.green(),
            title = "Top 5 rich list",
            description = f"1 - {rich_list[0][0]}#{rich_list[0][1]} £{rich_list[0][2]}\n2 - {rich_list[1][0]}#{rich_list[1][1]} £{rich_list[1][2]}\n3 - {rich_list[2][0]}#{rich_list[2][1]} £{rich_list[2][2]}\n4 - {rich_list[3][0]}#{rich_list[3][1]} £{rich_list[3][2]}\n5- {rich_list[4][0]}#{rich_list[4][1]} £{rich_list[4][2]}\n"
        )
        await ctx.send(embed=embed)