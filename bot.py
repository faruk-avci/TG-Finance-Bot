from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update
from database import Database
from commands import Commands
from request import Request 
from db import db
import os
from dotenv import load_dotenv
class Bot:
    def __init__(self, token,Commands, db, Requests):
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher
        self.commands = Commands(db, Requests)

        self.dispatcher.add_handler(CommandHandler("start", self.commands.start))
        self.dispatcher.add_handler(CommandHandler("help", self.commands.help))
        self.dispatcher.add_handler(CommandHandler("register", self.commands.register))
        self.dispatcher.add_handler(CommandHandler("unregister", self.commands.unregister))
        self.dispatcher.add_handler(CommandHandler("buy", self.commands.buy))
        self.dispatcher.add_handler(CommandHandler("sell", self.commands.sell))
        self.dispatcher.add_handler(CommandHandler("view_transactions", self.commands.view_transactions))
        self.dispatcher.add_handler(CommandHandler("view_stocks", self.commands.view_stocks))

    def start(self):
        self.updater.start_polling()
        self.updater.idle()


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    db = db('users.db')
    db.create_tables()
    db.close_connection()
    Created_db = Database(db.db_name)  
    Requests = Request(TOKEN)
    bot = Bot(TOKEN,Commands,Created_db,Requests)
    bot.start()
    


    