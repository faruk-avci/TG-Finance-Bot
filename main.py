from database.db import db
from db_manager.database import Database
from bot.bot import Bot
from commands.commands import Commands
from request.request import Request
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    token = os.getenv("TOKEN")
    finance_token = os.getenv("FINANCE")
    db_creator = db("finance.db")
    db_creator.create_tables()
    db_creator.close_connection()
    db_manager = Database(db_creator.db_name)
    request = Request(finance_token)
    request.start_periodic_fetch()

    commands_instance = Commands(db_manager, request)  # Create an instance of the Commands class
    bot = Bot(token, commands_instance)  # Pass the instance to the Bot constructor
    bot.start()

if __name__ == "__main__":
    main()
