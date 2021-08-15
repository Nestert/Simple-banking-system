import random
import sqlite3

conn = sqlite3.connect('card.s3db')


def generate_random_num(count_digit):
    numbers = []
    for i in range(count_digit):
        numbers.append(str(random.randint(0, 9)))
    return ''.join(numbers)


def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for i in even_digits:
        checksum += sum(digits_of(i * 2))
    return checksum % 10 == 0


class Card:
    bin = '400000'
    mii = bin[0]

    def __init__(self, acc_id):
        self.acc_id = acc_id

    def luhn(self):
        card = self.bin + self.acc_id
        evens = sum(int(i) for i in card[1::2])
        odd = []
        for i in card[::2]:
            k = int(i) * 2
            if k > 9:
                k -= 9
                odd.append(k)
            else:
                odd.append(k)
        odds = sum(odd)

        for i in range(10):
            if (evens + odds + i) % 10 == 0:
                card += str(i)
                break
        return card


class CardIssuer:
    @staticmethod
    def gen_card():
        return [Card(acc_id=generate_random_num(9)).luhn(),
                generate_random_num(4)]


class Storage:
    storage = conn.cursor()

    def add_card(self, number, pin):
        self.storage.execute("INSERT INTO card VALUES (?,?,?,'0')", (generate_random_num(3), number, pin))
        conn.commit()

    def select_card(self, number):
        self.storage.execute("SELECT * FROM card WHERE number=?", [number])
        card = self.storage.fetchone()
        return card

    def select_balance(self, number_card):
        self.storage.execute("SELECT balance FROM card WHERE number=?", [number_card])
        balance = self.storage.fetchone()
        return int(balance[0])

    def add_income_balance(self, number_card, amount):
        self.storage.execute("UPDATE card SET balance = balance + ? WHERE number=?", [amount, number_card])
        conn.commit()

    def delete_account(self, number_card):
        self.storage.execute("DELETE FROM card WHERE number=?", [number_card])
        conn.commit()



class Validator:
    @staticmethod
    def check_pin_is_valid(card, pin):
        if card is None:
            return False
        possible_pin = card[2]
        if possible_pin == pin:
            return True
        else:
            return False


class Bank:
    storage = Storage

    def issue_card(self):
        new_card = CardIssuer.gen_card()
        self.storage.add_card(self.storage, new_card[0], new_card[1])
        print(f"Your card has been created\n"
              f"Your card number:\n"
              f"{new_card[0]}\n"
              f"Your card PIN:\n"
              f"{new_card[1]}")

    def try_login(self, card_number, pin):
        card = self.storage.select_card(self.storage, card_number)
        validated = Validator.check_pin_is_valid(card, pin)
        print('You have successfully logged in!' if validated else 'Wrong card number or PIN!')
        return validated

    def balance(self, number_card):
        return self.storage.select_balance(self.storage, number_card)

    def add_income(self, number_card, amount):
        self.storage.add_income_balance(self.storage, number_card, amount)

    def alg_luhn(self, number_card):
        return luhn_checksum(number_card)

    def first_check(self, from_card, to_card):
        if not self.alg_luhn(self, to_card):
            return [False, 'Probably you made a mistake in the card number. Please try again!']
        if from_card == to_card:
            return [False, "You can't transfer money to the same account!"]
        if self.storage.select_card(self.storage, to_card) is None:
            return [False, "Such a card does not exist."]
        return [True, '']

    def try_transfer(self, from_card, to_card, amount):
        if self.balance(self, from_card) - int(amount) < 0:
            return 'Not enough money!'
        self.add_income(self, from_card, 0 - int(amount))
        self.add_income(self, to_card, int(amount))
        return 'Success!'

    def delete_account(self,number_card):
        self.storage.delete_account(self.storage, number_card)




class Flow:
    bank = Bank
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS card 
(id INTEGER PRIMARY KEY,
number TEXT,
pin TEXT,
balance INTEGER DEFAULT "0")""")
    conn.commit()
    session_card = ''

    def start(self):
        print("""1. Create an account
2. Log into account
0. Exit""")
        option = int(input('>'))
        self.pick_option(self, 1, option)

    def show_screen_two(self):
        print("""1. Balance
2. Add income
3. Do transfer
4. Close account
5. Log out
0. Exit""")
        option = int(input('>'))
        self.pick_option(self, 2, option)

    def pick_option(self, screen_num, option_num):
        if screen_num == 1:
            if option_num == 1:
                self.bank.issue_card(self.bank)
                self.start(self)
            elif option_num == 2:
                print('Enter your card number:')
                card_number = input('>')
                print('Enter your PIN:')
                pin = input('>')
                if self.bank.try_login(self.bank, card_number, pin):
                    self.session_card = card_number
                    self.show_screen_two(self)
                else:
                    self.start(self)
            elif option_num == 0:
                print('Bye!')
                exit()
        elif screen_num == 2:
            if option_num == 1:
                print(self.bank.balance(self.bank, self.session_card))
                self.show_screen_two(self)
            elif option_num == 2:
                print('Enter income:')
                amount = input('>')
                self.bank.add_income(self.bank, self.session_card, amount)
                print('Income was added!')
                self.show_screen_two(self)
            elif option_num == 3:
                card = input("""Transfer
Enter card number:
>""")
                (first_check_result, error_message) = self.bank.first_check(self.bank, self.session_card, card)
                if not first_check_result:
                    print(error_message)
                    self.show_screen_two(self)
                amount = input("""Enter how much money you want to transfer:
>""")
                print(self.bank.try_transfer(self.bank, self.session_card, card, amount))
                self.show_screen_two(self)
            elif option_num == 4:
                self.bank.delete_account(self.bank, self.session_card)
                print('The account has been closed!')
                self.session_card = ''
                self.start(self)
            elif option_num == 5:
                print('You have successfully logged out!')
                self.session_card = ''
                self.start(self)
            elif option_num == 0:
                print('Bye!')
                exit()


flow = Flow
flow.start(flow)
