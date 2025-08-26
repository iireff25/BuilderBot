import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Remove default help command to avoid conflicts
bot.remove_command('help')

# Load templates
def load_templates():
    """Load server templates from JSON file"""
    try:
        with open('templates.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: templates.json not found!")
        return {}
    except json.JSONDecodeError:
        print("Error: Invalid JSON in templates.json!")
        return {}

# Store templates globally
TEMPLATES = load_templates()

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'🤖 {bot.user} has connected to Discord!')
    print(f'📊 Serving {len(bot.guilds)} guilds')
    print(f'👥 Serving {len(bot.users)} users')
    print('✅ Bot is ready!')

@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latency: {latency}ms')

@bot.command(name='help')
async def help_command(ctx):
    """Show all available commands"""
    embed = discord.Embed(
        title="🤖 Server Builder Bot Commands",
        description="Here are all the available commands:",
        color=0x00ff00
    )
    
    commands_info = {
        "!build <template>": "Build a server structure using a template (community, gaming, study, marketplace, tech)",
        "!deletebuild": "Delete all categories and channels created by the bot",
        "!server": "Show server information and statistics",
        "!addrole <name>": "Create a new role with default permissions",
        "!deleterole <name>": "Delete a role by name",
        "!ping": "Check bot latency",
        "!help": "Show this help message"
    }
    
    for cmd, desc in commands_info.items():
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="Bot created with ❤️")
    await ctx.send(embed=embed)

