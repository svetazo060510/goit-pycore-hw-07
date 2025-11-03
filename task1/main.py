from collections import UserDict
from datetime import datetime, date, timedelta

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

if __name__ == "__main__":
    try:
        # Create a new AddressBook
        book = AddressBook()

        # Create and add Record for John
        john_record = Record("John")
        john_record.add_phone("1234567890")
        john_record.add_phone("5555555555")
        john_record.add_birthday("05.11.1985")
        book.add_record(john_record)

        # Create and add Record for Jane
        jane_record = Record("Jane")
        jane_record.add_phone("9876543210")
        jane_record.add_birthday("03.11.1990") 
        book.add_record(jane_record)

        # Create and add Record for Bill
        bill_record = Record("Bill")
        bill_record.add_phone("7777777777")
        bill_record.add_birthday("08.11.1992")
        book.add_record(bill_record)
        
        # Create and add Record for Sue
        sue_record = Record("Sue")
        sue_record.add_phone("8888888888")
        sue_record.add_birthday("15.11.1991")
        book.add_record(sue_record)

        # Print all Records
        print("All records:")
        for name, record in book.data.items():
            print(record)

        # Find and update phone for John
        john = book.find("John")
        john.edit_phone("1234567890", "1112223333")

        print(f"\nUpdated John: {john}")  # Contact name: John, phones: 1112223333; 5555555555

        # Find a valid phone of John
        found_phone = john.find_phone("5555555555")
        print(f"\nFound phone for {john.name.value}: {found_phone.value}")  # Виведення: 5555555555

        # Delete record for Jane
        book.delete("Jane")
        print("\nAll records after deleting Jane:")
        for name, record in book.data.items():
            print(record)
        
        #Test Birthdays
        print("\nUpcoming Birthdays:")
        upcoming = book.get_upcoming_birthdays()
        print(upcoming)

    except (ValueError, KeyError, AttributeError) as e:       
        print(f"An error occurred: {e}")
    
        # Test wrong data
        try:
            john.add_phone("123")
        except ValueError as e:
            print(f"\nValidation error: {e}")

    except (ValueError, KeyError, AttributeError) as e:
        print(f"An error occurred: {e}")