from typing import List, Iterable, Union

from find_time.classes import Person, Day, EventTime


def print_avail(attendees: Union[Person, Iterable[Person]]):
    if isinstance(attendees, Person):
        attendees = (attendees,)
    for person in attendees:
        print(f'{person.name}:')
        for day_spans in person.availability_by_day():
            if len(day_spans) == 0:
                continue
            day = day_spans[0].day
            print(f' - {day.name.title()}:', ', '.join(
                [f'{span.start_str}-{span.end_str}' for span in day_spans]))


def calc_overlap(people: Iterable[Person], days: Iterable[Day] = Day,
                 hours: Iterable[int] = range(0, 24), blocks_per_hour: int = 4,
                 merge: bool = False) -> List[EventTime]:
    # params for iterating over sub-intervals
    block_duration = 1. / blocks_per_hour
    sub_blocks = range(blocks_per_hour)

    # collect blocks
    blocks = []
    for day in days:
        for start_hour in hours:
            for start_min in (i / blocks_per_hour for i in sub_blocks):
                start = start_hour + start_min
                end = start + block_duration
                event = EventTime(day=day, start=start, end=end)
                for person in people:
                    event.add_person(person)
                blocks.append(event)
    if merge:
        blocks = merge_adjacent(blocks)
    return blocks


def merge_adjacent(blocks: Iterable[EventTime]) -> List[EventTime]:
    """Merges adjacent time blocks where availability does not differ. Assumes
    the input is sorted by start time."""
    combined = []
    current = blocks[0]
    for block in blocks[1:]:
        if current.can_combine(block):
            current = EventTime.combine(current, block)
        else:
            combined.append(current)
            current = block
    combined.append(current)
    return combined
