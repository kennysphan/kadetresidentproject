from django.shortcuts import render
import math
import datetime
from rest_framework import viewsets
from .serializers import RotationStatusSerializer
from .models import RotationStatus
from criteria.models import Criteria
from useraccess.models import SchedulerUser
from vacation.models import VacationRequests
from schedule.models import Schedule
from schedule.models import RotationsByWeek
from settings.models import Settings

def getWeekDelta(startDate, endDate):
    #assume that every rotation and the schedule itself starts on Wednesday, per Chris
    #the idea is that both of these variables should be DateTimeField objects and we should be able to get the difference in days
    difference = endDate - startDate
    delta = difference.days

    numberOfWeeks = math.floor(delta / 7) #we use floor to round down
    return numberOfWeeks

class RotationStatusView(viewsets.ModelViewSet):
    serializer_class = RotationStatusSerializer

    def get_queryset(self):

        weeks = 52
        weekTable = []

        RotationStatus.objects.all().delete()
        scheduleStart = Settings.objects.get(pk=1).StartSchedule
        messageOne = RotationStatus(Status='Status: Adding resident requests to schedule')
        messageOne.save()

        for resident in SchedulerUser.objects.all():
            # clears resident's schedule for weekTable array
            if resident.AccessLevel != 'NA':
                weekTableRow = []
                weekTableRow.append(resident.email)
                pgy = int(resident.AccessLevel)
                weekTableRow.append(pgy)
                for i in range(52):
                    weekTableRow.append('available')
                weekTable.append(weekTableRow)

        for requests in VacationRequests.objects.all():

            resident = SchedulerUser.objects.get(email=requests.email)
            scheduleElement = None

            if Schedule.objects.filter(email=requests.email).exists():
                scheduleElement = Schedule.objects.get(email=requests.email)
            else:
                scheduleElement = Schedule(
                    email = requests.email,
                    name = resident.last_name + ", " + resident.first_name,
                    postGradLevel = resident.AccessLevel,
                    generatedSchedule = {},
                    blackoutRotations = {},
                    assignedRotations = {}
                )

            for week in range (weeks): # clears resident's schedule in database
                scheduleElement.generatedSchedule.update({week: "available"})
                if str(week) in scheduleElement.assignedRotations:
                    thisRotation = scheduleElement.assignedRotations.pop(str(week))
                    if str(thisRotation) != "None":
                        scheduleElement.generatedSchedule.update({week: thisRotation})
            scheduleElement.save()

            userSchedule = []
            residentFound = False
            counter = -1
            while not residentFound:
                counter += 1
                userSchedule = weekTable[counter]
                residentFound = (str(userSchedule[0]) == str(requests.email))
            requestOne = requests.requestOne
            requestTwo = requests.requestTwo
            requestThree = requests.requestThree
            weekOfRequestOne = getWeekDelta(scheduleStart, requestOne)
            weekOfRequestTwo = getWeekDelta(scheduleStart, requestTwo)
            weekOfRequestThree = getWeekDelta(scheduleStart, requestThree)
            scheduleElement.generatedSchedule.update({weekOfRequestOne: "VACATION"})
            scheduleElement.generatedSchedule.update({weekOfRequestTwo: "VACATION"})
            scheduleElement.generatedSchedule.update({weekOfRequestThree: "VACATION"})
            scheduleElement.blackoutRotations.update({weekOfRequestOne: "VACATION"})
            scheduleElement.blackoutRotations.update({weekOfRequestTwo: "VACATION"})
            scheduleElement.blackoutRotations.update({weekOfRequestThree: "VACATION"})
            scheduleElement.save()

            userSchedule[weekOfRequestOne + 2] = "VACATION"
            userSchedule[weekOfRequestTwo + 2] = "VACATION"
            userSchedule[weekOfRequestThree + 2] = "VACATION"

        messageTwo = RotationStatus(Status='Status: Resident blackout dates now added')
        messageTwo.save()

        errorCounter = 0
        for currentWeek in range (weeks):

            # will ignore element 0
            pgyNeeded = [0] * 6
            pgyAvailable = [0] * 6

            # loop through all criteria/rotations, ignoring those not used in current week
            # increasing pgyNeeded based on minimum required residents
            rotationOnSchedule = None
            for rotation in Criteria.objects.all():
                startWeek = getWeekDelta(scheduleStart, rotation.StartRotation)
                endWeek = getWeekDelta(scheduleStart, rotation.EndRotation)
                pgy = int(str(rotation.ResidentYear)[len(str(rotation.ResidentYear)) - 1])
                #print(rotation.RotationType + ", " + str(startWeek) + ", " + str(currentWeek) + ", " + str(endWeek))
                if startWeek <= currentWeek <= endWeek:
                    #this section is for generating dropdown list for editing final schedules
                    if RotationsByWeek.objects.filter(rotationWeek=currentWeek).exists():
                        rotationOnSchedule = RotationsByWeek.objects.get(rotationWeek=currentWeek)
                    else:
                        rotationOnSchedule = RotationsByWeek(
                            rotationWeek = currentWeek,
                            availableRotations = []
                        )
                    rotationOnSchedule.availableRotations.append(rotation.RotationType)
                    if rotationOnSchedule.availableRotations.count(rotation.RotationType) > 1:
                        rotationOnSchedule.availableRotations.remove(rotation.RotationType)
                    rotationOnSchedule.save()
                    residentsNeeded = rotation.MinResident 
                    pgyNeeded[pgy] = pgyNeeded[pgy] + residentsNeeded
                else:
                    if RotationsByWeek.objects.filter(rotationWeek=currentWeek).exists():
                        rotationOnSchedule = RotationsByWeek.objects.get(rotationWeek=currentWeek)
                        if rotation.RotationType in rotationOnSchedule.availableRotations:
                            rotationOnSchedule.availableRotations.remove(rotation.RotationType)

            # loop through all residents, ignoring those not availabvle
            # increasing pgyAvailable for each available residents
            # assumes weekTable only has residents and not chief residents
            for resident in range(len(weekTable)): #this basically is the equivalent of iterating through users
                userSchedule = weekTable[resident]
                userPgy = userSchedule[1]

                #add +2 because beginning elements are the user info
                rotation = userSchedule[currentWeek + 2]
                if rotation == 'available':
                    pgyAvailable[userPgy] += 1

            # loop through and compare pgyNeeded to pgyAvailable.
            for pgy in range(1, 6):
                if pgyNeeded[pgy] > pgyAvailable[pgy]:
                    errorCounter += 1
                    short = pgyNeeded[pgy] - pgyAvailable[pgy]
                    message = RotationStatus(Status="Status: For week " + str(currentWeek) + ", we are short " + str(short) + " residents of PGY" + str(pgy))
                    message.save()
        if errorCounter == 0:
            message = RotationStatus(Status="Status: Resident availability check successful")
            message.save()
        else:
            message = RotationStatus(Status="Status: Resident availability check failed")
            message.save()
        return RotationStatus.objects.all()
