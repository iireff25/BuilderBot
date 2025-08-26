# 🔧 Slash Commands Setup Guide

## 🚨 **IMPORTANT: Your slash commands aren't showing up because of missing bot permissions!**

### **Step 1: Fix Bot Permissions**

1. **Go to Discord Developer Portal:**
   - Visit: https://discord.com/developers/applications
   - Select your bot application

2. **Enable Application Commands Scope:**
   - Go to **OAuth2** → **URL Generator**
   - Check ✅ **`applications.commands`** scope
   - Check ✅ **`bot`** scope
   - Copy the generated URL

3. **Re-invite the bot with proper permissions:**
   - Use the new URL to invite the bot to your server
   - This will give the bot permission to register slash commands

### **Step 2: Bot Permissions Required**

Make sure your bot has these permissions:
- ✅ **Administrator** (for server management)
- ✅ **Manage Channels** (to create/delete channels)
- ✅ **Manage Roles** (to create/delete roles)
- ✅ **Send Messages** (to respond to commands)
- ✅ **Use Slash Commands** (to register commands)

### **Step 3: Sync Commands**

Once the bot is running with proper permissions:

1. **Use the sync command:**
   ```
   !sync
   ```
   (Only you can use this command - it's owner-only)

2. **Or restart the bot** - it will auto-sync on startup

### **Step 4: Test Slash Commands**

After syncing, you should see these commands when you type `/`:

- `/help` - 📚 Show all available commands
- `/ping` - ⚡ Check system performance  
- `/server` - 📊 Advanced server analytics
- `/build` - 🏗️ Deploy server structure with templates
- `/deletebuild` - 🗑️ Reset server to clean slate

### **Step 5: If Commands Still Don't Show**

1. **Check bot status** - Make sure it's online
2. **Wait 1-2 minutes** - Discord can take time to register commands
3. **Try in a different server** - Test if it's a server-specific issue
4. **Check bot permissions** - Make sure it has all required permissions

### **🔍 Troubleshooting**

**Error: "Missing Access"**
- Bot needs `applications.commands` scope

**Error: "Unknown Interaction"** 
- Commands haven't synced yet, use `!sync`

**Commands not appearing in `/` menu**
- Wait 1-2 minutes after syncing
- Make sure bot is online and has proper permissions

### **✅ Success Indicators**

When working correctly, you should see:
- Bot status: "Playing Server Builder Pro v3.0 | /help"
- Console message: "✅ Successfully synced 5 slash commands globally!"
- Commands appear when typing `/` in Discord

---

**Need help?** The most common issue is missing the `applications.commands` scope when inviting the bot!
