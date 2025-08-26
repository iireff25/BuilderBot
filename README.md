# Discord Server Builder Bot

A powerful Discord bot built with discord.py that creates server structures using predefined templates. No AI required - everything is static and ready to use!

## 🚀 Features

- **🏗️ Server Builder**: Create complete server structures with categories, channels, and roles
- **📋 Multiple Templates**: Community, Gaming, Study, Marketplace, and Tech templates
- **🗑️ Cleanup Tools**: Delete all created categories and channels
- **📊 Server Info**: View detailed server statistics
- **🛡️ Role Management**: Create and delete roles easily
- **⚡ Utility Commands**: Ping, help, and more

## 📋 Available Templates

### 🌍 Community Template
- Welcome channels (welcome, announcements, rules, introductions)
- General channels (chat, music, gaming, media)
- Events section (events, event voice)

### 🎮 Gaming Template
- Welcome and announcements
- General gaming channels
- Tournament system (tournaments, results, voice)
- Game categories (FPS, MOBA, Battle Royale)
- Teams and clips sharing

### 📚 Study Template
- Welcome and study guidelines
- Subject-specific channels (Science, Math, History, English, CS)
- Study resources and notes
- Voice study rooms (quiet, group, background music)

### 🛒 Marketplace Template
- Welcome and safety guidelines
- Buy & sell channels
- Category-specific channels (Electronics, Clothing, Books, Gaming, Home)
- Feedback and support system

### 💻 Tech Template
- Welcome and tech news
- Programming language channels (Python, Java, JavaScript, C#, Rust)
- Development areas (Web, Mobile, Game, AI/ML, Cloud)
- Projects and collaboration channels

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- Discord Bot Token

### 2. Environment Variables
Copy `env.example` to `.env` and add your Discord bot token:
```bash
DISCORD_TOKEN=your_discord_bot_token_here
```

### 3. Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
```

### 4. Bot Permissions
Your Discord bot needs these permissions:
- Administrator (for building server structures)
- Manage Server
- Manage Channels
- Manage Roles
- Send Messages
- Read Message History

## 🎯 Commands

### Server Building
- `!build` - Show available templates
- `!build <template>` - Build server structure using template
- `!deletebuild` - Delete all categories and channels (with confirmation)

### Server Information
- `!server` - Show server statistics and information

### Role Management
- `!addrole <name>` - Create a new role with default permissions
- `!deleterole <name>` - Delete a role by name

### Utility
- `!ping` - Check bot latency
- `!help` - Show all available commands

## 🚀 Railway Deployment

### 1. Deploy to Railway
1. Go to [Railway](https://railway.app)
2. Sign up/Login with your GitHub account
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository

### 2. Set Environment Variables
In Railway dashboard, go to your project → "Variables" tab and add:
```
DISCORD_TOKEN=your_discord_bot_token_here
```

### 3. Deploy
- Railway will automatically detect the Python project
- It will install dependencies and run the bot
- Your bot will be online!

## 📁 Project Structure

```
├── bot.py              # Main bot file
├── templates.json      # Server templates
├── requirements.txt    # Python dependencies
├── Procfile           # Railway deployment config
├── runtime.txt        # Python version
├── env.example        # Environment variables template
└── README.md          # This file
```

## 🔧 Customization

### Adding New Templates
1. Edit `templates.json`
2. Add your template with the required structure:
```json
{
  "your_template": {
    "server_name": "Your Server Name",
    "categories": [
      {
        "name": "Category Name",
        "channels": [
          { "name": "channel-name", "type": "text|voice", "topic": "optional" }
        ]
      }
    ],
    "roles": [
      { "name": "Role Name", "permissions": ["permission1", "permission2"] }
    ]
  }
}
```

### Modifying Existing Templates
Simply edit the `templates.json` file to modify categories, channels, or roles in existing templates.

## 🛡️ Security Features

- **Permission Checks**: All commands check for appropriate permissions
- **Confirmation Dialogs**: Destructive actions require confirmation
- **Error Handling**: Comprehensive error handling and user feedback
- **Safe Deletion**: Role deletion checks for bot permissions

## 📊 Bot Statistics

The bot tracks and displays:
- Server member count
- Channel counts (text, voice, categories)
- Role count
- Server creation date
- Boost level
- Emoji count

## 🔍 Troubleshooting

### Common Issues:

1. **"DISCORD_TOKEN not found"**
   - Check your `.env` file has the correct token

2. **"You need Administrator permissions"**
   - Ensure the bot has proper permissions in your Discord server

3. **"Template not found"**
   - Use `!build` to see available templates
   - Check `templates.json` for correct template names

4. **"Error creating channels/roles"**
   - Check bot permissions
   - Ensure bot role is high enough in hierarchy

## 🤝 Contributing

Feel free to contribute by:
- Adding new templates
- Improving error handling
- Adding new features
- Fixing bugs

## 📄 License

MIT License - Feel free to modify and distribute!

## 🆘 Support

If you encounter issues:
1. Check the console logs for detailed error messages
2. Verify all environment variables are set correctly
3. Ensure your bot has the required Discord permissions
4. Test with a simple command first

---

**Happy server building! 🚀**
