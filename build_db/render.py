"""
Functions for rendering date and quantity literals.
提供的代码是一个 Python 脚本，它定义了一系列用于渲染日期和数量文字以及解析 ISO 8601 日期字符串的函数。
"""
from collections import namedtuple
import re


# See https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Dates_and_numbers
Format = namedtuple('Format', ['format_string', 'include_era',
                               'remove_leading_zeros'])

YEAR_FORMATS_en = [
    Format('%Y', True, True)
]

YEAR_FORMATS_zh = [
    Format('%Y年', True, True)
]


MONTH_FORMATS_en = [
    Format('%B %Y', True, True),
    Format('%b %Y', True, True),
    *YEAR_FORMATS_en
]

MONTH_FORMATS_zh = [
    Format('%Y年%m月', True, True),
    Format('%Y年%B', True, True),
    *YEAR_FORMATS_zh
]

DAY_FORMATS_en = [
    Format('%d %B %Y', True, True),
    Format('%d %b %Y', True, True),
    Format('%B %d, %Y', True, True),
    Format('%b %d, %Y', True, True),
    Format('%d %B', False, True),
    Format('%d %b', False, True),
    Format('%B %d', False, True),
    Format('%b %d', False, True),
    Format('%Y-%m-%d', False, False),
    *MONTH_FORMATS_en
]


DAY_FORMATS_zh = [
    Format('%Y年%m月%d日', True, True),
    Format('%Y年%B%d日', True, True),
    Format('%m月%d日', False, True),
    Format('%B%d日', False, True),
    Format('%Y-%m-%d', False, False),
    *MONTH_FORMATS_zh
]


RE_LEADING_ZEROS = re.compile(r'((?<=\s)0+|^0+)')
RE_ISO_8601 = re.compile(r'(?P<year>[+-][0-9]+)-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})(?=T)')


class Date_en(object):

    LONG_MONTHS = [None, 'January', 'February', 'March', 'April', 'May', 'June', 'July',
                   'August', 'September', 'October', 'November', 'December']

    SHORT_MONTHS = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                    'Sep', 'Oct', 'Nov', 'Dec']

    def __init__(self, year, month=None, day=None):
        self._year = year
        self._month = month
        self._day = day

    @property
    def year(self):
        return self._year

    @property
    def month(self):
        return self._month

    @property
    def day(self):
        return self._day

    def strftime(self, format_string):
        out = format_string
        if self._day:
            out = out.replace('%d', '%02d' % self._day)
        if self._month:
            out = out.replace('%b', Date_en.SHORT_MONTHS[self._month])
            out = out.replace('%m', '%02d' % self._month)
            out = out.replace('%B', Date_en.LONG_MONTHS[self._month])
        out = out.replace('%Y', '%d' % abs(self._year))
        return out



class Date_zh(object):

    LONG_MONTHS = [None, '一月', '二月', '三月', '四月', '五月', '六月', '七月',
                   '八月', '九月', '十月', '十一月', '十二月']

    SHORT_MONTHS = [None, '1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月',
                    '9月', '10月', '11月', '12月']

    def __init__(self, year, month=None, day=None):
        self._year = year
        self._month = month
        self._day = day

    @property
    def year(self):
        return self._year

    @property
    def month(self):
        return self._month

    @property
    def day(self):
        return self._day

    def strftime(self, format_string):
        out = format_string
        if self._day:
            out = out.replace('%d', '%02d' % self._day)
        if self._month:
            out = out.replace('%b', Date_zh.SHORT_MONTHS[self._month])
            out = out.replace('%m', '%d' % self._month)
            out = out.replace('%B', Date_zh.LONG_MONTHS[self._month])
        out = out.replace('%Y', '%d' % abs(self._year))
        return out



def parse_iso8601_en(iso_string: str):
    match = RE_ISO_8601.match(iso_string)
    if match:
        year = int(match.group('year'))
        month = int(match.group('month'))
        day = int(match.group('day'))
        return Date_en(year, month, day)
    

