# -*- coding: utf-8 -*-
"""
class for course schedule
"""

from bs4 import BeautifulSoup
import requests
from .sslType import SSLAdapter
import ssl


class CourseSchedule():
    """class that contains schedule of a course"""

    INDEX_OF_DAY = {'MON': 0, 'TUE': 24, 'WED': 48, 'THU': 72, 'FRI': 96}

    def get_schedule(self):
        return self.__schedule

    def parse_schedule(self, courseCode):
        """parse the course schedule and convert it to a binary string"""

        self.__schedule = {}

        # get html table format of course schedule
        print("Getting schedule for " + courseCode.upper() + "...", end=" ")
        schedule = self.__fetch_schedule(courseCode)
        print("Done")

        # convert the course schedule to a binary string
        #
        # it is a 120 bit string and every bit represents half an hour
        # bit 1 means that there is a class at that time
        # bit 0 means there is none
        #
        # for each day the time is from 8:30 am to 8:30 am
        # this should be able to cover the schedule of most of the
        # courses in NTU
        for i in range(len(schedule) // 7):
            for j in range(7):
                string = str(schedule[i * 7 + j])
                string = string[7:len(string) - 9]
                if j == 0 and string != "":  # get the index of the course
                    currentIndex = string
                    self.__schedule[currentIndex] = "0" * 120
                elif j == 3:  # get the days that have this course
                    indexOfDay = CourseSchedule.INDEX_OF_DAY[string]
                elif j == 4:  # get the time of that course in a day
                    numOfTimeSlots = self.__get_time(string)
                    indexOfTime = (int(string[:4]) - 830) // 50
                # if j reaches 6, prasing is done
                # the following code is to modify the binary string
                # according to the parsing result
                elif j == 6:
                    startingIndex = indexOfDay + indexOfTime
                    endingIndex = startingIndex + numOfTimeSlots
                    self.__schedule[currentIndex] = \
                        self.__schedule[currentIndex][:startingIndex] + \
                        "1" * numOfTimeSlots + \
                        self.__schedule[currentIndex][endingIndex:]
                else:
                    pass

    def __fetch_schedule(self, courseCode):
        """fetch course schedule using course code from NTU website"""

        # generate URL for the course
        url = \
            "https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE" + \
            ".main_display1?acadsem=2016;1&r_search_type=F&r_subj_code=" + \
            courseCode + \
            "&boption=Search&staff_access=false&acadsem=2016;1&r_course_yr="

        # try connecting to the server
        try:
            s = requests.Session()
            s.mount("https://", SSLAdapter(ssl.PROTOCOL_TLSv1))
            r = s.post(url)
        # exit program if server is not reachable
        except requests.exceptions.ConnectionError:
            print("Connection error. Cannot connect to NTU server.")
            print("Please try to run this script again.")
            exit(-1)

        # create BeautifulSoup object for later parsing
        soup = BeautifulSoup(r.text)

        # save the table which contains the course schedule
        try:
            schedule = soup.find_all("table")[1].find_all("td")
        except IndexError:
            print("\nThe course code does not exist in NTU database" +
                  "for this semester.")
            print("Please make sure you entered a valid course code.")
            exit(-1)
        schedule = schedule[:]

        return schedule

    def __get_time(self, timeString):
        """convert the time format '0830-0930'
        to number of bits in the binary string
        """

        timeInterval = int(timeString[5:]) - int(timeString[:4])
        numOfTimeSlots = timeInterval // 50

        return numOfTimeSlots
