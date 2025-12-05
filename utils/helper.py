from datetime import datetime
from django.utils.dateparse import parse_date
from cashbook.models import CashBook

def encode_date_time(date_time):
    return datetime.strptime(date_time, "%Y-%m-%dT%H:%M")


# Function to parse a date string into a date object
def parse_date_else_today_string(date_string = None):
    if not date_string:
        return parse_date(datetime.today().isoformat())
    else:
        return parse_date(date_string)
    

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