def parse_iso8601_zh(iso_string: str):
    match = RE_ISO_8601.match(iso_string)
    if match:
        year = int(match.group('year'))
        month = int(match.group('month'))
        day = int(match.group('day'))
        return Date_zh(year, month, day)


def custom_strftime_en(formats, date):
    out = ['time']
    for format in formats:
        date_string = date.strftime(format.format_string)
        if format.remove_leading_zeros:
            date_string = RE_LEADING_ZEROS.sub('', date_string)
        out.append(date_string)
        if format.include_era:
            is_bc = date.year < 0
            era_strings = ['BC', 'BCE'] if is_bc else ['AD', 'CE']
            for era_string in era_strings:
                out.append(' '.join((era_string, date_string)))
                out.append(' '.join((date_string, era_string)))
    return out


def custom_strftime_zh(formats, date):
    out = ['time']
    for format in formats:
        date_string = date.strftime(format.format_string)
        if format.remove_leading_zeros:
            date_string = RE_LEADING_ZEROS.sub('', date_string)
        out.append(date_string)
        if format.include_era:
            is_bc = date.year < 0
            era_strings = ['公元前'] if is_bc else ['公元']
            for era_string in era_strings:
                out.append(''.join((era_string, date_string)))
    return out


def render_time_en(value):
    posix_string = value['time']
    precision = int(value['precision'])
    return ['time', posix_string, precision]   



def render_time_zh(value):
    posix_string = value['time']
    precision = int(value['precision'])
    return ['time', posix_string, precision]   
    

def get_unit_label_from_uri(qid, alias_db):
    try:
        labels = alias_db[qid]
    except KeyError:
        return ""
    return labels


def format_number_with_commas(number):
    return "{:,}".format(number)


def render_quantity_zh(value):
    amount = float(value['amount'])
    unit = value['unit']
    if unit.startswith("http://www.wikidata.org/entity/Q"):
        qid = unit.split("/")[-1]
        return ['quantity', qid, str(amount)]    
    else:
        return ['quantity', 'None', str(amount)]
        


def render_quantity_en(value):
    amount = float(value['amount'])
    unit = value['unit']
    if unit.startswith("http://www.wikidata.org/entity/Q"):
        qid = unit.split("/")[-1]
        return ['quantity', qid, str(amount)]    
    else:
        return ['quantity', 'None', str(amount)]



def process_literal_zh(value, alias_db_zh):
    aliases = None
    if value['type'] == 'time':
        aliases = render_time_zh(value['value'])
    elif value['type'] == 'quantity':
        aliases = render_quantity_zh(value['value'], alias_db_zh)
    return aliases


def process_literal_en(value, alias_db_en):
    aliases = None
    if value['type'] == 'time':
        aliases = render_time_en(value['value'])
    elif value['type'] == 'quantity':
        aliases = render_quantity_en(value['value'], alias_db_en)
    return aliases



if __name__ == "__main__":
    quantity = {
        "datavalue": {
            "value": {
            "amount": "+103800",
            "upperBound": "+10.375",
            "lowerBound": "+10.385",
            "unit": "http://www.wikidata.org/entity/Q712226"
            },
            "type": "quantity"
        }
    }

    time = {
        "datavalue": {
            "value": {
            "time": "+2001-12-31T00:00:00Z",
            "timezone": 0,
            "before": 0,
            "after": 0,
            "precision": 11,
            "calendarmodel": "http:\/\/www.wikidata.org\/entity\/Q1985727"
            },
            "type": "time"
        }
    }
    language = 'zh'
    if language == 'zh':
        aliases = process_literal_zh(quantity["datavalue"])
        print(aliases)
        aliases = process_literal_zh(time["datavalue"])
        print(aliases)
    else:
        aliases = process_literal_en(quantity["datavalue"])
        print(aliases)
        aliases = process_literal_en(time["datavalue"])
        print(aliases)

