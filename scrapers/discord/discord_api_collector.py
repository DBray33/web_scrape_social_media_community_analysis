"""
Discord Data Collector - Uses Discord's official API to collect information
about Discord servers where the bot has been invited.
"""
import os
import discord
from discord.ext import commands
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord bot token (you'll need to create a bot at https://discord.com/developers/applications)
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Initialize Discord client
intents = discord.Intents.default()
intents.members = True  # Privileged intent, needs to be enabled in Developer Portal
bot = commands.Bot(command_prefix='!', intents=intents)

# Store server data
server_data = []

@bot.event
async def on_ready():
    """Run when the bot is ready"""
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    
    # Collect data from all servers the bot is in
    for guild in bot.guilds:
        try:
            # Get basic server info
            server_info = {
                'platform': 'Discord',
                'name': guild.name,
                'id': guild.id,
                'member_count': guild.member_count,
                'description': guild.description if guild.description else '',
                'creation_date': guild.created_at.strftime('%Y-%m-%d'),
                'icon_url': str(guild.icon.url) if guild.icon else '',
                'is_large': guild.large,  # Discord considers servers with >250 members as "large"
                'features': ", ".join(guild.features),
                'channels': [],
                'roles': [],
                'scraped_date': datetime.now().strftime('%Y-%m-%d')
            }
            
            # Get channel info
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    channel_info = {
                        'name': channel.name,
                        'type': 'text',
                        'topic': channel.topic if channel.topic else '',
                        'position': channel.position,
                        'is_nsfw': channel.is_nsfw(),
                        'category': channel.category.name if channel.category else 'None'
                    }
                    server_info['channels'].append(channel_info)
            
            # Get role info
            for role in guild.roles:
                role_info = {
                    'name': role.name,
                    'color': str(role.color),
                    'position': role.position,
                    'is_managed': role.managed,
                    'is_mentionable': role.mentionable
                }
                server_info['roles'].append(role_info)
            
            # Add to our data collection
            server_data.append(server_info)
            print(f"Collected data from {guild.name}")
            
        except Exception as e:
            print(f"Error collecting data from {guild.name}: {e}")
    
    # Export data after collecting from all servers
    await export_data()
    
    # Exit after data collection
    await bot.close()

async def export_data():
    """Export the collected data to CSV and JSON"""
    if not server_data:
        print("No data collected")
        return
    
    # Create output directory
    os.makedirs('scraped_data/discord', exist_ok=True)
    
    # Basic server info to DataFrame
    basic_info = []
    for server in server_data:
        # Create a copy without the nested lists
        server_copy = server.copy()
        
        # Extract number of channels and roles
        server_copy['num_channels'] = len(server_copy.pop('channels'))
        server_copy['num_roles'] = len(server_copy.pop('roles'))
        
        basic_info.append(server_copy)
    
    # Create DataFrame
    df = pd.DataFrame(basic_info)
    
    # Export to CSV
    csv_path = os.path.join('scraped_data', 'discord', 'servers.csv')
    df.to_csv(csv_path, index=False)
    
    # Export full data to JSON
    import json
    json_path = os.path.join('scraped_data', 'discord', 'servers_full.json')
    with open(json_path, 'w') as f:
        json.dump(server_data, f, indent=4)
    
    print(f"Exported data for {len(server_data)} servers to {csv_path} and {json_path}")

def run_bot():
    """Run the Discord bot"""
    if not TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not found in environment variables")
        print("You need to create a Discord bot at https://discord.com/developers/applications")
        print("and add the token to your .env file as DISCORD_BOT_TOKEN=your_token_here")
        return
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Error running Discord bot: {e}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("DISCORD SERVER DATA COLLECTOR")
    print("="*50)
    
    print("Starting Discord bot to collect server data...")
    run_bot()