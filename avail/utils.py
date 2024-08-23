from typing import List

from avail.classes import Attendee


def print_avail(attendees: List[Attendee]):
    for person in attendees:
        print(f'{person.name}:')
        for day_spans in person.availability().values():
            if len(day_spans) == 0:
                continue
            day = day_spans[0].day
            print(f' - {day.name.title()}:', ', '.join(
                [f'{span.start_str}-{span.end_str}' for span in day_spans]))
