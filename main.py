import re
from datetime import datetime
import pickle

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def input_error(message):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ValueError, TypeError) as e:
                print(message)
        return wrapper
    return decorator

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    @input_error("Name cannot be empty.")
    def __init__(self, value):
        if not value:
            raise ValueError

        super().__init__(value)

class Phone(Field):
    @input_error("Phone number must be 10 digits.")
    def __init__(self, value):
        if not re.match(r'^\d{10}$', value):
            raise ValueError

        super().__init__(value)

class Birthday(Field):
    @staticmethod
    def is_valid_format(value):
        return bool(re.match(r'^\d{2}\.\d{2}\.\d{4}$', value))

    @staticmethod
    def is_valid_date(value):
        try:
            birthday_date = datetime.strptime(value, "%d.%m.%Y")
            current_date = datetime.now()
            return birthday_date <= current_date
        except ValueError:
            return False

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        
    @input_error("Phone number must be 10 digits.")
    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def delete_phone(self, phone_number):
        self.phones = [phone for phone in self.phones if phone.value != phone_number]

    def edit_phone(self, old_phone_number, new_phone_number):
        for phone in self.phones:
            if phone.value == old_phone_number:
                phone.value = new_phone_number

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone.value

    def __str__(self):
        phone_numbers = '; '.join(str(p) for p in self.phones)
        birthday_str = f', birthday: {self.birthday}' if self.birthday else ''
        return f"Contact name: {self.name.value}, phones: {phone_numbers}{birthday_str}"

class AddressBook:
    def __init__(self):
        self.data = {}

    def parse_input(self, user_input):
        cmd, *args = user_input.split()
        cmd = cmd.strip().lower()
        return cmd, args

    def add_record(self, record):
        self.data[record.name.value] = record

    def delete_record(self, name):
        if name in self.data:
            del self.data[name]
            print(f"Contact '{name}' deleted successfully.")
        else:
            print("Contact not found.")

    def find_record(self, name):
        return self.data.get(name)

    def add_birthday(self, name, birthday):
        if not Birthday.is_valid_format(birthday):
            print("Invalid date format. Use DD.MM.YYYY")
            return
        
        if not Birthday.is_valid_date(birthday):
            print("Invalid date. Please enter a valid date.")
            return

        if name in self.data:
            self.data[name].birthday = Birthday(birthday)
            print(f"Birthday added for contact '{name}'.")
        else:
            print("Contact not found.")

    def show_birthday(self, name):
        if name in self.data and self.data[name].birthday:
            print(f"{name}'s birthday is on {self.data[name].birthday}")
        else:
            print("Birthday information not found.")

    def birthdays(self, days=7):
        current_date = datetime.now()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                try:
                    birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").replace(year=current_date.year)
                    if birthday_date < current_date:
                        birthday_date = birthday_date.replace(year=current_date.year + 1)
                    days_until_birthday = (birthday_date - current_date).days
                    if 0 <= days_until_birthday <= days:
                        upcoming_birthdays.append((record.name.value, birthday_date))
                except ValueError:
                    print(f"Error processing birthday for {record.name.value}. Invalid date format.")
        upcoming_birthdays.sort(key=lambda x: x[1])
        for name, birthday_date in upcoming_birthdays:
            print(f"{name}'s birthday is on {birthday_date.strftime('%Y-%m-%d')}")

    def change(self, name, new_phone_number):
        if len(new_phone_number) != 10 or not new_phone_number.isdigit():
            print("Phone number must be 10 digits.")
            return
        
        if name in self.data:
            record = self.data[name]
            record.phones = []
            record.add_phone(new_phone_number)
            print(f"Phone number for contact '{name}' updated successfully.")
        else:
            print("Contact not found.")

    def del_contact(self, name):
        if name in self.data:
            del self.data[name]
            print(f"Contact '{name}' deleted successfully.")
        else:
            print("Contact not found.")

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = book.parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            if len(args) < 2:
                print("Please provide both name and phone number.")
                continue
            name, *phone_numbers = args
            if not all(re.match(r'^\d{10}$', phone) for phone in phone_numbers):
                print("Phone number must be 10 digits.")
                continue
            record = Record(name)
            for phone_number in phone_numbers:
                record.add_phone(phone_number)
            book.add_record(record)
            print(f"Contact '{name}' added successfully.")

        elif command == "change":
            if len(args) != 2:
                print("Please provide name and the new phone number.")
                continue
            name, new_phone_number = args
            book.change(name, new_phone_number)

        elif command == "phone":
            if len(args) != 1:
                print("Please provide name.")
                continue
            name = args[0]
            if name in book.data:
                record = book.data[name]
                print(f"Phone numbers for contact '{name}': {', '.join(str(phone) for phone in record.phones)}")
            else:
                print("Contact not found.")

        elif command == "all":
            for record in book.data.values():
                print(record)

        elif command == "add-birthday":
            if len(args) != 2:
                print("Please provide both name and birthday in the format DD.MM.YYYY.")
                continue
            name, birthday = args
            book.add_birthday(name, birthday)

        elif command == "show-birthday":
            if len(args) != 1:
                print("Please provide name.")
                continue
            name = args[0]
            book.show_birthday(name)

        elif command == "birthdays":
            if args:
                days = int(args[0])
                book.birthdays(days)
            else:
                book.birthdays()

        elif command == "del":
            if len(args) != 1:
                print("Please provide name.")
                continue
            name = args[0]
            book.del_contact(name)

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
