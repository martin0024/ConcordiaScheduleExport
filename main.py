from bs4 import BeautifulSoup
from datetime import datetime
import re

# Input file containing the HTML schedule
FILE_IN = 'myconcordia.html'
FILE_OUT = 'calendar.ics'

class Course:
    def __init__(self, nbr, section, component, days_times, room, instructor, start_end_date):
        self.nbr = nbr
        self.section = section
        self.component = component
        self.days_times = days_times
        self.room = room
        self.instructor = instructor
        self.start_end_date = start_end_date

    def __repr__(self):
        return (f"Nbr: {self.nbr}\nSection: {self.section}\nComponent: {self.component}\n"
                f"Days & Times: {self.days_times}\nRoom: {self.room}\nInstructor: {self.instructor}\n"
                f"Start/End Date: {self.start_end_date}")

def parse_schedule(schedule):
    pattern = r'([A-Za-z]+) (\d{1,2}:\d{2}[APM]{2}) - (\d{1,2}:\d{2}[APM]{2})'

    match = re.match(pattern, schedule)

    if match:
        days_str = match.group(1)
        time_start = match.group(2)
        time_end = match.group(3)

        days = [days_str[i:i+2] for i in range(0, len(days_str), 2)]

        return days, time_start, time_end
    else:
        print(f"Failed to parse schedule: {schedule}")
        raise ValueError("The schedule string format is incorrect")

def time_convert(time):
    return datetime.strptime(time, "%I:%M%p").strftime("%H%M%S")

def generate_event(course):
    headers = ['BEGIN:VEVENT\n', 'END:VEVENT\n']
    event_content = f'SUMMARY:Course {course.nbr} - {course.component}\nLOCATION:{course.room}\n'
    description = (f'Course Number: {course.nbr}\nSection: {course.section}\nInstructor: {course.instructor}\n')
    event_content += f'DESCRIPTION:{description}\nSTATUS:CONFIRMED\n'

    if(course.days_times == 'TBA'):
        return ''

    date_split = course.start_end_date.split(' - ')
    start_month, start_day, start_year = map(int, date_split[0].split('/'))
    end_month, end_day, end_year = map(int, date_split[1].split('/'))

    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)

    days, time_start, time_end = parse_schedule(course.days_times)
    start_time = time_convert(time_start)
    end_time = time_convert(time_end)

    start_datetime = f"{start_date.strftime('%Y%m%d')}T{start_time}"
    end_datetime = f"{start_date.strftime('%Y%m%d')}T{end_time}"

    day_map = {'Mo': 'MO', 'Tu': 'TU', 'We': 'WE', 'Th': 'TH', 'Fr': 'FR'}
    byday = ','.join(day_map.get(day, '') for day in days if day in day_map)
    end_occurance = f'{end_date.strftime("%Y%m%d")}T000000'

    r_rule = f'RRULE:FREQ=WEEKLY;UNTIL={end_occurance};WKST=SU;BYDAY={byday}\n'

    event_content += f"DTSTART;TZID=America/New_York:{start_datetime}\n"
    event_content += f"DTEND;TZID=America/New_York:{end_datetime}\n"
    event_content += r_rule

    return headers[0] + event_content + headers[1]

def main():
    with open(FILE_IN, 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')

    courses = []
    rows = soup.find_all('tr', {'id': re.compile(r'^trCLASS_MTG_VW')})

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 6:
            cells[0].find('span').text.strip()
            nbr = cells[0].find('span').text.strip()
            section = cells[1].find('a').text.strip()
            component = cells[2].find('span').text.strip()
            days_times = cells[3].find('span').text.strip()
            room = cells[4].find('span').text.strip()
            instructor = cells[5].find('span').text.strip()
            start_end_date = cells[6].find('span').text.strip()

            courses.append(Course(nbr, section, component, days_times, room, instructor, start_end_date))

    with open(FILE_OUT, 'w+') as f:
        CALENDAR_HEADER = 'BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\n'
        f.write(CALENDAR_HEADER)
        for course in courses:
            f.write(generate_event(course))
        f.write('END:VCALENDAR')

if __name__ == '__main__':
    main()