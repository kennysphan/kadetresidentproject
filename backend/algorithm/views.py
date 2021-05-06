from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .serializers import AlgorithmStatusSerializer
from .models import AlgorithmStatus
import math
import pulp
import datetime
from criteria.models import Criteria
from useraccess.models import SchedulerUser
from vacation.models import VacationRequests
from schedule.models import Schedule
from settings.models import Settings

def getWeekDelta(startDate, endDate):
    #assume that every rotation and the schedule itself starts on Wednesday, per Chris
    #the idea is that both of these variables should be DateTimeField objects and we should be able to get the difference in days
    difference = endDate - startDate
    delta = difference.days

    numberOfWeeks = math.floor(delta / 7) #we use floor to round down
    return numberOfWeeks

class AlgorithmStatusView(viewsets.ModelViewSet):
    serializer_class = AlgorithmStatusSerializer

    def get_queryset(self):

        #information/constraints needed for scheduling algorithm
        weeks = 52
        residents = []
        rotations = []
        rotationMinMaxResidents = {}
        rotationMinMaxContinous = {}
        essentialRotations = [] #that are not overnight rotations
        overnightRotations = []
        otherRotations = []
        rotationWeeks = {}
        pgyRotation = {}
        pgyResident = {}
        unavailable = {}
        assigned = {}

        #to hold finished schedule
        weekTable = []

        AlgorithmStatus.objects.all().delete()
        scheduleStart = Settings.objects.get(pk=1).StartSchedule

        for resident in Schedule.objects.all():
            vacations = []
            other = []
            residents.append(resident.email) 
            weekTableRow = []
            weekTableRow.append(resident.email)
            pgy = int(resident.postGradLevel)
            pgyResident.update({resident.email: pgy}) 
            weekTableRow.append(pgy)
            for i in range(weeks):
                weekTableRow.append(resident.generatedSchedule.get(str(i)))
                if resident.generatedSchedule.get(str(i)) == "VACATION":
                    vacations.append(i)
                else:
                    if resident.generatedSchedule.get(str(i)) != "available":
                        other.append(i)
                        resident.assignedRotations.update({i: resident.generatedSchedule.get(str(i))})
                        resident.save()
            weekTable.append(weekTableRow)
            if len(vacations) > 0:
                unavailable.update({resident.email: vacations})
            if len(other) > 0:
                assigned.update({resident.email: other}) 

        for rotation in Criteria.objects.all():
                startWeek = getWeekDelta(scheduleStart, rotation.StartRotation)
                endWeek = getWeekDelta(scheduleStart, rotation.EndRotation)
                pgy = int(str(rotation.ResidentYear)[len(str(rotation.ResidentYear)) - 1]) #Force cast as int
                rotations.append(rotation.RotationType)
                rotationMinMaxResidents.update({rotation.RotationType: (rotation.MinResident, rotation.MaxResident)})
                rotationMinMaxContinous.update({rotation.RotationType: (rotation.MinContinuedWeeks, rotation.MaxContinuedWeeks)})
                if rotation.Essential:
                    if not rotation.Overnight: #to track essential rotations that are not also overnight
                        essentialRotations.append(rotation.RotationType)
                elif rotation.Overnight:
                    overnightRotations.append(rotation.RotationType)
                else:
                    otherRotations.append(rotation.RotationType)
                rotationWeeks.update({rotation.RotationType: [i for i in range(startWeek, endWeek + 1)]})
                pgyRotation.update({rotation.RotationType: pgy})


        # PuLP 'problem'
        problem = pulp.LpProblem("resident_scheduler", pulp.LpMaximize)

        # PuLP variables
		# assignments = pulp.LpVariable.dicts("Assignments", ((week, resident, rotation) for week in range(weeks) for resident in residents for rotation in rotations), cat="Binary")		
        essential = pulp.LpVariable.dicts("Essential", ((week, resident, rotation) for week in range(weeks) for resident in residents for rotation in essentialRotations), cat="Binary")
        overnight = pulp.LpVariable.dicts("Overnight", ((week, resident, rotation) for week in range(weeks) for resident in residents for rotation in overnightRotations), cat="Binary")
        other = pulp.LpVariable.dicts("Other", ((week, resident, rotation) for week in range(weeks) for resident in residents for rotation in otherRotations), cat="Binary")
        is_assigned = pulp.LpVariable.dicts("Is_Assigned", residents, cat="Binary")

        # PuLP constraints
        for week in range(weeks):
            for rotation in essentialRotations:
                if week in rotationWeeks[rotation]:
                    # In every week, each rotation is assigned by min/max required residents
                    problem += pulp.lpSum(essential[week, resident, rotation] for resident in residents) >= rotationMinMaxResidents[rotation][0] #min
                    problem += pulp.lpSum(essential[week, resident, rotation] for resident in residents) <= rotationMinMaxResidents[rotation][1] #max
                else:
                    # otherwise, if rotation does not span current week, no residents assigned
                    problem += pulp.lpSum(essential[week, resident, rotation] for resident in residents) == 0

            for rotation in overnightRotations:
                if week in rotationWeeks[rotation]:
                    # In every week, each rotation is assigned by min/max required residents
                    problem += pulp.lpSum(overnight[week, resident, rotation] for resident in residents) >= rotationMinMaxResidents[rotation][0] #min
                    problem += pulp.lpSum(overnight[week, resident, rotation] for resident in residents) <= rotationMinMaxResidents[rotation][1] #max
                else:
                    # otherwise, if rotation does not span current week, no residents assigned
                    problem += pulp.lpSum(overnight[week, resident, rotation] for resident in residents) == 0

            for rotation in otherRotations:
                if week in rotationWeeks[rotation]:
                    # In every week, each rotation is assigned by min/max required residents
                    problem += pulp.lpSum(other[week, resident, rotation] for resident in residents) >= rotationMinMaxResidents[rotation][0] #min
                    problem += pulp.lpSum(other[week, resident, rotation] for resident in residents) <= rotationMinMaxResidents[rotation][1] #max
                else:
                    # otherwise, if rotation does not span current week, no residents assigned
                    problem += pulp.lpSum(other[week, resident, rotation] for resident in residents) == 0

            for resident in residents:
                # Nobody is assigned multiple rotations in the same week
                problem += pulp.lpSum(essential[week, resident, rotation] for rotation in essentialRotations) <= 1
                problem += pulp.lpSum(overnight[week, resident, rotation] for rotation in overnightRotations) <= 1
                problem += pulp.lpSum(other[week, resident, rotation] for rotation in otherRotations) <= 1
				# residents with incorrect PGY level are not available for rotation
                for rotation in essentialRotations:
                    if week in rotationWeeks[rotation]:
                        if pgyRotation[rotation] != pgyResident[resident]:
                            problem += essential[week, resident, rotation] == 0
                for rotation in overnightRotations:
                    if week in rotationWeeks[rotation]:
                        if pgyRotation[rotation] != pgyResident[resident]:
                            problem += overnight[week, resident, rotation] == 0
                for rotation in otherRotations:
                    if week in rotationWeeks[rotation]:
                        if pgyRotation[rotation] != pgyResident[resident]:
                            problem += other[week, resident, rotation] == 0

        # essential rotation cannot follow overnight
        for resident in residents:
            for week in range(1, weeks):
                problem += pulp.lpSum(essential[week, resident, rotation] for rotation in essentialRotations) + pulp.lpSum(overnight[week - 1, resident, rotation] for rotation in overnightRotations) <= 1

        for resident, blockedOut in unavailable.items():
            for week in blockedOut:
				# Nobody is assigned a rotation in a week they are unavailable
                for rotation in essentialRotations:
                    if week in rotationWeeks[rotation]:
                        problem += essential[week, resident, rotation] == 0
                for rotation in overnightRotations:
                    if week in rotationWeeks[rotation]:
                        problem += overnight[week, resident, rotation] == 0
                for rotation in otherRotations:
                    if week in rotationWeeks[rotation]:
                        problem += other[week, resident, rotation] == 0

        # residents should be assigned between a min and max number of weeks on a rotation
        for rotation in essentialRotations:
            for week in rotationWeeks[rotation]:
                #if (week - rotationMinMaxContinous[rotation][0]) in rotationWeeks[rotation]:
                    #for resident in residents:
                        #problem += (pulp.lpSum(essential[someWeeks, resident, rotation] for someWeeks in range(week - rotationMinMaxContinous[rotation][0], week + 1)) == rotationMinMaxContinous[rotation][0]) or (pulp.lpSum(essential[someWeeks, resident, rotation] for someWeeks in range(week - rotationMinMaxContinous[rotation][0], week + 1)) == 0)
                if ((week - rotationMinMaxContinous[rotation][1] - 1) in rotationWeeks[rotation]):
                    for resident in residents:
                        problem += pulp.lpSum(essential[someWeeks, resident, rotation] for someWeeks in range(week - rotationMinMaxContinous[rotation][1] - 1, week + 1)) <= rotationMinMaxContinous[rotation][1]
        for rotation in overnightRotations:
            for week in rotationWeeks[rotation]:
                #if (week - rotationMinMaxContinous[rotation][0]) in rotationWeeks[rotation]:
                    #for resident in residents:
                        #problem += (pulp.lpSum(overnight[someWeeks, resident, rotation] for someWeeks in range(week - rotationMinMaxContinous[rotation][0], week + 1)) == rotationMinMaxContinous[rotation][0]) or (pulp.lpSum(overnight[someWeeks, resident, rotation] for someWeeks in range(week - rotationMinMaxContinous[rotation][0], week + 1)) == 0)
                if ((week - rotationMinMaxContinous[rotation][1] - 1) in rotationWeeks[rotation]):
                    for resident in residents:
                        problem += pulp.lpSum(overnight[someWeeks, resident, rotation] for someWeeks in range(week - rotationMinMaxContinous[rotation][1] - 1, week + 1)) <= rotationMinMaxContinous[rotation][1]
        for rotation in otherRotations:
            for week in rotationWeeks[rotation]:
                #if (week - rotationMinMaxContinous[rotation][0]) in rotationWeeks[rotation]:
                    #for resident in residents:
                        #problem += (pulp.lpSum(other[someWeeks, resident, rotation] for someWeeks in range(week - rotationMinMaxContinous[rotation][0], week + 1)) == rotationMinMaxContinous[rotation][0]) or (pulp.lpSum(other[someWeeks, resident, rotation] for someWeeks in range(week - rotationMinMaxContinous[rotation][0], week + 1)) == 0)
                if ((week - rotationMinMaxContinous[rotation][1] - 1) in rotationWeeks[rotation]):
                    for resident in residents:
                        problem += pulp.lpSum(other[someWeeks, resident, rotation] for someWeeks in range(week - rotationMinMaxContinous[rotation][1] - 1, week + 1)) <= rotationMinMaxContinous[rotation][1]

        for resident, alreadyScheduled in assigned.items():
            currentResident = Schedule.objects.get(email=resident)
            for week in alreadyScheduled:
                rotation = currentResident.assignedRotations.get(str(week))
				# preassigned rotations
                if rotation in essentialRotations:
                    problem += essential[week, resident, rotation] == 1
                elif rotation in overnightRotations:
                    problem += overnight[week, resident, rotation] == 1
                elif rotation in otherRotations:
                    problem += other[week, resident, rotation] == 1

        for resident in residents:
            # residents only work one kind of shift
            for week in range(weeks):
                problem += pulp.lpSum(essential[week, resident, rotation] for rotation in essentialRotations) + pulp.lpSum(overnight[week, resident, rotation] for rotation in overnightRotations) + pulp.lpSum(other[week, resident, rotation] for rotation in otherRotations) <= 1

        for resident in residents:
            # Nobody works too many rotations
            problem += pulp.lpSum(essential[week, resident, rotation] for week in range(weeks) for rotation in essentialRotations) + pulp.lpSum(overnight[week, resident, rotation] for week in range(weeks) for rotation in overnightRotations) + pulp.lpSum(other[week, resident, rotation] for week in range(weeks) for rotation in otherRotations) <= weeks

        # Constrain 'is_assigned' auxiliary variable
        for week in range(weeks):
            for resident in residents:
                for rotation in essentialRotations:
                    if week in rotationWeeks[rotation]:
                        problem += is_assigned[resident] >= essential[week, resident, rotation]
                for rotation in overnightRotations:
                    if week in rotationWeeks[rotation]:
                        problem += is_assigned[resident] >= overnight[week, resident, rotation]
                for rotation in otherRotations:
                    if week in rotationWeeks[rotation]:
                        problem += is_assigned[resident] >= other[week, resident, rotation]

        for resident in residents:
            problem += is_assigned[resident] <= pulp.lpSum(essential[week, resident, rotation] for week in range(weeks) for rotation in essentialRotations) + pulp.lpSum(overnight[week, resident, rotation] for week in range(weeks) for rotation in overnightRotations) + pulp.lpSum(other[week, resident, rotation] for week in range(weeks) for rotation in otherRotations)

        # PuLP objective
        problem += pulp.lpSum(is_assigned[resident] for resident in residents)
		
		# Solve problem
        problem.solve()
        outcome = str(pulp.LpStatus[problem.status])
        pulpStatus = AlgorithmStatus(Status='')
        if outcome == 'Optimal':
            pulpStatus = AlgorithmStatus(Status='Algorithm succeeded in creating schedule')
            pulpStatus.save()
            for week in range(weeks):
                for resident in residents:
                    for rotation in essentialRotations:
                        if week in rotationWeeks[rotation]:
                            if pulp.value(essential[week, resident, rotation]) == 1:
                                currentResident = Schedule.objects.get(email=resident)
                                currentResident.generatedSchedule.update({week: rotation})
                                currentResident.save()
                                #message = AlgorithmStatus(Status="For week " + str(week) + ", " + str(resident) + " is assigned to " + str(rotation))
                                #message.save()
                    for rotation in overnightRotations:
                        if week in rotationWeeks[rotation]:
                            if pulp.value(overnight[week, resident, rotation]) == 1:
                                currentResident = Schedule.objects.get(email=resident)
                                currentResident.generatedSchedule.update({week: rotation})
                                currentResident.save()
                                #message = AlgorithmStatus(Status="For week " + str(week) + ", " + str(resident) + " is assigned to " + str(rotation))
                                #message.save()
                    for rotation in otherRotations:
                        if week in rotationWeeks[rotation]:
                            if pulp.value(other[week, resident, rotation]) == 1:
                                currentResident = Schedule.objects.get(email=resident)
                                currentResident.generatedSchedule.update({week: rotation})
                                currentResident.save()
                                #message = AlgorithmStatus(Status="For week " + str(week) + ", " + str(resident) + " is assigned to " + str(rotation))
                                #message.save()
        else:
            pulpStatus = AlgorithmStatus(Status='Algorithm failed in creating schedule')
            pulpStatus.save()
        return AlgorithmStatus.objects.all()
