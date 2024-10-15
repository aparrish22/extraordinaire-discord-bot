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

## bot invite link for discord user
https://discordapp.com/oauth2/authorize?&client_id=[insert_client_id]&scope=bot