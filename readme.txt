ssh login (be sure to double check your IP address on AWS):
    ssh -i "DiscordBotKeyPairName.pem" ec2-user@3.21.242.56

use virtual environment with the command:
    source venv/bin/activate

4.	Detach from the session:
	•	Press Ctrl + B, then D to detach from the tmux session.
	•	The bot will keep running even if you disconnect from the SSH session.
	5.	Reattach to the tmux session:
	•	To check on the bot later, SSH into the EC2 instance and run:
        tmux attach -t discordbot
        
To detach from discordbot session, use (literally use CTRL on macbook keyboard) CTRL + B then press D


## bot invite link for discord user
https://discordapp.com/oauth2/authorize?&client_id=[insert_client_id]&scope=bot

To start the bot, use python bot_script.py

game_slug argument must be the title of game world found in URL, for example, dndextraordinaire-wd is the Waterdeep campaign foundry world.

# TODO
check if arguments accept game name as a String with quotes or without quotes, and if the api call actually changes it