import re


class Inquirie:
    def __init__(self, date, subscriber, amount, inquiry_type, terms):
        self.date = date
        self.subscriber = subscriber
        self.amount = amount
        self.inquiry_type = inquiry_type
        self.terms = terms

    @classmethod
    def extract_inquiries(cls, text):
        inquiries_list = []
        lines = cls._extract_lines(text.split('\n'))
        inquirie_data_list = cls._extract_items_with_dates(lines)

        for inquiry_data in inquirie_data_list:
            if len(inquiry_data) > 5:
                inquiry_data[3] = ' '.join(inquiry_data[3:-1])
                inquiry_data[4] = inquiry_data[-1]
                inquiry_data = inquiry_data[:5]

            inquiry = Inquirie(*inquiry_data)
            inquiries_list.append(inquiry)

        return inquiries_list

    @staticmethod
    def _extract_lines(lines):
        start_index = 0
        stop_index = 0

        start_pattern_found = False
        stop_pattern_found = False

        while stop_index < len(lines):
            if not start_pattern_found and (
                    'Date' in lines[start_index]
                    and 'Subscriber' in lines[start_index + 1]
                    and 'Amount' in lines[start_index + 2]
                    and 'Type' in lines[start_index + 3]
                    and 'Terms' in lines[start_index + 4]
            ):
                start_pattern_found = True

            if not stop_pattern_found and 'END -- Experian Credit Profile Report' in lines[stop_index]:
                stop_pattern_found = True

            if start_pattern_found and stop_pattern_found:
                start_index += 6
                break

            if not start_pattern_found:
                start_index += 1

            if not stop_pattern_found:
                stop_index += 1

        lines = lines[start_index-1:stop_index]

        return lines

    @staticmethod
    def _extract_items_with_dates(items):
        result = []
        sublist = []
        date_regex = re.compile(r'\d{2}/\d{2}/\d{4}')

        for item in items:
            if date_regex.match(item):
                if sublist:
                    result.append(sublist)
                    sublist = []
            sublist.append(item)

        if sublist:
            result.append(sublist)

        return result
