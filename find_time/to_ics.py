import argparse
from datetime import datetime as dt, timedelta
from pathlib import Path

from dateutil import tz
from ics import Calendar, Event
from ics.grammar.parse import ContentLine

import find_time

date_format = '%Y-%m-%d'
time_format = '%H:%M'


def next_weekday_after_date(weekday: int, date: dt):
    offset = (weekday - date.isoweekday()) % 7
    return date + timedelta(offset)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='Input file')
    parser.add_argument('-o', '--output', required=True, help='Output file')
    parser.add_argument('-s', '--start-date', required=True,
                        help='Start date: YYYY-MM-DD')
    parser.add_argument('-e', '--end-date', required=True,
                        help='End date: YYYY-MM-DD')
    parser.add_argument('-t', '--timezone', help='Timezone',
                        default='US/Eastern')
    args = parser.parse_args()

    # calendar
    c = Calendar()

    # load people
    people = find_time.load(args.input)

    # parse start and end date
    timezone = tz.gettz(args.timezone)
    start_date = dt.strptime(args.start_date, date_format).replace(
        tzinfo=timezone)
    end_date = dt.strptime(args.end_date, date_format).replace(tzinfo=timezone)
    end_date_str = end_date.astimezone(tz.UTC).strftime('%Y%m%dT%H%M%SZ')

    # add availability to calendar
    print(f'adding availability')
    for person in people:
        for a in person.availability_by_block():
            d = next_weekday_after_date(a.day.value, start_date)
            h, m = a.start_int
            st = d.replace(hour=h, minute=m)
            h, m = a.end_int
            et = d.replace(hour=h, minute=m)

            e = Event()
            e.name = person.name
            e.begin = st
            e.end = et
            e.extra.append(ContentLine(name='RRULE',
                                       value=f'FREQ=WEEKLY;UNTIL={end_date_str}'))
            c.events.add(e)

    # write calendar
    print('writing .ics')
    with Path(args.output).open('w') as f:
        f.write(c.serialize())
    print('done')


if __name__ == '__main__':
    main()
