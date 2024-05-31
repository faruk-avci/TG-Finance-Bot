from telegram.ext import Updater, CommandHandler, CallbackContext
class Bot:
    def __init__(self, token,Commands):
        self.updater = Updater(token)
        self.dispatcher = self.updater.dispatcher
        self.commands = Commands

    def handle_commands(self):
        self.dispatcher.add_handler(CommandHandler("start", self.commands.start))
        self.dispatcher.add_handler(CommandHandler("help", self.commands.help))
        self.dispatcher.add_handler(CommandHandler("register", self.commands.register))
        self.dispatcher.add_handler(CommandHandler("unregister", self.commands.unregister))
        self.dispatcher.add_handler(CommandHandler("buy", self.commands.buy))
        self.dispatcher.add_handler(CommandHandler("sell", self.commands.sell))
        self.dispatcher.add_handler(CommandHandler("view_transactions", self.commands.view_transactions))
        self.dispatcher.add_handler(CommandHandler("view_stocks", self.commands.view_stocks))
        self.dispatcher.add_handler(CommandHandler("add_balance", self.commands.add_balance))
        self.dispatcher.add_handler(CommandHandler("withdraw", self.commands.withdraw))


    def start(self):
        self.handle_commands()
        self.updater.start_polling()
        self.updater.idle()    