from avail import load_availability
from classes import Day, EventTime


def main():
    # load attendees
    attendees = load_availability('availability.txt')

    # evaluate 0.5 hour time blocks
    time_blocks = []
    for day in (Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY, Day.THURSDAY, Day.FRIDAY):
        for start_hour in range(8, 17):
            for start_min in (0, .25, 0.5, .75):
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

    by_attendees = sorted(combined, key=lambda x: x.num_available, reverse=True)
    by_length = sorted(by_attendees, key=lambda x: x.time.end - x.time.start, reverse=True)
    for idx, block in enumerate(by_attendees):
        print(
            f'{idx + 1}) {block.time} ({block.num_available} of {block.num_invited} available):')
        print(' - Available:', ', '.join(sorted(block.available)))
        print(' - Unavailable:', ', '.join(sorted(block.not_available)))


if __name__ == '__main__':
    main()

