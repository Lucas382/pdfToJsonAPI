import re

class Creditor:
    def __init__(
        self,
        name,
        opened_date,
        original_amount,
        charge_off_amount,
        status_date,
        past_due,
        last_paid_date,
        balance_date,
        current_balance,
        account_condition,
        payment_status,
        account_type,
        account_number,
        responsibility,
        account_terms,
        worst_delinquency,
        worst_delinq_date,
        months_reviewed
    ):
        self.name = name
        self.opened_date = opened_date
        self.original_amount = original_amount
        self.charge_off_amount = charge_off_amount
        self.status_date = status_date
        self.past_due = past_due
        self.last_paid_date = last_paid_date
        self.balance_date = balance_date
        self.current_balance = current_balance
        self.account_condition = account_condition
        self.payment_status = payment_status
        self.account_type = account_type
        self.account_number = account_number
        self.responsibility = responsibility
        self.account_terms = account_terms
        self.worst_delinquency = worst_delinquency
        self.worst_delinq_date = worst_delinq_date
        self.months_reviewed = months_reviewed

    @classmethod
    def extract_creditors(cls, text):
        creditors_list = []
        lines = cls._extract_lines(text.split('\n'))
        creditors_data_list = cls._extract_items(lines)
        creditors_data = cls._extract_creditors(creditors_data_list)

        for creditor in creditors_data:
            creditor = Creditor(*creditor)
            creditors_list.append(creditor)

        return creditors_list


    @staticmethod
    def _extract_lines(lines):
        start_index = 0
        stop_index = 0

        start_pattern_found = False
        stop_pattern_found = False

        while stop_index < len(lines):
            if not start_pattern_found and (
                    'Open' in lines[start_index]
                    and 'Date' in lines[start_index + 1]
                    and 'Original' in lines[start_index + 2]
                    and 'Amount' in lines[start_index + 3]
                    and 'Status' in lines[start_index + 4]
            ):
                start_pattern_found = True

            if not stop_pattern_found and (
                    'Date' in lines[stop_index]
                    and 'Subscriber' in lines[stop_index + 1]
                    and 'Amount' in lines[stop_index + 2]
                    and 'Type' in lines[stop_index + 3]
                    and 'Terms' in lines[stop_index + 4]
            ):
                stop_pattern_found = True

            if start_pattern_found and stop_pattern_found:
                while 'Months Reviewed:' not in lines[stop_index]:
                    stop_index -= 1

                break

            if not start_pattern_found:
                start_index += 1

            if not stop_pattern_found:
                stop_index += 1

        lines = lines[start_index-1:stop_index+2]

        return lines

    @staticmethod
    def _extract_items(lines):
        itens = []

        start_index = 0
        stop_index = 0

        start_pattern_found = False
        stop_pattern_found = False

        for i, line in enumerate(lines):
            if 'Revolving Accounts' in line:
                break

            if not start_pattern_found and ('Open' in lines[start_index]):
                start_pattern_found = True

            if not stop_pattern_found and ('Months Reviewed:' in lines[stop_index]):
                stop_pattern_found = True

            if start_pattern_found and stop_pattern_found:
                start_index -= 1
                stop_index += 2

                itens.append(lines[start_index:stop_index])

                start_index = i
                stop_index = i
                start_pattern_found = False
                stop_pattern_found = False

            if not start_pattern_found:
                start_index += 1

            if not stop_pattern_found:
                stop_index += 1

        return itens

    @staticmethod
    def _extract_creditors(creditors_data_list):
        def is_money(value):
            pattern = r'^\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?$'
            return bool(re.match(pattern, value))

        creditor_list = []
        for creditor_chunk in creditors_data_list:
            creditor = [creditor_chunk[0]]

            # ----- First Table ------
            date_regex = re.compile(r'\d{2}/\d{2}/\d{4}')
            header_end = 1
            row_start = 0
            row_end = 0

            for i, data in enumerate(creditor_chunk):
                if date_regex.match(data):
                    row_start = i
                    header_end = i
                    break

            for i, data in enumerate(creditor_chunk):
                if 'Account' in data and 'Condition:' in creditor_chunk[i + 1]:
                    row_end = i
                    break


            headers = [f'{creditor_chunk[i]} {creditor_chunk[i+1]}' for i in range(1, header_end, 2)]
            headers = [item.strip() for item in headers if item.strip()]
            row = creditor_chunk[row_start:row_end]

            creditor.append(row[0])
            headers.remove('Open Date')
            row.pop(0)

            creditor.append(row[0])
            headers.remove('Original Amount')
            row.pop(0)

            if 'Charge Off Amount' in headers[0]:
                creditor.append(row[0])
                headers.remove('Charge Off Amount')
                row.pop(0)
            else:
                creditor.append('N/A')

            creditor.append(row[0])
            headers.remove('Status Date')
            row.pop(0)

            if is_money(row[0]):
                headers.remove('Past Due')
                creditor.append(row[0])
            else:
                headers.remove('Past Due')
                creditor.append('N/A')

            creditor.append(row[0])
            headers.remove('Last Paid Date')
            row.pop(0)

            if is_money(row[0]) and 'Scheduled Payment' in headers[0]:
                headers.pop(0) #Remove 'Scheduled Payment'

                row.pop(0)

            creditor.append(row[0])
            headers.remove('Balance Date')
            row.pop(0)

            if row and is_money(row[0]):
                headers.pop(0)  # Remove 'Current Balance'
                creditor.append(row[0])
                row.pop(0)
            else:
                headers.pop(0)
                creditor.append('N/A')

            #----End First Table

            if creditor_chunk[row_end+2] != 'Account #:': #account_condition
                creditor.append(creditor_chunk[row_end+2])
            else:
                creditor.append('N/A')
                row_end += 1

            creditor.append(creditor_chunk[row_end+6]) # payment_status
            creditor.append(creditor_chunk[row_end+10]) # account_type
            creditor.append(creditor_chunk[row_end+4]) # account_number
            creditor.append(creditor_chunk[row_end+8]) # responsibility
            creditor.append(creditor_chunk[row_end+12]) # account_terms.

            worst_delinquency_index = 0
            worst_delinq_date_index = 0
            months_reviewed_index = 0

            for i, data in enumerate(creditor_chunk):
                if 'Worst Delinquency:' in data:
                    worst_delinquency_index = i+1
                if 'Worst Delinq Date:' in data:
                    worst_delinq_date_index = i+1
                if 'Months Reviewed:' in data:
                    months_reviewed_index = i+1

            if 'Worst Delinq Date:' in creditor_chunk[worst_delinquency_index]:
                creditor.append('N/A')
            else:
                creditor.append(creditor_chunk[worst_delinquency_index: worst_delinq_date_index - 1][0])

            if 'Months Reviewed:' in creditor_chunk[worst_delinq_date_index]:
                creditor.append('N/A')
            else:
                creditor.append(creditor_chunk[worst_delinq_date_index: months_reviewed_index -1][0])

            creditor.append(creditor_chunk[-1]) #months_reviewed

            creditor_list.append(creditor)

        return creditor_list
