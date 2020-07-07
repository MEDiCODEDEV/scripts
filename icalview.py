#!/usr/bin/env python3

# https://gist.github.com/ParagDoke/2388d7311f11cab4fa5f5538fa694d0e

# The only examples are the tests:
# /usr/lib/python3/dist-packages/icalendar/tests/

import sys

from icalendar import Calendar
import datetime

import argparse


def read_ics_file(infile):
    """Parse an ics file into a dictionary.
    """
    cal = Calendar.from_ical(open(infile, 'rb').read())

    # Get the local timezone
    localtz = datetime.datetime.now().astimezone().tzinfo

    event = {}

    for component in cal.walk():
        if component.name != 'VEVENT':
            continue

        if 'SUMMARY' in event:
            print("Yikes, more than one event!")

        event['SUMMARY'] = component.get('summary')
        event['DESCRIPTION'] = component.get('description')
        event['LOCATION'] = component.get('location')

        event['DTSTART'] = component.get('DTSTART').dt
        event['DTEND'] = component.get('DTEND').dt

        # I don't know what the dtstamp or exdate are. No docs.
        # dtstamp = component.get('DTSTAMP')
        # exdate = component.get('exdate')

        # Rewrite into current timezone
        event['LOCALSTART'] = event['DTSTART'].astimezone(localtz)
        event['LOCALEND'] = event['DTEND'].astimezone(localtz)
        # dtstamp.dt = dtstamp.dt.astimezone(localtz)

    return event


def print_event(event):
    """Print in an informal but readable way."""

    print(f"START: {event['LOCALSTART'].strftime('%a, %d %b %Y %I:%M %Z')}")
    if event['DTSTART'].tzinfo != event['LOCALSTART'].tzinfo:
        print(f"      ({event['DTSTART'].strftime('%a, %d %b %Y %I:%M %Z')})")
    print(f"  END: {event['LOCALEND'].strftime('%a, %d %b %Y %I:%M %Z')}")
    if event['DTEND'].tzinfo != event['LOCALEND'].tzinfo:
        print(f"      ({event['DTEND'].strftime('%a, %d %b %Y %I:%M %Z')})")
    print("SUMMARY", event['SUMMARY'])
    print("LOCATION", event['LOCATION'])

    # Description for some events is really long.
    if len(event['DESCRIPTION']) > 300:
        print("DESCRIPTION", event['DESCRIPTION'][:300], "...")
    else:
        print("DESCRIPTION", event['DESCRIPTION'])


def remind_for_event(ev):
    """Create a line that can be added to a file for /usr/bin/remind."""

    desc = ev['DESCRIPTION'].replace('\n\n', '\n').replace('\n', ' ||| ')
    print(f"REM {ev['LOCALSTART'].strftime('%d %m %Y')} +1 MSG {ev['SUMMARY']} ||| LOCATION {ev['LOCATION']} ||| DESCRIPTION: ||| {desc}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parse ical files")
    parser.add_argument('-f', action="store", dest="format", default="text",
                        help='Output format: text (default), remind')
    parser.add_argument('files', nargs='+', help="Input ical files")
    args = parser.parse_args(sys.argv[1:])
    # print("args", args)

    events = [ read_ics_file(f) for f in args.files ]

    for ev in events:
        if args.format == "remind":
            remind_for_event(ev)

        else:
            print_event(ev)
