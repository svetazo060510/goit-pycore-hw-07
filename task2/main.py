from collections import UserDict
from datetime import datetime, date, timedelta
from functools import wraps

# Classes
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            parsed_date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(parsed_date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_str):
        phone = Phone(phone_str)
        self.phones.append(phone)

    def remove_phone(self, phone_str):
        phone_obj = self.find_phone(phone_str)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError(f"Phone {phone_str} not found.")

    def edit_phone(self, old_phone_str, new_phone_str):
        old_phone_obj = self.find_phone(old_phone_str)
        if old_phone_obj:
            self.phones.remove(old_phone_obj)
            self.add_phone(new_phone_str)
            return
        raise ValueError(f"Phone {old_phone_str} not found.")

    def find_phone(self, phone_str):
        for phone_obj in self.phones:
            if phone_obj.value == phone_str:
                return phone_obj
        return None

    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"

class AddressBook(UserDict):    
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)
        else:
            raise KeyError(f"Contact {name} not found.")
        
    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = date.today()
        seven_days_from_today = today + timedelta(days=7)

        for record in self.data.values():
            if record.birthday:
                birthday_date = record.birthday.value
                
                birthday_this_year = birthday_date.replace(year=today.year)
                
                if birthday_this_year < today:
                    birthday_this_year = birthday_date.replace(year=today.year + 1)

                if today <= birthday_this_year < seven_days_from_today:
                    day_of_week = birthday_this_year.isoweekday()

                    if day_of_week >= 6:
                        if day_of_week == 6: 
                            upcoming_congratulation = birthday_this_year + timedelta(days=2)
                        elif day_of_week == 7: 
                            upcoming_congratulation = birthday_this_year + timedelta(days=1)
                    else:
                        upcoming_congratulation = birthday_this_year
                    
                    if upcoming_congratulation >= seven_days_from_today:
                        continue
                        
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulation_date": upcoming_congratulation.strftime("%Y.%m.%d")
                    })

        return upcoming_birthdays

# New Logic
def parse_input(user_input):
    # Parse input into command and args
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    # Decorator to catch ValueError, KeyError, IndexError.
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Error: {e}"
        except KeyError as e:
            return f"Error: Contact '{e.key}' not found."
        except IndexError:
            return "Error: Not enough arguments provided. Please try again."
    return inner

# Function for commands
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone) 
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact's phone updated."
    else:
        raise KeyError(name)

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return "; ".join(p.value for p in record.phones)
    else:
        raise KeyError(name)

@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "No contacts found."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_str = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday_str)
        return "Birthday added."
    else:
        raise KeyError(name)

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        if record.birthday:
            return record.birthday.value.strftime("%d.%m.%Y")
        else:
            return "Birthday not set for this contact."
    else:
        raise KeyError(name)

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays this week."
    return "\n".join([f"Name: {item['name']}, Date: {item['congratulation_date']}" for item in upcoming])

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        try:
            user_input = input("Enter a command: ")
            if not user_input:
                continue
                
            command, *args = parse_input(user_input)

            if command in ["close", "exit"]:
                print("Good bye!")
                break

            elif command == "hello":
                print("How can I help you?")

            elif command == "add":
                print(add_contact(args, book))

            elif command == "change":
                print(change_contact(args, book))

            elif command == "phone":
                print(show_phone(args, book))

            elif command == "all":
                print(show_all(book))

            elif command == "add-birthday":
                print(add_birthday(args, book))

            elif command == "show-birthday":
                print(show_birthday(args, book))

            elif command == "birthdays":
                print(birthdays(args, book))

            else:
                print("Invalid command.")
        
        except ValueError as e:
            if "not enough values to unpack" in str(e):
                print("Invalid command. Please enter a command and arguments.")
            else:
                print(e)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()