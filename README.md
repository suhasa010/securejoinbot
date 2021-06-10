# securejoinbot

* Secure Generation of Invite links for Private Telegram groups *

**How to create your own bot using this repository:**

1. Clone or Fork this repository.
2. Create a heroku app and connect to your forked repository.
3. Create a redis database in redislabs.com or use Redis addon on heroku.
4. Rename the sample.env file to .env and fill in all the required details.
5. Create a bot in @Botfather and get the BOT_TOKEN and paste it in .env
6. Customize the bot messages in strings.py according to your wish.
7. Start the bot.

**Features:**

1. Admins can generate inline links using "@<yourbotname> link"
2. Users can generate links that expire in specified number of days/hours/seconds and is only valid for them (customizable to allow more users per link, check sample.env).
3. Admins can view the logs in their log channels (NOTIF_CHANNEL_ID needs to be specified in .env) where the bot should added as an admin.
4. Admins can reset the limit to generate more invite links in the bot PM using /resetlimit command.
5. Admins can revoke any link by just sending the invite link to be revoked in the bot PM and using /revoke command as a reply to the invite link.
6. Admins can view stats related to how many users have started the bot and generated invite links.
