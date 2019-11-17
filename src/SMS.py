#!/usr/bin/env python3
# Work with Python 3.6
import discord
import csv
import twilio
from twilio.rest import Client as TwilioClient
import time
from timeit import default_timer as timer
import phonenumbers as phone
import logging

now = datetime.now()
time_stamp = now.strftime("%m/%d/%Y %H:%M:%S")

# Error logging
logging.basicConfig(filename='src/smartnotifysms.log', level=logging.INFO)
logging.info(f'Starting new session: {time_stamp}')

# Data Logging
data_file = 'src/numbers.txt'
key_file = 'src/keys.txt'
line0 = 'user,number\n'
contact_list = []  # Stores contacts collected
# Stores channel names of unfinished user number-add requests
awaiting_channel_resp = []

#Discord keys
CHANNEL_TOKEN = None
SMS_CHANNEL = None
admin = None # not a key
# Twilio keys
twil_account_sid = None
twil_auth_token = None
twil_num = None


try:
    with open(key_file) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        f.close()
except:
    logging.error("Could not load info from keys.txt. Check formatting in README.txt")
    exit()
else:
    if len(content == 6):
        CHANNEL_TOKEN = content[0]
        twil_account_sid = content[1]
        twil_auth_token= content[2]
        twil_num = content[3]
        SMS_CHANNEL = content[4]
        admin = content[5]
        logging.info('Loaded keys.')
    else:
        logging.error('Error in formatting of keys.txt. Not 6 tokens to read.')
        exit()

# Discord
try:
    client = discord.Client()
except:
    logging.error('Incorrect Discord Key')
myembed = discord.Embed(
    title="SmartNotify SMS Commands:", description="Instructions: ", color=0xf16868)
myembed.add_field(name='!addnumber: add number to list', value='- You will receive a DM with instructions', inline=False)
myembed.set_footer(text="By SmartNotify\t\t" + str(time_stamp), icon_url="https://cdn.discordapp.com/attachments/628750460949364757/631225789538500608/unknown.png")
myembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/628750460949364757/631226140601876540/New_logo.png")




###########################################################################################
# Helper Functions - to be moved to another file
# Person holds the username, phone number


class Person:
    username = None
    number = None

    def __init__(self, name, num):
        self.username = name
        self.number = num

    def getName(self):
        return self.username

    def getNumber(self):
        return self.number

    def getInfo(self):
        return 'User: ' + self.getName() + "\t Phone: " + self.getNumber()

# Print the username and number to the Discord Channel passed


async def printContacts(channel):
    if len(contact_list) is 0:
        await channel.send("Contact list is empty. Use !addnumber to add create entry.")
    else:
        await channel.send("Contact List:")
        for person in contact_list:
            await channel.send(person.getInfo())

# Returns the user's Person object if found, false otherwise


def in_list(author, list):
    for person in list:
        if author == person.username:
            return person
    return False

# Populate saved data, to be run at start
# Read from file to populate contact list


