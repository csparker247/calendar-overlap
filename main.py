from enum import Enum
from typing import Self, Union, List, Set
from pathlib import Path
from copy import deepcopy


class Day(Enum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6


def str_to_day(s: str) -> Day:
    s = s.lower()
    if s in ('sunday', 'sun', 'su'):
        return Day.SUNDAY
    elif s in ('monday', 'mon', 'm'):
        return Day.MONDAY
    elif s in ('tuesday', 'tue', 't'):
        return Day.TUESDAY
    elif s in ('wednesday', 'wed', 'w'):
        return Day.WEDNESDAY
    elif s in ('thursday', 'thu', 'th', 'r'):
        return Day.THURSDAY
    elif s in ('friday', 'fri', 'f'):
        return Day.FRIDAY
    elif s in ('saturday', 'sat', 'sa'):
        return Day.SATURDAY


def str_to_time(s: str) -> float:
    h, _, m = s.partition(':')
    return float(h) + float(m) / 60


class TimeSpan:
    _day: Day = None
    _start: float = None
    _end: float = None

    def __init__(self, day: Union[str, Day], start: Union[str, float], end: Union[str, float]):
        if isinstance(day, str):
            day = str_to_day(day)
        if isinstance(start, str):
            start = str_to_time(start)
        if isinstance(end, str):
            end = str_to_time(end)
        if start >= 24:
            start -= 24 * (start // 24)
        if end >= 24:
            end -= 24 * (end // 24)
        self._day = day
        self._start = start
        self._end = end

    def __repr__(self):
        return f'TimeSpan(day={self._day.name}, start={self._start:.2f}, end={self._end:.2f})'

    def __str__(self):
        return f'{self._day.name.title()}, {self.start_str}-{self.end_str}'

    @classmethod
    def from_str(cls, s: str) -> Self:
        day, _, se = s.strip().partition(' ')
        start, end = se.split('-')
        return cls(day, start, end)

    @property
    def day(self):
        return self._day

    @property
    def start(self):
        return self._start

    @property
    def start_str(self):
        si, sd = divmod(self._start, 1)
        return f'{int(si):02}:{int(sd*60):02}'

    @property
    def end(self):
        return self._end

    @property
    def end_str(self):
        ei, ed = divmod(self._end, 1)
        return f'{int(ei):02}:{int(ed*60):02}'

    def contains(self, span: Self) -> bool:
        if span._day != self._day:
            return False

        return span._start >= self._start and span._end <= self._end


class EventTime:
    _time: TimeSpan = None
    _available: Set[str] = None
    _not_available: Set[str] = None

    def __init__(self, time: TimeSpan = None, day: Union[str, Day] = None, start: Union[str, float] = None, end: Union[str, float] = None):
        if time is None and (day is None or start is None or end is None):
            raise ValueError("Either 'time' or 'day', 'start', and 'end' must be specified")
        if time is not None:
            self._time = time
        else:
            self._time = TimeSpan(day, start, end)
        self._available = set()
        self._not_available = set()

    @property
    def time(self):
        return self._time

    @property
    def available(self):
        return self._available

    @property
    def not_available(self):
        return self._not_available

    def add_attendee(self, attendee, is_available: bool = None):
        if is_available is None:
            is_available = attendee.is_available(self.time)
        if is_available:
            self._available.add(attendee.name)
        else:
            self._not_available.add(attendee.name)

    def can_combine(self, event_time: Self) -> bool:
        if self._time.end != event_time.time.start and self._time.start != event_time.time.end:
            return False

        return self.available == event_time.available and self.not_available == event_time.not_available

    @classmethod
    def combine(cls, a: Self, b: Self) -> Self:
        day = a.time.day
        start = min(a.time.start, b.time.start)
        end = max(a.time.end, b.time.end)
        event = cls(day=day, start=start, end=end)
        event._available = deepcopy(a.available)
        event._not_available = deepcopy(a.not_available)
        return event


class Attendee:
    _availability = None

    def __init__(self, name: str):
        self._name = name
        self._availability = {
            Day.SUNDAY: [],
            Day.MONDAY: [],
            Day.TUESDAY: [],
            Day.WEDNESDAY: [],
            Day.THURSDAY: [],
            Day.FRIDAY: [],
            Day.SATURDAY: []
        }

    def __repr__(self):
        return f'Attendee(name={self._name})'

    def __str__(self):
        return self._name

    @property
    def name(self):
        return self._name

    def add_availability(self, span: TimeSpan):
        self._availability[span.day].append(span)
        self._availability[span.day].sort(key=lambda x: x.start)

    def availability(self):
        return self._availability

    def is_available(self, span: Union[TimeSpan, EventTime]) -> bool:
        if isinstance(span, EventTime):
            span = EventTime.time
        for slot in self._availability[span.day]:
            if slot.contains(span):
                return True
        return False


def load_availability(path: Union[str, Path]) -> List[Attendee]:
    """Availability file format:
    Name 1,D HH:MM-HH:MM,D HH:MM-HH:MM, ...
    Name 2,D HH:MM-HH:MM,D HH:MM-HH:MM, ...
    """
    if isinstance(path, str):
        path = Path(path)

    # read file
    with path.open() as f:
        lines = f.readlines()

    # parse
    attendees = {}
    for line_num, line in enumerate(lines):
        # split into elements
        elems = line.strip().split(',')
        if len(elems) < 2:
            print(f'Cannot parse line {line_num + 1}: {line}')
            continue

        # get attendee
        name = elems[0].strip()
        if name in attendees.keys():
            attendee = attendees[name]
        else:
            attendee = Attendee(name)
            attendees[name] = attendee

        # iterate over each availability span
        for slot in elems[1:]:
            attendee.add_availability(TimeSpan.from_str(slot))

    return list(attendees.values())


def print_availability(attendees: List[Attendee]):
    for person in attendees:
        print(f'{person.name}:')
        for day_spans in person.availability().values():
            if len(day_spans) == 0:
                continue
            day = day_spans[0].day
            print(f' - {day.name.title()}:', ', '.join([f'{span.start_str}-{span.end_str}' for span in day_spans]))


def main():
    # load attendees
    attendees = load_availability('availability.txt')

    # evaluate 15 min time blocks
    time_blocks = []
    for day in (Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY, Day.THURSDAY, Day.FRIDAY):
        for start_hour in range(8, 17):
            for start_min in (0, 0.25, 0.5, 0.75):
                start = start_hour + start_min
                end = start + 0.25
                event = EventTime(day=day, start=start, end=end)
                for person in attendees:
                    event.add_attendee(person)
                time_blocks.append(event)

    # combine adjacent time blocks
    combined = []
    current = time_blocks[0]
    for block in time_blocks[1:]:
        if current.can_combine(block):
            current = EventTime.combine(current, block)
        else:
            combined.append(current)
            current = block

    print(f'time blocks: {len(time_blocks)}, combined: {len(combined)}')

    test = combined[0]
    print(f'{test.time}:')
    print('Available: ')
    for n in test.available:
        print(f' - {n}')


if __name__ == '__main__':
    main()