@bot.command(name='build')
async def build_server(ctx, template_name: str = None):
    """Build server structure based on template"""
    # Check permissions
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ You need Administrator permissions to use this command!")
        return
    
    if not template_name:
        # Show available templates
        embed = discord.Embed(
            title="📋 Available Templates",
            description="Use `!build <template>` to build a server structure:",
            color=0x00ff00
        )
        
        for template_key, template_data in TEMPLATES.items():
            embed.add_field(
                name=f"`{template_key}`", 
                value=f"**{template_data['server_name']}**\n{len(template_data['categories'])} categories, {len(template_data['roles'])} roles",
                inline=True
            )
        
        await ctx.send(embed=embed)
        return
    
    template_name = template_name.lower()
    if template_name not in TEMPLATES:
        await ctx.send(f"❌ Template '{template_name}' not found! Use `!build` to see available templates.")
        return
    
    template = TEMPLATES[template_name]
    guild = ctx.guild
    
    # Send initial message
    embed = discord.Embed(
        title="🏗️ Building Server Structure",
        description=f"Building **{template['server_name']}** template...",
        color=0x00ff00
    )
    embed.add_field(name="Categories", value=f"{len(template['categories'])}", inline=True)
    embed.add_field(name="Roles", value=f"{len(template['roles'])}", inline=True)
    embed.add_field(name="Total Channels", value=f"{sum(len(cat['channels']) for cat in template['categories'])}", inline=True)
    
    message = await ctx.send(embed=embed)
    
    try:
        # Rename server if template has a name
        if template.get('server_name'):
            await guild.edit(name=template['server_name'])
        
        # Delete all existing channels and categories first
        cleanup_embed = discord.Embed(
            title="🧹 Cleaning Server",
            description="Deleting all existing channels and categories...",
            color=0x00ff00
        )
        await message.edit(embed=cleanup_embed)
        
        deleted_count = 0
        for channel in guild.channels:
            if channel != ctx.channel:  # Don't delete the command channel
                try:
                    await channel.delete(reason=f"Cleanup before building {template['server_name']}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting channel {channel.name}: {e}")
        
        print(f"Deleted {deleted_count} existing channels/categories")
        
        # Create roles
        created_roles = []
        for role_data in template['roles']:
            print(f"Creating role: {role_data['name']}")
            try:
                # Convert permission strings to discord.Permissions
                permissions = discord.Permissions()
                for perm in role_data.get('permissions', []):
                    if hasattr(discord.Permissions, perm):
                        setattr(permissions, perm, True)
                
                role = await guild.create_role(
                    name=role_data['name'],
                    permissions=permissions,
                    reason=f"Server structure created by {bot.user.name}"
                )
                created_roles.append(role)
            except Exception as e:
                print(f"Error creating role {role_data['name']}: {e}")
        
        # Create categories and channels
        created_categories = []
        created_channels = []
        
        for i, category_data in enumerate(template['categories']):
            # Update progress
            progress_embed = discord.Embed(
                title="🏗️ Building Server Structure",
                description=f"Creating category **{category_data['name']}** ({i+1}/{len(template['categories'])})...",
                color=0x00ff00
            )
            progress_embed.add_field(name="Categories Created", value=f"{len(created_categories)}", inline=True)
            progress_embed.add_field(name="Channels Created", value=f"{len(created_channels)}", inline=True)
            progress_embed.add_field(name="Roles Created", value=f"{len(created_roles)}", inline=True)
            await message.edit(embed=progress_embed)
            try:
                print(f"Creating category: {category_data['name']}")
                # Create category
                category = await guild.create_category(
                    name=category_data['name'],
                    reason=f"Server structure created by {bot.user.name}"
                )
                created_categories.append(category)
                
                # Create channels in category
                for channel_data in category_data['channels']:
                    try:
                        if channel_data['type'] == 'voice':
                            # Create voice channel
                            channel = await guild.create_voice_channel(
                                name=channel_data['name'],
                                category=category,
                                reason=f"Server structure created by {bot.user.name}"
                            )
                        else:
                            # Create text channel
                            channel_kwargs = {
                                'name': channel_data['name'],
                                'category': category,
                                'reason': f"Server structure created by {bot.user.name}"
                            }
                            
                            # Add topic for text channels
                            if channel_data.get('topic'):
                                channel_kwargs['topic'] = channel_data['topic']
                            
                            channel = await guild.create_text_channel(**channel_kwargs)
                        
                        created_channels.append(channel)
                        print(f"Created channel: {channel.name} in category: {category.name}")
                        
                    except Exception as e:
                        print(f"Error creating channel {channel_data['name']}: {e}")
                        
            except Exception as e:
                print(f"Error creating category {category_data['name']}: {e}")
        
        # Final progress update
        final_progress_embed = discord.Embed(
            title="🏗️ Building Server Structure",
            description="✅ All categories and channels created! Finalizing...",
            color=0x00ff00
        )
        final_progress_embed.add_field(name="Categories Created", value=f"{len(created_categories)}", inline=True)
        final_progress_embed.add_field(name="Channels Created", value=f"{len(created_channels)}", inline=True)
        final_progress_embed.add_field(name="Roles Created", value=f"{len(created_roles)}", inline=True)
        await message.edit(embed=final_progress_embed)
        
        # Update success message
        success_embed = discord.Embed(
            title="✅ Server Structure Built Successfully!",
            description=f"**{template['server_name']}** template has been applied to your server.",
            color=0x00ff00
        )
        success_embed.add_field(name="Categories Created", value=f"{len(created_categories)}", inline=True)
        success_embed.add_field(name="Channels Created", value=f"{len(created_channels)}", inline=True)
        success_embed.add_field(name="Roles Created", value=f"{len(created_roles)}", inline=True)
        success_embed.add_field(name="Channels Cleaned", value=f"{deleted_count} old channels deleted", inline=True)
        
        if template.get('server_name'):
            success_embed.add_field(name="Server Renamed", value=f"✅ {template['server_name']}", inline=False)
        
        await message.edit(embed=success_embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error Building Server Structure",
            description=f"An error occurred: {str(e)}",
            color=0xff0000
        )
        await message.edit(embed=error_embed)

