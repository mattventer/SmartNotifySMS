*SmartNotify Twitter Success Post Bot:

FIRST TIME USE: You must have python3 installed on your machine with pip
    - use 'pip3 install -r requirements.txt' to install required dependencies
    - you must be in the src/ directory to run this command

TO RUN:
		- ./start.sh 
	* program output will be sent to app_output.log in src/


**DO NOT MOVE THE LOCATION OF 'numbers.txt' OR 'keys.txt' OR MODIFY FILENAMES

ONLY MODIFY 'keys.txt' USING THE FOLLOWING FORMAT:
DISCORD_BOT_TOKEN
TWILIO_ACCOUNT_SID
TWILIO_ACCOUNT_AUTH
TWILIO_PHONE_NUMBER
'name-of-channel-to-monitor' <- Don't use quotations
'admin username' <- Don't use quotations


NOTES:
-Discord token is from a Bot you must create on a Discord Developer App
    - Create a Bot for this app, the Token under the "Bot" page is your DISCORD_BOT_TOKEN
    - Note: you must authorize this app + bot in your channel by using the OAuth2 tab
- name-of-channel-to-monitor is the channel name exactly as it appears in discord, excluding the leading '#'
- admin is the only user who can use commands: !sms and !showlist
- admin username must be full, unique, username. Not your nickname specific to the channel

HELP:
- If the bot loads but nothing happens when a message is sent in the channel, ensure the specific channel
    to be monitored is spelled correctly in 'keys.txt' and in the correct location. All other channels
    will be ignored except the one specified in 'keys.txt'.


Written by Matthew Venter
SmartNotify 2019
venterke@gmail.com
10/03/2019
Modified: 10/21/2019

