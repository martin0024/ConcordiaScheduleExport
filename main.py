from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

# Input file containing the HTML schedule
FILE_IN = 'myconcordia.html'
FILE_OUT = 'calendar.ics'

class Course:
    def __init__(self, name, nbr, section, component, days_times, room, instructor, start_end_date):
        self.name = name
        self.nbr = nbr
        self.section = section
        self.component = component
        self.days_times = days_times
        self.room = room
        self.instructor = instructor
        self.start_end_date = start_end_date

    def __repr__(self):
        return f"Name: {self.name}\nNbr: {self.nbr}\nSection: {self.section}\nComponent: {self.component}\nDays & Times: {self.days_times}\nRoom: {self.room}\nInstructor: {self.instructor}\nStart/End Date: {self.start_end_date}"


def convert_time(time):
    return time.strftime('%Y%m%dT%H%M%S')

def parse_time(date: datetime, time_str: str):
    return datetime.strptime(f'{date.strftime("%Y-%m-%d")} {time_str}', '%Y-%m-%d %I:%M%p')

def parse_schedule(schedule):
    pattern = r'([A-Za-z]+) (\d{1,2}:\d{2}[APM]{2}) - (\d{1,2}:\d{2}[APM]{2})'

    match = re.match(pattern, schedule)

    if match:
        days_str = match.group(1)
        time_start = match.group(2)
        time_end = match.group(3)

        # Convert days to list if needed
        days = [day for day in days_str]
        return days, time_start, time_end
    else:
        print(f"Failed to parse schedule: {schedule}")  # Debugging print statement
        raise ValueError("The schedule string format is incorrect")

def generate_event(course):
    headers = ['BEGIN:VEVENT\n', 'END:VEVENT\n']
    event_content = f'SUMMARY:{course.name.split(' - ')[0]} - {course.component}\nLOCATION:{course.room}\n'
    description = f'Course Name: {course.name}\nSection: {course.section}\nInstructor: {course.instructor}\n'
    event_content += f'DESCRIPTION:{description}\nSTATUS:CONFIRMED\n'

    date_split = course.start_end_date.split(' - ')
    start_month, start_day, start_year = map(int, date_split[0].split('/'))
    end_month, end_day, end_year = map(int, date_split[1].split('/'))

    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)

    def time_convert(time):
        return datetime.strptime(time, "%I:%M%p").strftime("%H%M%S")

    time_start, time_end = parse_schedule(course.days_times)[1:]
    start_time = time_convert(time_start)
    end_time = time_convert(time_end)

    start_datetime = f"{start_date.strftime('%Y%m%d')}T{start_time}"
    end_datetime = f"{start_date.strftime('%Y%m%d')}T{end_time}"

    weekdays = parse_schedule(course.days_times)[0]
    day_map = {
        'M': 'MO', 'T': 'TU', 'W': 'WE', 'R': 'TH', 'F': 'FR', 'S': 'SA', 'U': 'SU'
    }

    byday = ','.join(day_map.get(day, '') for day in weekdays if day in day_map)
    end_occurance = f'{end_date.strftime("%Y%m%d")}T000000'

    r_rule = f'RRULE:FREQ=WEEKLY;UNTIL={end_occurance};WKST=SU;BYDAY={byday}\n'

    event_content += f"DTSTART;TZID=America/New_York:{start_datetime}\n"
    event_content += f"DTEND;TZID=America/New_York:{end_datetime}\n"
    event_content += r_rule

    return headers[0] + event_content + headers[1]


def main():
    with open(FILE_IN, 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')

    classes = []
    course_sections = soup.find_all('h3')

    for section in course_sections:
        course_name = section.text.strip()
        table = section.find_next('table')

        if table:
            class_info_table = table.find_next('table')
            if class_info_table:
                rows = class_info_table.find_all('tr')
                for row in rows:
                    columns = [td.text.strip() for td in row.find_all('td')]
                    if len(columns) == 7:
                        columns.insert(0, course_name)
                        classes.append(Course(*columns))

    print(classes)

    with open(FILE_OUT, 'w+') as f:
        CALENDAR_HEADER = 'BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\n'
        f.write(CALENDAR_HEADER)
        for course in classes:
            print('eeee')
            f.write(generate_event(course))
        f.write('END:VCALENDAR')

if __name__ == '__main__':
    main()