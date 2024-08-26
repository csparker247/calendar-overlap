from copy import deepcopy
from enum import Enum
from typing import Union, Self, Set


class Day(Enum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6


def str_to_day(s: str) -> Day:
    s = s.title()
    if s in ('Sunday', 'Sun', 'Su'):
        return Day.SUNDAY
    elif s in ('Monday', 'Mon', 'M'):
        return Day.MONDAY
    elif s in ('Tuesday', 'Tue', 'T'):
        return Day.TUESDAY
    elif s in ('Wednesday', 'Wed', 'W'):
        return Day.WEDNESDAY
    elif s in ('Thursday', 'Thu', 'Th', 'R'):
        return Day.THURSDAY
    elif s in ('Friday', 'Fri', 'F'):
        return Day.FRIDAY
    elif s in ('Saturday', 'Sat', 'Sa'):
        return Day.SATURDAY


def str_to_time(s: str) -> float:
    h, _, m = s.partition(':')
    return float(h) + float(m) / 60


class TimeSpan:
    _day: Day = None
    _start: float = None
    _end: float = None

    def __init__(self, day: Union[str, Day], start: Union[str, float],
                 end: Union[str, float]):
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
        return f'{int(si):02}:{int(sd * 60):02}'

    @property
    def end(self):
        return self._end

    @property
    def end_str(self):
        ei, ed = divmod(self._end, 1)
        return f'{int(ei):02}:{int(ed * 60):02}'

    def contains(self, span: Self) -> bool:
        if span._day != self._day:
            return False

        return span._start >= self._start and span._end <= self._end


class EventTime:
    _time: TimeSpan = None
    _available: Set[str] = None
    _not_available: Set[str] = None

    def __init__(self, time: TimeSpan = None, day: Union[str, Day] = None,
                 start: Union[str, float] = None,
                 end: Union[str, float] = None):
        if time is None and (day is None or start is None or end is None):
            raise ValueError(
                "Either 'time' or 'day', 'start', and 'end' must be specified")
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
    def num_invited(self):
        return len(self._available) + len(self._not_available)

    @property
    def available(self):
        return self._available

    @property
    def num_available(self):
        return len(self._available)

    @property
    def not_available(self):
        return self._not_available

    def add_person(self, person, is_available: bool = None):
        if is_available is None:
            is_available = person.is_available(self.time)
        if is_available:
            self._available.add(person.name)
        else:
            self._not_available.add(person.name)

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


class Person:
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
