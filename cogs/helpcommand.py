import discord
from discord.ext import commands


async def setup(bot):
    await bot.add_cog(helpcommand(bot))


class helpcommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def helpcommand(self, ctx, arg = None):
        if arg is None:
            embed = discord.Embed(
                colour = discord.Colour.purple(),
                description = 'Categories:\nfun\nmisc\neconomy\nsideplus'
            )
            await ctx.send(embed=embed)

        if arg is not None:
            if arg == "fun":

                embed = discord.Embed(
                    colour = discord.Colour.blue(),
                    title = 'echo'
                )
                await ctx.send(embed=embed)
    
            elif arg == 'economy':
                embed = discord.Embed(
                    colour = discord.Colour.blue(),
                    title = 'bal\nwork\ngamble\nblackjack'
                )
                await ctx.send(embed=embed)
            
            elif arg == 'echo':

                embed = discord.Embed(
                    colour = discord.Colour.blue(),
                    title = 'repeats arguments given'
                )
                await ctx.send(embed=embed)
            elif arg == 'gamble':
                embed = discord.Embed(
                    colour = discord.Colour.blue(),
                    title = 'play a higher/lower game with bot'
                )
                await ctx.send(embed=embed)

