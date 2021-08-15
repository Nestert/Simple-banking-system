import random


def generate_random_num(count_digit):
    numbers = []
    for i in range(count_digit):
        numbers.append(str(random.randint(0, 9)))
    return ''.join(numbers)


class Card:
    bin = '400000'
    mii = bin[0]

    def __init__(self, acc_id, checksum):
        self.acc_id = acc_id
        self.checksum = checksum

    def full_card_num(self):
        return self.bin + self.acc_id + self.checksum


class CardIssuer:
    @staticmethod
    def gen_card():
        return (Card(acc_id=generate_random_num(9), checksum=generate_random_num(1)).full_card_num(),
                generate_random_num(4))


class Storage:
    storage = dict()

    def store_card_with_pin(self, key, value):
        self.storage[key] = value


class Validator:
    @staticmethod
    def check_card_is_valid(storage, card_number, pin):
        possible_pin = storage.get(card_number)
        if possible_pin == pin:
            return True
        else:
            return False


class Bank:
    storage = Storage

    def issue_card(self):
        new_card = CardIssuer.gen_card()

        self.storage.store_card_with_pin(self.storage, new_card[0], new_card[1])
        print(f"""Your card has been created
Your card number:
{new_card[0]}
Your card PIN:
{new_card[1]}""")

    def try_login(self, card_number, pin):
        validated = Validator.check_card_is_valid(self.storage.storage, card_number, pin)
        print('You have successfully logged in!' if validated else 'Wrong card number or PIN!')
        return validated


class Flow:
    bank = Bank

    def start(self):
        print("""1. Create an account
2. Log into account
0. Exit""")
        option = int(input('>'))
        self.pick_option(self, 1, option)

    def show_screen_two(self):
        print("""1. Balance
2. Log out
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
                    self.show_screen_two(self)
                else:
                    self.start(self)
            elif option_num == 0:
                print('Bye!')
                exit()
        elif screen_num == 2:
            if option_num == 1:
                print('Balance: 0')
                self.show_screen_two(self)
            elif option_num == 2:
                print('You have successfully logged out!')
                self.start()
            elif option_num == 0:
                print('Bye!')
                exit()


flow = Flow
flow.start(flow)
