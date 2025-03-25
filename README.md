# Mythic Mashup Bot

A Discord bot for forming balanced World of Warcraft Mythic+ groups using role reactions and spec-based logic.

## 🚀 Features
- Easy group forming using reaction emojis 
- Smart balancing: Heroism and Battle Res awareness
- Advanced mode with spec-based input using custom emojis added to a discord server
- Custom UI with Discord buttons

## 🛠 Setup Instructions

1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/mythic-mashup-bot.git
cd mythic-mashup-bot
```

2. **Create a `.env` file** with your credentials:

```env
DISCORD_TOKEN=your_token
GUILD_IDS=1234567890,2345678910...
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

4. **Run the bot**:

```bash
python main.py
```

## 💡 Notes
- Make sure your bot has permission to read messages, add reactions, and manage messages.
- Don't forget to invite it with the appropriate scope (`applications.commands bot`).

## 🧙 Author
Crafted for WoW Guilds to organize Mythic+ Group activities. Adapt, fork, and improve!
