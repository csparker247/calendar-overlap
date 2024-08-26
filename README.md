# find-time
A simple tool for finding regular availability overlaps between event invitees.

## Usage
```shell
python -m pip install find-time

find-time --help
```

## Availability file format

The following format is supported by `find_time.parse`:

```
# anything following a pound sign (#) is a comment
# blank lines are ignored

## entry format ##
# name:      Any string. Terminates when encountering a colon (:)
# day:       Full day names (Sunday, Monday, Tuesday, ...), three-letter 
#            abbreviations (Sun, Mon, Tue, ...), or day short codes 
#            (Su, M, T, W, R, F, Sa). Case-insensitive.
# time:      {HH}:{MM} in 24hr format, e.g. 13:00
# timespan:  {time}-{time} which correlate to start and end time, e.g. 13:00-14:00
# entry:     {name}: {day} {timespan}(, {day} {timespan})*

##  example entries ##
# {name}: {day} {timespan}
John Smith: Monday 11:00-12:00

# {name}: {list of day shortcodes} {timespan}
# short codes: su,m,t,w,r,f,sa
John Smith: MWF 14:00-15:00

# {name}: {day} {timespan}, {day} {timespan}, ...
John Smith: TR 8:00-12:15, TR 15:30-17:00

# multiple entries for a single person
Jane Smith: MF 14:30-17:00
Jane Smith: W 15:30-17:00
```

## Special note
This tool was created quickly to evaluate availability overlaps for a small 
number of invitees (one or two dozen). It is not optimized for performance and 
really should not be trusted for large events.