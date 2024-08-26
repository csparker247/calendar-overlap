import find_time


def main():
    # load attendees
    invitees = find_time.load('availability.txt')

    # evaluate 0.25 hour time blocks and merge them based on availability
    blocks = find_time.calc_overlap(invitees, hours=range(8, 17),
                                    blocks_per_hour=4, merge=True)

    by_num_available = sorted(blocks, key=lambda x: x.num_available,
                              reverse=True)
    by_length = sorted(by_num_available,
                       key=lambda x: x.time.end - x.time.start, reverse=True)
    for idx, block in enumerate(by_num_available):
        if block.num_available == 0:
            continue
        print(
            f'{idx + 1}) {block.time} ({block.num_available} of {block.num_invited} available):')
        print(' - Available:', ', '.join(sorted(block.available)))
        print(' - Unavailable:', ', '.join(sorted(block.not_available)))


if __name__ == '__main__':
    main()