@bot.command(name='deletebuild')
async def delete_build(ctx):
    """Delete all categories and channels created by the bot"""
    # Check permissions
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ You need Administrator permissions to use this command!")
        return
    
    # Ask for confirmation
    embed = discord.Embed(
        title="⚠️ Confirm Deletion",
        description="This will delete ALL categories and channels in the server. This action cannot be undone!",
        color=0xffaa00
    )
    embed.add_field(name="Are you sure?", value="React with ✅ to confirm or ❌ to cancel", inline=False)
    
    message = await ctx.send(embed=embed)
    await message.add_reaction('✅')
    await message.add_reaction('❌')
    
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == message.id
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        
        if str(reaction.emoji) == '✅':
            # Delete all categories and channels
            deleted_count = 0
            
            for channel in ctx.guild.channels:
                if channel.category:  # Only delete channels in categories
                    try:
                        await channel.delete(reason=f"Cleanup by {bot.user.name}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"Error deleting channel {channel.name}: {e}")
            
            for category in ctx.guild.categories:
                try:
                    await category.delete(reason=f"Cleanup by {bot.user.name}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting category {category.name}: {e}")
            
            success_embed = discord.Embed(
                title="🗑️ Cleanup Complete",
                description=f"Successfully deleted {deleted_count} channels and categories.",
                color=0x00ff00
            )
            await ctx.send(embed=success_embed)
            
        else:
            await ctx.send("❌ Deletion cancelled.")
            
    except asyncio.TimeoutError:
        await ctx.send("⏰ Confirmation timed out. Deletion cancelled.")

@bot.command(name='server')
async def server_info(ctx):
    """Show server information and statistics"""
    guild = ctx.guild
    
    # Count channels by type
    text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
    voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
    categories = len(guild.categories)
    
    embed = discord.Embed(
        title=f"📊 {guild.name} Server Information",
        color=0x00ff00
    )
    
    embed.add_field(name="👑 Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
    embed.add_field(name="📅 Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    
    embed.add_field(name="💬 Text Channels", value=text_channels, inline=True)
    embed.add_field(name="🎵 Voice Channels", value=voice_channels, inline=True)
    embed.add_field(name="📁 Categories", value=categories, inline=True)
    
    embed.add_field(name="🛡️ Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="😀 Emojis", value=len(guild.emojis), inline=True)
    embed.add_field(name="🎨 Boost Level", value=guild.premium_tier, inline=True)
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    await ctx.send(embed=embed)

@bot.command(name='addrole')
async def add_role(ctx, *, role_name: str):
    """Create a new role with default permissions"""
    # Check permissions
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ You need 'Manage Roles' permission to use this command!")
        return
    
    try:
        # Create role with default permissions
        role = await ctx.guild.create_role(
            name=role_name,
            permissions=discord.Permissions(send_messages=True, read_message_history=True, connect=True, speak=True),
            reason=f"Role created by {ctx.author.name}"
        )
        
        embed = discord.Embed(
            title="✅ Role Created",
            description=f"Role **{role_name}** has been created successfully!",
            color=0x00ff00
        )
        embed.add_field(name="Role", value=role.mention, inline=True)
        embed.add_field(name="Created by", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error creating role: {str(e)}")

@bot.command(name='deleterole')
async def delete_role(ctx, *, role_name: str):
    """Delete a role by name"""
    # Check permissions
    if not ctx.author.guild_permissions.manage_roles:
        await ctx.send("❌ You need 'Manage Roles' permission to use this command!")
        return
    
    # Find the role
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    
    if not role:
        await ctx.send(f"❌ Role '{role_name}' not found!")
        return
    
    # Check if role is deletable
    if role.position >= ctx.guild.me.top_role.position:
        await ctx.send("❌ I cannot delete this role (it's higher than my highest role)!")
        return
    
    try:
        await role.delete(reason=f"Role deleted by {ctx.author.name}")
        
        embed = discord.Embed(
            title="🗑️ Role Deleted",
            description=f"Role **{role_name}** has been deleted successfully!",
            color=0x00ff00
        )
        embed.add_field(name="Deleted by", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error deleting role: {str(e)}")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param}")
    else:
        print(f"Error in command {ctx.command}: {error}")
        await ctx.send("❌ An unexpected error occurred. Please try again.")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN not found in environment variables!")
        exit(1)
    
    print("🚀 Starting Discord Server Builder Bot...")
    bot.run(token)
