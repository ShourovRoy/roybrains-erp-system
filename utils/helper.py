from datetime import datetime
from django.utils.dateparse import parse_date
from cashbook.models import CashBook
from journal.models import JournalBook

from django.utils.timezone import make_aware

def encode_date_time(date_time):
    naive_datetime = datetime.strptime(date_time, "%Y-%m-%dT%H:%M")
    return make_aware(naive_datetime)


from django.utils import timezone

# Function to parse a date string into a date object
def parse_date_else_today_string(date_string = None):
    if not date_string:
        return timezone.localdate()
    else:
        return parse_date(date_string)
    


# get journal book
def get_or_create_journal_book(business, date):


    # get todays journal
    journal_book, journal_book_created = JournalBook.objects.get_or_create(
        business=business,
        date__date=date,
        defaults={
            "total_debit": float(0.00),
            "total_credit": float(0.00),
            "date": date
        }
    )

    return journal_book

    





# check cashbook available on the given date else get previous date cashbook
def get_cashbook_on_date_or_previous(business, date):
    # get todays cashbook
    cash_book = CashBook.objects.filter(
        business=business,
        date__date=date
    ).first()

    # if not found get the latest previous cashbook
    if not cash_book:
        previous_lastest_cash_book = CashBook.objects.filter(
            business=business,
            date__date__lt=date,
        ).order_by('-date').first()

        opening_cash_balance = previous_lastest_cash_book.cash_amount if previous_lastest_cash_book else 0.0
        opening_bank_balance = previous_lastest_cash_book.bank_amount if previous_lastest_cash_book else 0.0


        # create new cashbook for the date with opening balance
        cash_book = CashBook.objects.create(
            business=business,
            date=date,
            cash_amount=opening_cash_balance,
            bank_amount=opening_bank_balance,
            status="Opening",
        )

    return cash_book