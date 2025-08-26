import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Bot owner information
BOT_OWNER_ID = 1179595808585285704
BOT_OWNER_NAME = "Server Builder Pro"
BOT_VERSION = "v3.0"
TOPGG_BOT_ID = "1409790273118273556"
TOPGG_REVIEW_URL = f"https://top.gg/bot/{TOPGG_BOT_ID}#reviews"
TOPGG_VOTE_URL = f"https://top.gg/bot/{TOPGG_BOT_ID}"

bot = commands.Bot(command_prefix='!', intents=intents)

# Remove default help command to avoid conflicts
bot.remove_command('help')

# Note: We use the built-in CommandTree that discord.py automatically creates
# No need to create a new one as it causes ClientException
# The bot.tree is already available for registering slash commands

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

# Build storage system
SAVED_BUILDS = {}

def generate_build_code():
    """Generate a unique 8-character build code"""
    import random
    import string
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if code not in SAVED_BUILDS:
            return code

def save_server_structure(guild):
    """Save the complete server structure"""
    build_data = {
        'server_name': guild.name,
        'categories': [],
        'roles': []
    }
    
    # Save categories and their channels
    for category in guild.categories:
        category_data = {
            'name': category.name,
            'channels': []
        }
        
        # Save channels in this category
        for channel in category.channels:
            channel_data = {
                'name': channel.name,
                'type': 'voice' if isinstance(channel, discord.VoiceChannel) else 'text'
            }
            
            # Add topic for text channels
            if isinstance(channel, discord.TextChannel) and channel.topic:
                channel_data['topic'] = channel.topic
                
            category_data['channels'].append(channel_data)
            
        build_data['categories'].append(category_data)
    
    # Save roles (excluding @everyone and bot roles)
    for role in guild.roles:
        if role.name != "@everyone" and role != guild.me.top_role:
            role_data = {
                'name': role.name,
                'permissions': []
            }
            
            # Convert permissions to strings
            for perm, value in role.permissions:
                if value:
                    role_data['permissions'].append(perm)
                    
            build_data['roles'].append(role_data)
    
    return build_data

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f'🤖 {bot.user} has connected to Discord!')
    print(f'📊 Serving {len(bot.guilds)} guilds')
    print(f'👥 Serving {len(bot.users)} users')
    print(f'👑 Bot Owner: <@{BOT_OWNER_ID}>')
    print('✅ Bot is ready!')
    
    # Sync slash commands globally
    try:
        print("🔄 Syncing slash commands with Discord...")
        synced = await bot.tree.sync()
        print(f"✅ Successfully synced {len(synced)} slash commands globally!")
        print("📋 Available slash commands:")
        for cmd in synced:
            print(f"   /{cmd.name} - {cmd.description}")
    except Exception as e:
        print(f"❌ Error syncing slash commands: {e}")
        print("💡 Make sure your bot has 'applications.commands' scope enabled!")
    
    # Set modern bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"Server Builder Pro {BOT_VERSION} | /help"
        )
    )

