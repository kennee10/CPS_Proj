#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# DATA
data = {
    "667047883-vuvip": {
        "name": "Gabriella",
        "languagePreference": "English",
        "IC": "T0012345A",
        "address": "Blk 884 Yishun Street 81",
        "DOB": "1-1-2000",
        "bloodType": "O+",
        "emergencyContact": "81234567",
        "relationshipOfEmergencyContact": "Mother"
    }, 
    "1189583850-pigav": {
        "name": "Jonathon",
        "languagePreference": "English",
        "IC": "T0067891Z",
        "address": "20 Bukit Timah Road",
        "DOB": "31-12-2000",
        "bloodType": "AB+",
        "emergencyContact": "87654321",
        "relationshipOfEmergencyContact": "Sister"
    }
}

currentLatitude = 0
currentLongitude = 0

from ast import Call
import time
import settings
import telegram
import logging
import haversine
import serial
import enum
import pprint
import time


from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
)

# Enable logging
logging.basicConfig(format="%(asctime)s %(levelname)s %(filename)s:%(funcName)s():%(lineno)i: %(message)s", datefmt="%Y-%m-%d %H:%M:%S",  level=logging.DEBUG)
logger = logging.getLogger(__name__)

#on /start, bot will ask client to turn on live location
def start(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please turn on your live location.")

#handle location messages
def location(update: Update, context: CallbackContext) -> None:
    message = None
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    global currentLatitude
    currentLatitude = message.location.latitude
    global currentLongitude
    currentLongitude = message.location.longitude

#send user's data
def sendInfo(usersData, bot):
    data_string = ("Name: " + usersData.get('name') + "\nLanguage Preference: " + usersData.get('languagePreference') 
    + "\nIC: " + usersData.get('IC') + "\nAddress: " + usersData.get('address') + "\nDate of Birth: " + usersData.get('DOB')
    + "\nBlood Type: " + usersData.get('bloodType') + "\nEmergency Contact: " + usersData.get('emergencyContact')
    + "\nRelationship of Emergency Contact: " + usersData.get('relationshipOfEmergencyContact'))
    bot.send_message(chat_id=settings.chat_id1, text = data_string)
    bot.send_location(chat_id=settings.chat_id1, latitude =  currentLatitude, longitude =  currentLongitude)
    bot.send_message(chat_id=settings.chat_id2, text = data_string)
    bot.send_location(chat_id=settings.chat_id2, latitude =  currentLatitude, longitude =  currentLongitude)


def handle_stateless_callback_query(update: Update, context: CallbackContext):
    update.message.reply_text(text=f"Hey, try sending /start")


def handle_unknown_command(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="huh?")


def handle_text_message_from_private_chats(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text=f"Hey, try sending /start")


def main() -> None:
    # Create an updater object, and pass it the bot's token. 
    # The updater continuously fetches new updates from Telegram and passes them to the updater.dispatcher object.
    updater = telegram.ext.Updater(settings.my_token)
    bot = telegram.Bot(settings.my_token)

    # Add handler for text messages (excluding commands), from private chats
    updater.dispatcher.add_handler(MessageHandler(
        filters=Filters.text & ~Filters.command & Filters.chat_type.private, 
        callback=handle_text_message_from_private_chats))

    # Add handler for location messages, from private chats
    updater.dispatcher.add_handler(MessageHandler(
        filters=Filters.location & Filters.chat_type.private, 
        callback=location))

    # Add handler for commands that don't get handled by anything so far
    updater.dispatcher.add_handler(MessageHandler(filters=Filters.command, callback=handle_unknown_command))

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT. 
    # This should be used most of the time, since start_polling() is non-blocking and will stop the bot gracefully.
    # updater.idle()
    #time.sleep(20)
    #sendInfo(data["667047883-vuvip"], bot)
    #comment out the whole block below and use the above line of code to test without microbit

    # Set up the Serial connection to capture the Microbit communications
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = "COM8"
    ser.open()

    while True:
        time.sleep(5)

        if ser.in_waiting > 0:

            microbitdata = str(ser.readline())
            uniqueIdentifier = microbitdata[3:22].strip()
            
            # check if user exists
            if uniqueIdentifier in data:
                
                usersData = data[uniqueIdentifier]
                sendInfo(usersData, bot)

if __name__ == "__main__":
    main()
