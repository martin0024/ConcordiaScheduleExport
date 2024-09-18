from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from loading_spinner import loading_spinner

FILE_IN = 'myconcordia.html'
FILE_OUT = 'calendar.ics'

class Course:
    def __init__(self, name, nbr, section, component, days_times, room, instructor, start_end_date, status):
        self.name = name
        self.nbr = nbr
        self.section = section
        self.component = component
        self.days_times = days_times
        self.room = room
        self.instructor = instructor
        self.start_end_date = start_end_date
        self.status = status

    def __repr__(self):
        return (f"Name: {self.name}\nNbr: {self.nbr}\nSection: {self.section}\nComponent: {self.component}\n"
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

def get_first_class_day(start_date, days):
    """Find the first occurrence of a class based on the day of the week."""
    day_map = {'Mo': 0, 'Tu': 1, 'We': 2, 'Th': 3, 'Fr': 4}
    first_class_day = min([day_map[day] for day in days if day in day_map])
    days_ahead = (first_class_day - start_date.weekday() + 7) % 7
    return start_date + timedelta(days=days_ahead)

def generate_event(course):
    headers = ['BEGIN:VEVENT\n', 'END:VEVENT\n']
    description = (
        f"Course Name: {course.name}\\n"
        f"Course Number: {course.nbr}\\n"
        f"Section: {course.section}\\n"
        f"Instructor: {course.instructor}"
    )
    event_content = f'SUMMARY:{course.name.split(" - ")[0]} - {course.component}\nLOCATION:{course.room}\nDESCRIPTION:{description}\nSTATUS:CONFIRMED\n'

    if course.days_times == 'TBA':
        return ''

    date_split = course.start_end_date.split(' - ')
    start_month, start_day, start_year = map(int, date_split[0].split('/'))
    end_month, end_day, end_year = map(int, date_split[1].split('/'))

    start_date = datetime(start_year, start_month, start_day)
    end_date = datetime(end_year, end_month, end_day)

    days, time_start, time_end = parse_schedule(course.days_times)
    start_time = time_convert(time_start)
    end_time = time_convert(time_end)

    first_class_date = get_first_class_day(start_date, days)

    start_datetime = f"{first_class_date.strftime('%Y%m%d')}T{start_time}"
    end_datetime = f"{first_class_date.strftime('%Y%m%d')}T{end_time}"

    day_map = {'Mo': 'MO', 'Tu': 'TU', 'We': 'WE', 'Th': 'TH', 'Fr': 'FR'}
    byday = ','.join(day_map.get(day, '') for day in days if day in day_map)
    end_occurance = f'{end_date.strftime("%Y%m%d")}T000000'

    r_rule = f'RRULE:FREQ=WEEKLY;UNTIL={end_occurance};WKST=SU;BYDAY={byday}\n'
    alarm = (
        'BEGIN:VALARM\n'
        'TRIGGER:-PT15M\n'
        'ACTION:DISPLAY\n'
        'DESCRIPTION:Reminder\n'
        'END:VALARM\n'
    )

    event_content += f"DTSTART;TZID=America/New_York:{start_datetime}\n"
    event_content += f"DTEND;TZID=America/New_York:{end_datetime}\n"
    event_content += r_rule
    event_content += alarm

    return headers[0] + event_content + headers[1]

def main():
    with open(FILE_IN, 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')

    course_names = [name.text.strip() for name in soup.find_all('h3', {'class': 'ui-bar'})]

    courses = []
    sections = soup.find_all('td', {'class': 'gsgroupbox'})

    for section, course_name in zip(sections, course_names):
        rows = section.find_all('tr', {'id': re.compile(r'^trCLASS_MTG_VW')})
        status = [status.text.strip() for status in section.find_all('span', {'class': 'PSEDITBOX_DISPONLY'})]
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 6:
                nbr = cells[0].find('span').text.strip()
                section = cells[1].find('a').text.strip()
                component = cells[2].find('span').text.strip()
                days_times = cells[3].find('span').text.strip()
                room = cells[4].find('span').text.strip()
                instructor = cells[5].find('span').text.strip()
                start_end_date = cells[6].find('span').text.strip()

                courses.append(Course(course_name, nbr, section, component, days_times, room, instructor, start_end_date, status))

    print(f'Found \033[31m{len(courses)}\033[0m courses.')
    loading_spinner(5, message='Generating calendar file... Please wait...')


    with open(FILE_OUT, 'w+') as f:
        CALENDAR_HEADER = 'BEGIN:VCALENDAR\nVERSION:2.0\nCALSCALE:GREGORIAN\n'
        f.write(CALENDAR_HEADER)
        for course in courses:
            if course.status[0] == 'Enrolled':
                event_data = generate_event(course)
                if event_data:
                    f.write(event_data)
        f.write('END:VCALENDAR')
        print(f"Calendar file generated: \033[31m{FILE_OUT}\033[0m")



if __name__ == '__main__':
    main()