def readData(f):
    logging.info("Populating user/number data...")
    with open(f, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            # First line used as dictionary keys
            if line_count == 0:
                logging.info(f'Column names are {", ".join(row)}:')
                line_count += 1  # Auto iterates to next line after keys
            new_person = Person(row['user'], row['number'])
            contact_list.append(new_person)
            logging.info(str(line_count) + ": " + new_person.getInfo())
            line_count += 1
        logging.info(f'\nProcessed {line_count - 1} lines from {f}')
        csv_file.close()

# Writes updated list to data file


def updateDataFile(f, contact_list):
    with open(f, "w") as out_file:
        out_file.write(line0)
        for contact in contact_list:
            out_file.write(contact.getName() + "," +
                           contact.getNumber() + "\n")
        out_file.close()
        logging.info(f"numbers.txt updated with {contact.getName()},{contact.getNumber()}")


def massSendSMS(msg, contacts):
    twilio_client = TwilioClient(twil_account_sid, twil_auth_token)
    failCount = 0
    successCount = 0
    count = 1
    output = None
    for user in contacts:
        try:
            logging.info("Sending message to " + user.getName() + " " + msg)
            twilio_client.messages.create(
                body=msg, from_=twil_num, to=user.getNumber())
        except:
            logging.info(f'Failed: {user.getName()}: {user.getNumber()}')
            failCount += 1
        else:
            logging.info(f'Success: {user.getName()}: {user.getNumber()}')
            successCount += 1
        count += 1
        time.sleep(0.3)
    logging.info("\nSuccessful: " + str(successCount) + "\nFailed: " + str(failCount))

def isAdmin(author):
    if author == admin:
        return True
    else:
        return False


############################################################################################
# Event handling
@client.event
async def on_message(msg):
    # Do not want the bot to reply to itself
    if msg.author == client.user:
        return
    elif str(msg.channel) == SMS_CHANNEL:
        # Print incoming messages to local terminal
        #print("**%s** %s : %s" % (msg.channel, msg.author.name, msg.content))
        if msg.content.startswith('!commands'):
            await msg.channel.send(embed=myembed)
        elif msg.content.startswith('!showlist'):
            if isAdmin(str(msg.author)):
                await printContacts(msg.channel)
            else:
                await msg.channel.send("@%s you do not have permission to execute this command." % msg.author)
        elif msg.content.startswith('!addnumber'):
            # Check if username already present in list
            res = in_list(str(msg.author), contact_list)
            if res:  # Don't want duplicate numbers
                await msg.channel.send("@%s you are already in the messaging list\n"
                                    "Use command !removenumber to remove your number." % msg.author)
            else:  # Send personal dm for info
                await msg.channel.send("@%s please check your dm" % msg.author)
                await msg.author.send(content="You have requested to be added to the messaging list.\nPlease enter your phone number\n"
                                        "*Include country and area code*")
                # Formatting of Discord channel name
                dm_channel = 'Direct Message with ' + str(msg.author)
                awaiting_channel_resp.append(dm_channel)
        elif msg.content.startswith('!removenumber'):
            res = in_list(str(msg.author), contact_list)
            # Person is in list
            if res:
                contact_list.remove(res)
                await msg.channel.send("@%s you have been remove from the list" % msg.author)
                updateDataFile(data_file, contact_list)  # Save changes to file
            else:
                await msg.channel.send("@%s you are not in the list." % msg.author)
        elif msg.content.startswith('!sms'):  # Text list with the trailing msg
            if isAdmin(str(msg.author)):  
                if len(contact_list) > 0:
                    msg = msg.content.strip('!sms')  # Get msg to send out
                    massSendSMS(msg, contact_list)
                else:
                    await msg.channel.send("Contact list is empty. Use command !addnumber")
            else:
                await msg.channel.send("@%s you do not have permission to execute this command." % msg.author)
    # Dm with phone number
    elif str(msg.channel) in awaiting_channel_resp:
        try:
            num = phone.parse(msg.content, None)
        except:
            await msg.author.send("%s is not a valid phone number. Please try again.\n"
                                    "Make sure to include the country and area code." % msg.content)
        else:
            if phone.is_valid_number(num):
                new_person = Person(str(msg.author), str(msg.content))
                contact_list.append(new_person)
                updateDataFile(data_file, contact_list)  # Save changes to file
                # Remove from waiting list
                awaiting_channel_resp.remove(str(msg.channel))
                await msg.author.send("%s has been added to the list" % new_person.getInfo())
            else:
                await msg.author.send("%s is not a valid phone number. Please try again.\n"
                                        "Make sure to include the country and area code." % msg.content)


@client.event
async def on_ready():
    logging.info('Logged in as')
    logging.info(client.user.name)
    logging.info(client.user.id)
    logging.info('Monitoring Channel: %s' % SMS_CHANNEL)
    readData(data_file)  # Populate contacts from data file

client.run(CHANNEL_TOKEN)