@bot.command(name='ping')
async def ping(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="⚡ System Status",
        description=f"**Latency:** `{latency}ms`\n**Status:** `Online`\n**Version:** `{BOT_VERSION}`",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
    await ctx.send(embed=embed)

@bot.command(name='builds')
async def list_saved_builds(ctx):
    """List all saved build codes (Administrator only)"""
    # Check permissions - Administrator required
    if not ctx.author.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="**Administrator permissions required**\nYou need elevated permissions to view saved builds.",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        await ctx.send(embed=embed)
        return
    
    if not SAVED_BUILDS:
        embed = discord.Embed(
            title="📋 No Saved Builds",
            description="**No server structures have been saved yet.**\nUse `!savebuild` to save your first server structure!",
            color=0xffaa00,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title="💾 Saved Server Builds",
        description=f"**{len(SAVED_BUILDS)}** saved server structures available:",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    
    # List all saved builds with details
    for build_code, build_data in SAVED_BUILDS.items():
        total_categories = len(build_data['categories'])
        total_channels = sum(len(cat['channels']) for cat in build_data['categories'])
        total_roles = len(build_data['roles'])
        
        embed.add_field(
            name=f"🔑 `{build_code}`",
            value=f"**{build_data['server_name']}**\n📁 `{total_categories}` categories • 💬 `{total_channels}` channels • 🛡️ `{total_roles}` roles",
            inline=False
        )
    
    embed.add_field(
        name="📋 Usage",
        value="Use `!build <code>` to deploy any of these saved structures\nUse `!removebuild <code>` to delete a saved build",
        inline=False
    )
    
    embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
    await ctx.send(embed=embed)

@bot.command(name='removebuild')
async def remove_saved_build(ctx, build_code: str):
    """Remove a saved build code (Administrator only)"""
    # Check permissions - Administrator required
    if not ctx.author.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="**Administrator permissions required**\nYou need elevated permissions to remove saved builds.",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        await ctx.send(embed=embed)
        return
    
    if not build_code:
        embed = discord.Embed(
            title="❌ Missing Build Code",
            description="**Please provide a build code to remove.**\nUsage: `!removebuild <code>`",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        await ctx.send(embed=embed)
        return
    
    # Convert to uppercase for consistency
    build_code = build_code.upper()
    
    if build_code not in SAVED_BUILDS:
        embed = discord.Embed(
            title="❌ Build Code Not Found",
            description=f"**Build code `{build_code}` not found!**\nUse `!builds` to see available saved builds.",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        await ctx.send(embed=embed)
        return
    
    # Get build data before removing
    build_data = SAVED_BUILDS[build_code]
    server_name = build_data['server_name']
    total_categories = len(build_data['categories'])
    total_channels = sum(len(cat['channels']) for cat in build_data['categories'])
    total_roles = len(build_data['roles'])
    
    # Remove the build
    del SAVED_BUILDS[build_code]
    
    embed = discord.Embed(
        title="🗑️ Build Removed Successfully",
        description=f"**Build code `{build_code}` has been removed from saved builds.**",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="🔑 Removed Code", value=f"`{build_code}`", inline=True)
    embed.add_field(name="📊 Build Details", value=f"**{server_name}**\n📁 `{total_categories}` categories • 💬 `{total_channels}` channels • 🛡️ `{total_roles}` roles", inline=False)
    embed.add_field(name="📋 Remaining Builds", value=f"`{len(SAVED_BUILDS)}` saved builds remaining", inline=True)
    
    embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
    await ctx.send(embed=embed)

@bot.command(name='savebuild')
async def save_build(ctx):
    """Save the current server structure with a unique code (Administrator only)"""
    # Check permissions - Administrator required
    if not ctx.author.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="**Administrator permissions required**\nYou need elevated permissions to save server structures.",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        await ctx.send(embed=embed)
        return
    
    try:
        # Send initial message
        embed = discord.Embed(
            title="💾 Saving Server Structure",
            description="**Analyzing current server structure...**\nPlease wait while I scan your server.",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        message = await ctx.send(embed=embed)
        
        # Save the server structure
        build_data = save_server_structure(ctx.guild)
        
        # Generate unique code
        build_code = generate_build_code()
        
        # Store the build data
        SAVED_BUILDS[build_code] = build_data
        
        # Count components
        total_categories = len(build_data['categories'])
        total_channels = sum(len(cat['channels']) for cat in build_data['categories'])
        total_roles = len(build_data['roles'])
        
        # Create success embed
        success_embed = discord.Embed(
            title="✅ Server Structure Saved!",
            description=f"**Your server structure has been saved successfully!**\nUse this code to recreate it on any server:",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        success_embed.add_field(
            name="🔑 Build Code", 
            value=f"`{build_code}`", 
            inline=False
        )
        success_embed.add_field(name="📁 Categories", value=f"`{total_categories}`", inline=True)
        success_embed.add_field(name="💬 Channels", value=f"`{total_channels}`", inline=True)
        success_embed.add_field(name="🛡️ Roles", value=f"`{total_roles}`", inline=True)
        success_embed.add_field(
            name="📋 Usage", 
            value=f"Use `!build {build_code}` to recreate this structure on any server", 
            inline=False
        )
        # Add Top.gg voting prompt
        success_embed.add_field(
            name="⭐ Support BuilderBot!",
            value=f"**Enjoying the bot? Please vote for us on Top.gg!**\n[Vote Now]({TOPGG_VOTE_URL}) • [Leave Review]({TOPGG_REVIEW_URL})",
            inline=False
        )
        success_embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        
        await message.edit(embed=success_embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Save Failed",
            description=f"**Error:** `{str(e)}`\nPlease try again or contact support.",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        error_embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        await message.edit(embed=error_embed)

@bot.command(name='sync')
async def sync_commands(ctx):
    """Sync slash commands (Owner only)"""
    if ctx.author.id != BOT_OWNER_ID:
        await ctx.send("❌ This command is only available to the bot owner!")
        return
    
    try:
        await ctx.send("🔄 Syncing slash commands...")
        synced = await bot.tree.sync()
        embed = discord.Embed(
            title="✅ Commands Synced Successfully!",
            description=f"**{len(synced)}** slash commands have been synced with Discord.",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="📋 Synced Commands", 
            value="\n".join([f"`/{cmd.name}` - {cmd.description}" for cmd in synced]),
            inline=False
        )
        embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error syncing commands: {str(e)}")

@bot.command(name='help')
async def help_command(ctx):
    """Show all available commands"""
    embed = discord.Embed(
        title="🚀 Server Builder Pro - Command Center",
        description="**Next-Generation Discord Server Management**\nBuild, customize, and manage your server with professional templates",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    
    commands_info = {
        "**🔧 Core Commands:**": "",
        "`!build <template>`": "🏗️ Deploy complete server structure",
        "`!deletebuild`": "🗑️ Clean slate - remove all structure",
        "`!server`": "📊 Advanced server analytics",
        "`!ping`": "⚡ System performance check",
        "`!help`": "📖 Command documentation",
        "**⚡ Slash Commands:**": "",
        "`/build`": "🎯 Interactive template deployment",
        "`/deletebuild`": "🔄 One-click server reset",
        "`/server`": "📈 Real-time server metrics",
        "`/ping`": "⚡ Performance diagnostics",
        "`/help`": "📚 Command reference"
    }
    
    for cmd, desc in commands_info.items():
        if cmd.startswith("**"):
            embed.add_field(name=cmd, value=desc, inline=False)
        else:
            embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.add_field(
        name="🎨 Available Templates", 
        value="**Community** • **Gaming** • **Study** • **Marketplace** • **Tech**", 
        inline=False
    )
    
    # Add Top.gg support section
    embed.add_field(
        name="⭐ Support BuilderBot!",
        value=f"**If you're enjoying BuilderBot, please consider leaving a review on Top.gg!**\n[Leave Review]({TOPGG_REVIEW_URL}) • [Vote for us]({TOPGG_VOTE_URL})",
        inline=False
    )
    
    embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    
    await ctx.send(embed=embed)

@bot.command(name='build')
async def build_server(ctx, build_code: str = None):
    """Build server structure based on template or saved build code"""
    # Check permissions - Administrator required
    if not ctx.author.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="**Administrator permissions required**\nYou need elevated permissions to build server structures.",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        await ctx.send(embed=embed)
        return
    
    if not build_code:
        # Show available templates and build options
        embed = discord.Embed(
            title="🎨 Available Build Options",
            description="**Choose a template or use a saved build code:**",
            color=0x00ff00
        )
        
        # Show templates
        embed.add_field(
            name="📋 Templates", 
            value="Use `!build <template>` with these templates:", 
            inline=False
        )
        
        for template_key, template_data in TEMPLATES.items():
            embed.add_field(
                name=f"`{template_key}`", 
                value=f"**{template_data['server_name']}**\n`{len(template_data['categories'])}` categories • `{len(template_data['roles'])}` roles",
                inline=True
            )
        
        # Show saved builds info
        embed.add_field(
            name="💾 Saved Builds", 
            value=f"Use `!build <code>` with a saved build code\n**Available saved builds:** `{len(SAVED_BUILDS)}`", 
            inline=False
        )
        
        embed.add_field(
            name="📋 Usage Examples", 
            value="`!build community` - Use community template\n`!build ABC12345` - Use saved build code", 
            inline=False
        )
        
        await ctx.send(embed=embed)
        return
    
    # Check if it's a saved build code (8 characters, alphanumeric)
    if len(build_code) == 8 and build_code.isalnum():
        # Try to find saved build
        if build_code.upper() in SAVED_BUILDS:
            template = SAVED_BUILDS[build_code.upper()]
            build_type = "saved build"
        else:
            embed = discord.Embed(
                title="❌ Build Code Not Found",
                description=f"**Build code `{build_code}` not found!**\nMake sure the code is correct or use `!savebuild` to create a new one.",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
            await ctx.send(embed=embed)
            return
    else:
        # Try to find template
        template_name = build_code.lower()
        if template_name not in TEMPLATES:
            embed = discord.Embed(
                title="❌ Template Not Found",
                description=f"**Template `{build_code}` not found!**\nUse `!build` to see available templates and build codes.",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
            await ctx.send(embed=embed)
            return
        
        template = TEMPLATES[template_name]
        build_type = "template"
    guild = ctx.guild
    
    # Send initial message
    embed = discord.Embed(
        title="🚀 Deploying Server Structure",
        description=f"**Source:** `{build_type}`\n**Name:** `{template['server_name']}`\n**Status:** Initializing deployment...",
        color=0x00ff00
    )
    embed.add_field(name="📁 Categories", value=f"`{len(template['categories'])}`", inline=True)
    embed.add_field(name="🛡️ Roles", value=f"`{len(template['roles'])}`", inline=True)
    embed.add_field(name="💬 Channels", value=f"`{sum(len(cat['channels']) for cat in template['categories'])}`", inline=True)
    
    message = await ctx.send(embed=embed)
    
    try:
        # Rename server if template has a name
        if template.get('server_name'):
            await guild.edit(name=template['server_name'])
        
        # Delete all existing channels and categories first
        cleanup_embed = discord.Embed(
            title="🧹 Server Cleanup",
            description="**Phase 1:** Removing existing structure\n**Status:** Cleaning channels, categories, and roles...",
            color=0x00ff00
        )
        await message.edit(embed=cleanup_embed)
        
        deleted_count = 0
        deleted_roles = 0
        
        # Delete all channels and categories
        for channel in guild.channels:
            if channel != ctx.channel:  # Don't delete the command channel
                try:
                    await channel.delete(reason=f"Cleanup before building {template['server_name']}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting channel {channel.name}: {e}")
        
        # Delete all roles except @everyone and bot's own role
        for role in guild.roles:
            if role.name != "@everyone" and role != guild.me.top_role:
                try:
                    await role.delete(reason=f"Cleanup before building {template['server_name']}")
                    deleted_roles += 1
                except Exception as e:
                    print(f"Error deleting role {role.name}: {e}")
        
        print(f"Deleted {deleted_count} channels/categories and {deleted_roles} roles")
        
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
                title="🚀 Deploying Server Structure",
                description=f"**Phase 2:** Building structure\n**Current:** `{category_data['name']}` ({i+1}/{len(template['categories'])})",
                color=0x00ff00
            )
            progress_embed.add_field(name="📁 Categories", value=f"`{len(created_categories)}`", inline=True)
            progress_embed.add_field(name="💬 Channels", value=f"`{len(created_channels)}`", inline=True)
            progress_embed.add_field(name="🛡️ Roles", value=f"`{len(created_roles)}`", inline=True)
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
            title="🚀 Deploying Server Structure",
            description="**Phase 3:** Finalizing deployment\n**Status:** All components created successfully!",
            color=0x00ff00
        )
        final_progress_embed.add_field(name="📁 Categories", value=f"`{len(created_categories)}`", inline=True)
        final_progress_embed.add_field(name="💬 Channels", value=f"`{len(created_channels)}`", inline=True)
        final_progress_embed.add_field(name="🛡️ Roles", value=f"`{len(created_roles)}`", inline=True)
        await message.edit(embed=final_progress_embed)
        
        # Update success message
        success_embed = discord.Embed(
            title="✅ Deployment Successful!",
            description=f"**{template['server_name']}** has been deployed successfully!\nYour server is now ready for use.",
            color=0x00ff00
        )
        success_embed.add_field(name="📁 Categories", value=f"`{len(created_categories)}`", inline=True)
        success_embed.add_field(name="💬 Channels", value=f"`{len(created_channels)}`", inline=True)
        success_embed.add_field(name="🛡️ Roles", value=f"`{len(created_roles)}`", inline=True)
        success_embed.add_field(name="🧹 Cleaned", value=f"`{deleted_count} channels, {deleted_roles} roles`", inline=True)
        
        if template.get('server_name'):
            success_embed.add_field(name="🏷️ Server Renamed", value=f"`{template['server_name']}`", inline=False)
        
        # Add Top.gg voting prompt
        success_embed.add_field(
            name="⭐ Support BuilderBot!",
            value=f"**Enjoying the bot? Please vote for us on Top.gg!**\n[Vote Now]({TOPGG_VOTE_URL}) • [Leave Review]({TOPGG_REVIEW_URL})",
            inline=False
        )
        
        await message.edit(embed=success_embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Deployment Failed",
            description=f"**Error:** `{str(e)}`\nPlease check bot permissions and try again.",
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
        title=f"📊 {guild.name} - Server Analytics",
        description="**Real-time server metrics and statistics**",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    
    # Get server owner information
    try:
        owner = guild.owner
        if owner:
            owner_info = f"{owner.mention}\n**{owner.name}#{owner.discriminator}**\nID: `{owner.id}`"
        else:
            owner_info = "Unknown"
    except:
        owner_info = "Unknown"
    
    embed.add_field(name="👑 Server Owner", value=owner_info, inline=True)
    embed.add_field(name="👥 Total Members", value=f"`{guild.member_count}`", inline=True)
    embed.add_field(name="📅 Created", value=f"`{guild.created_at.strftime('%Y-%m-%d')}`", inline=True)
    
    embed.add_field(name="💬 Text Channels", value=f"`{text_channels}`", inline=True)
    embed.add_field(name="🎵 Voice Channels", value=f"`{voice_channels}`", inline=True)
    embed.add_field(name="📁 Categories", value=f"`{categories}`", inline=True)
    
    embed.add_field(name="🛡️ Roles", value=f"`{len(guild.roles)}`", inline=True)
    embed.add_field(name="😀 Emojis", value=f"`{len(guild.emojis)}`", inline=True)
    embed.add_field(name="🎨 Boost Level", value=f"`{guild.premium_tier}`", inline=True)
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
    
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

# ==================== SLASH COMMANDS ====================

@bot.tree.command(name="help", description="📚 Show all available commands")
async def slash_help(interaction: discord.Interaction):
    """Slash command version of help"""
    embed = discord.Embed(
        title="🚀 Server Builder Pro - Command Center",
        description="**Next-Generation Discord Server Management**\nBuild, customize, and manage your server with professional templates",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    
    commands_info = {
        "**🔧 Core Commands:**": "",
        "`!build <template>`": "🏗️ Deploy complete server structure",
        "`!deletebuild`": "🗑️ Clean slate - remove all structure",
        "`!server`": "📊 Advanced server analytics",
        "`!ping`": "⚡ System performance check",
        "`!help`": "📖 Command documentation",
        "**⚡ Slash Commands:**": "",
        "`/build`": "🎯 Interactive template deployment",
        "`/deletebuild`": "🔄 One-click server reset",
        "`/server`": "📈 Real-time server metrics",
        "`/ping`": "⚡ Performance diagnostics",
        "`/help`": "📚 Command reference"
    }
    
    for cmd, desc in commands_info.items():
        if cmd.startswith("**"):
            embed.add_field(name=cmd, value=desc, inline=False)
        else:
            embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.add_field(
        name="🎨 Available Templates", 
        value="**Community** • **Gaming** • **Study** • **Marketplace** • **Tech**", 
        inline=False
    )
    
    # Add Top.gg support section
    embed.add_field(
        name="⭐ Support BuilderBot!",
        value=f"**If you're enjoying BuilderBot, please consider leaving a review on Top.gg!**\n[Leave Review]({TOPGG_REVIEW_URL}) • [Vote for us]({TOPGG_VOTE_URL})",
        inline=False
    )
    
    embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="⚡ Check system performance")
async def slash_ping(interaction: discord.Interaction):
    """Slash command version of ping"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="⚡ System Performance",
        description=f"**Latency:** `{latency}ms`\n**Status:** `Online`\n**Version:** `{BOT_VERSION}`",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="server", description="📊 Advanced server analytics")
async def slash_server(interaction: discord.Interaction):
    """Slash command version of server info"""
    guild = interaction.guild
    
    # Count channels by type
    text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
    voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
    categories = len(guild.categories)
    
    embed = discord.Embed(
        title=f"📊 {guild.name} - Server Analytics",
        description="**Real-time server metrics and statistics**",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    
    # Get server owner information
    try:
        owner = guild.owner
        if owner:
            owner_info = f"{owner.mention}\n**{owner.name}#{owner.discriminator}**\nID: `{owner.id}`"
        else:
            owner_info = "Unknown"
    except:
        owner_info = "Unknown"
    
    embed.add_field(name="👑 Server Owner", value=owner_info, inline=True)
    embed.add_field(name="👥 Total Members", value=f"`{guild.member_count}`", inline=True)
    embed.add_field(name="📅 Created", value=f"`{guild.created_at.strftime('%Y-%m-%d')}`", inline=True)
    
    embed.add_field(name="💬 Text Channels", value=f"`{text_channels}`", inline=True)
    embed.add_field(name="🎵 Voice Channels", value=f"`{voice_channels}`", inline=True)
    embed.add_field(name="📁 Categories", value=f"`{categories}`", inline=True)
    
    embed.add_field(name="🛡️ Roles", value=f"`{len(guild.roles)}`", inline=True)
    embed.add_field(name="😀 Emojis", value=f"`{len(guild.emojis)}`", inline=True)
    embed.add_field(name="🎨 Boost Level", value=f"`{guild.premium_tier}`", inline=True)
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="build", description="🏗️ Deploy server structure with templates")
@app_commands.describe(template="Choose a template to build")
@app_commands.choices(template=[
    app_commands.Choice(name="Community Hub", value="community"),
    app_commands.Choice(name="Gaming Community", value="gaming"),
    app_commands.Choice(name="Study Group", value="study"),
    app_commands.Choice(name="Marketplace", value="marketplace"),
    app_commands.Choice(name="Tech Community", value="tech")
])
async def slash_build(interaction: discord.Interaction, template: str):
    """Slash command version of build"""
    # Check permissions
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="You need Administrator permissions to use this command!",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Bot Owner: <@{BOT_OWNER_ID}> | Server Builder Pro")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if template not in TEMPLATES:
        embed = discord.Embed(
            title="❌ Template Not Found",
            description=f"Template '{template}' not found!",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Bot Owner: <@{BOT_OWNER_ID}> | Server Builder Pro")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Defer response since this will take time
    await interaction.response.defer()
    
    template_data = TEMPLATES[template]
    guild = interaction.guild
    
    # Send initial message
    embed = discord.Embed(
        title="🚀 Deploying Server Structure",
        description=f"**Template:** `{template_data['server_name']}`\n**Status:** Initializing deployment...",
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="📁 Categories", value=f"`{len(template_data['categories'])}`", inline=True)
    embed.add_field(name="🛡️ Roles", value=f"`{len(template_data['roles'])}`", inline=True)
    embed.add_field(name="💬 Channels", value=f"`{sum(len(cat['channels']) for cat in template_data['categories'])}`", inline=True)
    embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
    
    message = await interaction.followup.send(embed=embed)
    
    try:
        # Rename server if template has a name
        if template_data.get('server_name'):
            await guild.edit(name=template_data['server_name'])
        
        # Delete all existing channels and categories first
        cleanup_embed = discord.Embed(
            title="🧹 Server Cleanup",
            description="**Phase 1:** Removing existing structure\n**Status:** Cleaning channels, categories, and roles...",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        cleanup_embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        await message.edit(embed=cleanup_embed)
        
        deleted_count = 0
        deleted_roles = 0
        
        # Delete all channels and categories
        for channel in guild.channels:
            if channel != interaction.channel:  # Don't delete the command channel
                try:
                    await channel.delete(reason=f"Cleanup before building {template_data['server_name']}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting channel {channel.name}: {e}")
        
        # Delete all roles except @everyone and bot's own role
        for role in guild.roles:
            if role.name != "@everyone" and role != guild.me.top_role:
                try:
                    await role.delete(reason=f"Cleanup before building {template_data['server_name']}")
                    deleted_roles += 1
                except Exception as e:
                    print(f"Error deleting role {role.name}: {e}")
        
        print(f"Deleted {deleted_count} channels/categories and {deleted_roles} roles")
        
        # Create roles
        created_roles = []
        for role_data in template_data['roles']:
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
        
        for i, category_data in enumerate(template_data['categories']):
            # Update progress
            progress_embed = discord.Embed(
                title="🚀 Deploying Server Structure",
                description=f"**Phase 2:** Building structure\n**Current:** `{category_data['name']}` ({i+1}/{len(template_data['categories'])})",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            progress_embed.add_field(name="📁 Categories", value=f"`{len(created_categories)}`", inline=True)
            progress_embed.add_field(name="💬 Channels", value=f"`{len(created_channels)}`", inline=True)
            progress_embed.add_field(name="🛡️ Roles", value=f"`{len(created_roles)}`", inline=True)
            progress_embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
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
            title="🚀 Deploying Server Structure",
            description="**Phase 3:** Finalizing deployment\n**Status:** All components created successfully!",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        final_progress_embed.add_field(name="📁 Categories", value=f"`{len(created_categories)}`", inline=True)
        final_progress_embed.add_field(name="💬 Channels", value=f"`{len(created_channels)}`", inline=True)
        final_progress_embed.add_field(name="🛡️ Roles", value=f"`{len(created_roles)}`", inline=True)
        final_progress_embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        await message.edit(embed=final_progress_embed)
        
        # Update success message
        success_embed = discord.Embed(
            title="✅ Deployment Successful!",
            description=f"**{template_data['server_name']}** has been deployed successfully!\nYour server is now ready for use.",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        success_embed.add_field(name="📁 Categories", value=f"`{len(created_categories)}`", inline=True)
        success_embed.add_field(name="💬 Channels", value=f"`{len(created_channels)}`", inline=True)
        success_embed.add_field(name="🛡️ Roles", value=f"`{len(created_roles)}`", inline=True)
        success_embed.add_field(name="🧹 Cleaned", value=f"`{deleted_count} channels, {deleted_roles} roles`", inline=True)
        
        if template_data.get('server_name'):
            success_embed.add_field(name="🏷️ Server Renamed", value=f"`{template_data['server_name']}`", inline=False)
        
        # Add Top.gg voting prompt
        success_embed.add_field(
            name="⭐ Support BuilderBot!",
            value=f"**Enjoying the bot? Please vote for us on Top.gg!**\n[Vote Now]({TOPGG_VOTE_URL}) • [Leave Review]({TOPGG_REVIEW_URL})",
            inline=False
        )
        
        success_embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        
        await message.edit(embed=success_embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Deployment Failed",
            description=f"**Error:** `{str(e)}`\nPlease check bot permissions and try again.",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        error_embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
        await message.edit(embed=error_embed)

@bot.tree.command(name="deletebuild", description="🗑️ Reset server to clean slate")
async def slash_deletebuild(interaction: discord.Interaction):
    """Slash command version of deletebuild"""
    # Check permissions
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="You need Administrator permissions to use this command!",
            color=0xff0000,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Bot Owner: <@{BOT_OWNER_ID}> | Server Builder Pro")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Create confirmation embed
    embed = discord.Embed(
        title="⚠️ Server Reset Confirmation",
        description="**This action will completely reset your server structure.**\nAll categories, channels, and roles will be permanently deleted.",
        color=0xffaa00,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="⚠️ Warning", value="This action **cannot be undone**!", inline=False)
    embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
    
    # Create confirmation button
    class ConfirmView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30.0)
        
        @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.danger)
        async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
            if interaction.user.guild_permissions.administrator:
                # Delete all categories and channels
                deleted_count = 0
                deleted_roles = 0
                
                for channel in interaction.guild.channels:
                    if channel != interaction.channel:  # Don't delete the command channel
                        try:
                            await channel.delete(reason=f"Cleanup by {bot.user.name}")
                            deleted_count += 1
                        except Exception as e:
                            print(f"Error deleting channel {channel.name}: {e}")
                
                # Delete all roles except @everyone and bot's own role
                for role in interaction.guild.roles:
                    if role.name != "@everyone" and role != interaction.guild.me.top_role:
                        try:
                            await role.delete(reason=f"Cleanup by {bot.user.name}")
                            deleted_roles += 1
                        except Exception as e:
                            print(f"Error deleting role {role.name}: {e}")
                
                success_embed = discord.Embed(
                    title="✅ Server Reset Complete",
                    description=f"**Server has been reset successfully!**\n`{deleted_count}` channels/categories and `{deleted_roles}` roles removed.",
                    color=0x00ff00,
                    timestamp=datetime.utcnow()
                )
                success_embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
                
                await interaction.response.edit_message(embed=success_embed, view=None)
            else:
                await interaction.response.send_message("❌ You don't have permission to do this!", ephemeral=True)
        
        @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
        async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
            cancel_embed = discord.Embed(
                title="❌ Reset Cancelled",
                description="**Server reset has been cancelled.**\nYour server structure remains unchanged.",
                color=0xff0000,
                timestamp=datetime.utcnow()
            )
            cancel_embed.set_footer(text=f"Developed by <@{BOT_OWNER_ID}> | {BOT_OWNER_NAME} {BOT_VERSION}")
            await interaction.response.edit_message(embed=cancel_embed, view=None)
    
    await interaction.response.send_message(embed=embed, view=ConfirmView())

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN not found in environment variables!")
        exit(1)
    
    print("🚀 Starting Discord Server Builder Bot...")
    bot.run(token)
