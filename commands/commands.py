from telegram import Update
from telegram.ext import CallbackContext
import matplotlib.pyplot as plt
from prettytable import PrettyTable
import io
import datetime
class Commands:
    def __init__(self, db, request):
        self.db = db
        self.request = request

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text("Welcome to the Stock Bot! Type /help to see the available commands.")
        if not self.db.check_if_user_exists(update.message.from_user.id):
            self.register(update, context)

    def help(self, update: Update, context: CallbackContext):
        help_text = (
            "The following commands are available:\n"
            "/register - Register to the bot\n"
            "/unregister - Unregister from the bot\n"
            "/buy <symbol> <quantity> <price(optional)> - Buy a stock\n"
            "/sell <symbol> <quantity> <price(optional)> - Sell a stock\n"
            "/view_stocks - View your stocks and budget\n"
            "/add_balance <amount> - Add balance to your account\n"
            "/withdraw <amount> - Withdraw balance from your account\n"
            "/withdraw_all - Withdraw all balance from your account\n"


        )
        update.message.reply_text(help_text)

    def generate_pie_chart(self,labels, sizes):
        plt.figure(figsize=(7, 5))  # Smaller figure size for a more compact look
        _, texts, autotexts = plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, pctdistance=0.75)

        # Increase the size of the percentage texts and labels for better readability
        for text in texts:
            text.set_fontsize(15)
        for autotext in autotexts:
            autotext.set_fontsize(15)  # Increase the fontsize of the autotexts (percentages)

        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        # Save the pie chart as a bytes object
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')  # Use 'bbox_inches' to tightly fit the plot
        buf.seek(0)
        plt.close()  # Important to close the plot to free up memory
        return buf
    
    def register(self, update, context):
        user_id = update.message.from_user.id
        if self.db.check_if_user_exists(user_id):
            update.message.reply_text("You are already registered!")
            return
        else:
            conn = self.db.connect_db()
            c = conn.cursor()
            username = update.message.from_user.username
            generated_id = f"{user_id}123"
            c.execute('INSERT INTO users (user_id, generated_id,username,registration_date) VALUES (?, ?, ?, ?)', (user_id, generated_id, username, str(datetime.datetime.now())))
            conn.commit()
            conn.close()
            update.message.reply_text(f"Congrats! {username} you have been registered successfully!")
            return
    
    def unregister(self, update, context):
        user_id = update.message.from_user.id
        if self.db.check_if_user_exists(user_id):
            conn = self.connect_db()
            c = conn.cursor()
            c.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            c.execute('DELETE FROM user_stocks WHERE user_id = ?', (user_id,))
            conn.commit()
            update.message.reply_text("You have successfully unregistered.")
            conn.close()     
        else:
            update.message.reply_text("You are not registered already!")

    def view_stocks(self, update: Update, context: CallbackContext):
        user_id = update.message.from_user.id
        budget = self.db.get_user_budget(user_id)
        stocks = self.db.get_user_stocks(user_id)

        if stocks:
            labels = []
            sizes = []
            # Initialize header and format it properly
            table_text = "Stock    Quantity      Avg        Total\n"
            table_text += "-"*42 + "\n"  # Adds a dividing line for clarity

            for stock in stocks:
                total_value = stock[1] * stock[2]
                labels.append(stock[0])  # Adding labels for the pie chart
                sizes.append(total_value)  # Adding values for the pie chart
                # Properly formatted string line for each stock
                table_text += f"{stock[0]:<10} {stock[1]:<9} ${stock[2]:<9,.2f} ${total_value:,.2f}\n"
            
            table_text += "-"*42 + "\n"  # Adds a dividing line for clarity
            table_text += f"Budget: ${budget[0]:,.2f}\n"
            chart = self.generate_pie_chart(labels, sizes)
            update.message.reply_photo(photo=chart)
            update.message.reply_text(table_text)
        else:
            update.message.reply_text("You currently have no stocks in your portfolio.")
    
    def buy(self, update, context):
            user_id = update.message.from_user.id
            if self.db.check_if_user_exists(user_id):
                command_params = update.message.text.split()

                stock_symbol = command_params[1].upper()
                quantity = int(command_params[2].replace(",", ""))
                
                if stock_symbol in self.request.stock_symbols:
                    price = float(self.request.stock_prices[stock_symbol])
                else:
                    # check if the stock symbol is valid
                    quote = self.request.get_price(stock_symbol)
                    if "error" in quote:
                        raise ValueError("Error: Stock symbol not found.")
                    else:
                        price = float(quote["price"])
                        self.request.stock_prices[stock_symbol] = price


                if quantity <= 0 or price <= 0:
                    raise ValueError("Error: Quantity and price must be greater than 0.")

               
                if stock_symbol.endswith(".IS"):
                    stock_symbol = stock_symbol[:-3]
                
                if self.db.get_user_budget(user_id)[0] >= quantity * price:

                    if len(command_params) == 4:
                        with self.db.connect_db() as conn:
                            c = conn.cursor()
                            stock = self.db.get_user_stock(user_id, stock_symbol)
                            price = float(command_params[3])
                            if stock:
                                new_quantity = stock[1] + quantity
                                new_average = ((stock[2] * stock[1]) + (quantity * price)) / new_quantity
                                self.db.update_stock(user_id, stock_symbol, new_quantity, new_average)
                                self.db.add_transaction(stock[3],user_id, stock_symbol, quantity, price, datetime.datetime.now(),"BUY")
                                update.message.reply_text(f"Bought {quantity} shares of {stock_symbol} at {price} successfully!")

                            else:
                                self.db.add_stock(user_id, stock_symbol, quantity, price)
                                stock = self.db.get_user_stock(user_id, stock_symbol)
                                self.db.add_transaction(stock[3],user_id, stock_symbol, quantity, price, datetime.datetime.now(),"BUY")
                                update.message.reply_text( f"New stock {stock_symbol} added to your portfolio with {quantity} shares at {price}.")
                            self.db.add_balance(user_id, -1 * quantity * price)
                            conn.commit()

                    elif len(command_params) == 3:
                        update.message.reply_text("You didn't specify a price. Using the current market price.")
                        with self.db.connect_db() as conn:

                            c = conn.cursor()
                            stock = self.db.get_user_stock(user_id, stock_symbol)
                            if stock:
                                new_quantity = int(stock[1]) + quantity
                                new_average = ((stock[2] * stock[1]) + (quantity * price)) / new_quantity
                                self.db.update_stock(user_id, stock_symbol, new_quantity, new_average)
                                self.db.add_transaction(stock[3],user_id, stock_symbol, quantity, price, datetime.datetime.now(),"BUY")
                                update.message.reply_text(f"Bought {quantity} shares of {stock_symbol} at {price} successfully!")
                            else:
                                self.db.add_stock(user_id, stock_symbol, quantity,price)
                                stock = self.db.get_user_stock(user_id, stock_symbol)
                                self.db.add_transaction(stock[3],user_id, stock_symbol, quantity, price, datetime.datetime.now(),"BUY")
                                update.message.reply_text( f"New stock {stock_symbol} added to your portfolio with {quantity} shares at {price}.")
                            self.db.add_balance(user_id, -1 * quantity * price)
                            conn.commit()
                    else:
                            update.message.reply_text("Invalid parameters. Please use /buy <symbol> <quantity> <price(optional)>")
                else:
                    update.message.reply_text("You don't have enough balance to buy that amount of shares.")
            
            else:
                update.message.reply_text("You need to register first using /register.")

    def sell(self, update, context):
        try:
            user_id = update.message.from_user.id
            if self.db.check_if_user_exists(user_id):
                command_params = update.message.text.split(" ")

                stock_symbol = command_params[1].upper()
                quantity = int(command_params[2])
                
                if stock_symbol in self.request.stock_symbols:
                    price = float(self.request.stock_prices[stock_symbol])
                else:
                    quote = self.request.get_price(stock_symbol)
                    if "error" in quote:
                        raise ValueError("Error: Stock symbol not found.")
                    else:
                        price = float(quote["price"])
                        self.request.stock_prices[stock_symbol] = price


                if quantity <= 0 or price <= 0:
                    raise ValueError("Error: Quantity and price must be greater than 0.")
                
                if stock_symbol.endswith(".IS"):
                    stock_symbol = stock_symbol[:-3]

                if len(command_params) == 4:
                    with self.db.connect_db() as conn:
                        c = conn.cursor()
                        stock = self.db.get_user_stock(user_id, stock_symbol)
                        price = float(command_params[3])

                        if stock:
                            if stock[1] < quantity:
                                raise ValueError("Error: You don't have enough shares to sell.")
                            new_quantity = stock[1] - quantity
                            if new_quantity == 0:
                                self.db.delete_stock(user_id, stock_symbol)
                            else:
                                self.db.update_stock(user_id, stock_symbol, new_quantity, stock[2])
                            self.db.add_transaction(stock[3],user_id, stock_symbol, quantity, price, datetime.datetime.now(),"SELL")
                            update.message.reply_text(f"Sold {quantity} shares of {stock_symbol} at {price} successfully!")
                            self.db.add_balance(user_id, quantity * price)
                        else:
                            raise ValueError("Error: You don't have any shares of this stock.")
                        conn.commit()
                    
                elif len(command_params) == 3:
                    update.message.reply_text("You didn't specify a price. Using the current market price.")
                    with self.db.connect_db() as conn:
                        c = conn.cursor()
                        stock = self.db.get_user_stock(user_id, stock_symbol)
                        if stock:
                            if stock[1] < quantity:
                                raise ValueError("Error: You don't have enough shares to sell.")
                            new_quantity = stock[1] - quantity
                            if new_quantity == 0:
                                self.db.delete_stock(user_id, stock_symbol)
                            else:
                                self.db.update_stock(user_id, stock_symbol, new_quantity, stock[2])
                            self.db.add_transaction(stock[3],user_id, stock_symbol, quantity, price, datetime.datetime.now(),"SELL")
                            update.message.reply_text(f"Sold {quantity} shares of {stock_symbol} at {price} successfully!")
                            self.db.add_balance(user_id, quantity * price)
                        else:
                            raise ValueError("Error: You don't have any shares of this stock.")
                        conn.commit()
                
                else:
                    update.message.reply_text("Invalid parameters. Please use /sell <symbol> <quantity> <price(optional)>")
            else:
                update.message.reply_text("You need to register first using /register.")
        except ValueError as e:
            update.message.reply_text(str(e))
        except Exception as e:
            update.message.reply_text(f"An error occurred: {str(e)}")

    def add_balance(self, update, context):
        user_id = update.message.from_user.id
        if self.db.check_if_user_exists(user_id):
            command_params = update.message.text.split()
            if len(command_params) == 2:
                amount = float(command_params[1])
                if amount <= 0:
                    update.message.reply_text("Amount must be greater than 0.")
                else:
                    self.db.add_balance(user_id, amount)
                    update.message.reply_text(f"Added {amount} to your balance.")
                    self.db.add_transaction(None,user_id, None, None, amount, datetime.datetime.now(),"DEPOSIT")
            else:
                update.message.reply_text("Invalid parameters. Please use /add_balance <amount>")
        else:
            update.message.reply_text("You need to register first using /register.")

    def withdraw(self, update, context):
        user_id = update.message.from_user.id
        if self.db.check_if_user_exists(user_id):
            command_params = update.message.text.split()
            if len(command_params) == 2:
                amount = float(command_params[1])
                if amount <= 0:
                    update.message.reply_text("Amount must be greater than 0.")
                else:
                    budget = self.db.get_user_budget(user_id)
                    if budget[0] >= amount:
                        self.db.withdraw_balance(user_id, amount)
                        update.message.reply_text(f"Withdrew {amount} from your balance.")
                        self.db.add_transaction(None,user_id, None, None, amount,  datetime.datetime.now(),"WITHDRAW")
                    else:
                        update.message.reply_text("You don't have enough balance to withdraw that amount.")
            else:
                update.message.reply_text("Invalid parameters. Please use /withdraw <amount>")
        else:
            update.message.reply_text("You need to register first using /register.")

    def withdraw_all(self, update, context):
        user_id = update.message.from_user.id
        if self.db.check_if_user_exists(user_id):
            budget = self.db.get_user_budget(user_id)
            if budget[0] > 0:
                self.db.withdraw_balance(user_id, budget[0])
                update.message.reply_text(f"Withdrew {budget[0]} from your balance.")
                self.db.add_transaction(None,user_id, None, None, budget[0], datetime.datetime.now(),"WITHDRAW")
            else:
                update.message.reply_text("You don't have any balance to withdraw.")
        else:
            update.message.reply_text("You need to register first using /register.")

    def view_transactions(self, update, context):
        if self.db.check_if_user_exists(update.message.from_user.id):
            if self.db.check_if_admin(update.message.from_user.id):
                transactions = self.db.get_transactions()
                if transactions:
                    transaction_list = ""
                    for transaction in transactions:
                        transaction_list += f"User: {transaction[1]}, Stock: {transaction[2]}, Quantity: {transaction[3]}, Price: {transaction[4]}, Type: {transaction[6]}, Date: {transaction[7]}\n"
                    update.message.reply_text(transaction_list)
                else:
                    update.message.reply_text("No transactions found.")
            else:
                update.message.reply_text("You are not authorized to view transactions.")
  
        else:
            update.message.reply_text("You need to register first using /register.")

    def get_stock_dict(self, update, context):
        update.message.reply_text(self.request.get_stock_dict())
    