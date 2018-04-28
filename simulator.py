'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

class Task:
    def __init__(self, process_id, cpu_time_requested, arrive_time):
            self.process_id = process_id
            self.arrive_time = arrive_time
            self.cpu_time_requested = cpu_time_requested
            self.cpu_time_left = cpu_time_requested
    def __repr__(self):
            return ('[process_id: %d, cpu_time_requested: %d,  cpu_time_left: %d]'%(self.process_id, self.cpu_time_requested, self.cpu_time_left))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    current_time = 0
    first_task = Task(process_list[0].id, process_list[0].burst_time, process_list[0].arrive_time)
    task_queue = [first_task]
    moreProcesses = True
    schedule = []

    while len(task_queue) != 0 or moreProcesses:
        time_spent = 0
        if len(task_queue) != 0:
            head_task = task_queue[0]
            # head_task has now got cpu time

            if head_task.cpu_time_left > time_quantum:
                head_task.cpu_time_left -= time_quantum
                time_spent = time_quantum
            else:
                time_spent = head_task.cpu_time_left
                head_task.cpu_time_left = 0

            # pop from head
            task_queue = task_queue[1:]

            if head_task.cpu_time_left > 0:
                task_queue.append(head_task)

            #TODO: Append to schedule only when there is a change in task
            schedule.append((current_time, head_task.process_id))
        else:
            time_spent = 1

        current_time += time_spent

        new_processes, moreProcesses = get_new_processes(process_list, current_time - time_spent, current_time)
        # add new tasks
        add_to_process_list(new_processes, task_queue)

    #TODO: Add Waiting time
    return (schedule, 0)

def add_to_process_list(new_processes, current_task_queue):
    for process in new_processes:
        found = False
        for task in current_task_queue:
            if process.id == task.process_id:
                found = True
                task.cpu_time_requested += process.burst_time
                task.cpu_time_left += process.burst_time
        if not found:
            current_task_queue.append(Task(process.id, process.burst_time, process.arrive_time))

def get_new_processes(process_list, fromTime, toTime):
    new_processes = []
    moreProcesses = False
    for process in process_list:
        if process.arrive_time > fromTime and process.arrive_time <= toTime:
            new_processes.append(process)
        if process.arrive_time > fromTime:
            moreProcesses = True
    return new_processes, moreProcesses

def SRTF_scheduling(process_list):
    current_time = 0
    first_process = process_list[0]
    first_task = Task(first_process.id, first_process.burst_time, first_process.arrive_time)
    task_list = [first_task]
    current_task = first_task
    more_processes = True

    schedule = [(0, first_task.process_id)]

    while more_processes or len(task_list) > 0:
        if current_task != None:
            # check to see if there is a shorter process in the queue
            task_with_shortest_time = current_task
            for task in task_list:
                if task.cpu_time_left < current_task.cpu_time_left:
                    task_with_shortest_time = task

            if task_with_shortest_time.process_id != current_task.process_id:
                # switch the task
                current_task = task_with_shortest_time
                schedule.append((current_time, current_task.process_id))

            current_task.cpu_time_left -= 1
            if current_task.cpu_time_left == 0:
                # Task is done. delete task from task_list
                task_index = -1
                for i, task in enumerate(task_list):
                    if task.process_id == current_task.process_id:
                        task_index = i

                task_list.__delitem__(task_index)
                current_task = None

        current_time += 1
        # there should be only one process
        new_processes, more_processes = get_new_processes(process_list, current_time - 1, current_time)

        # add_to_task_queue
        add_to_process_list(new_processes, task_list)

        if current_task == None or current_task.cpu_time_left == 0:
            # Find the next shortest task
            task_with_shortest_time = None
            for task in task_list:
                if task_with_shortest_time == None:
                    task_with_shortest_time = task
                elif task.cpu_time_left < task_with_shortest_time:
                    task_with_shortest_time = task

            current_task = task_with_shortest_time
            if current_task != None:
                schedule.append((current_time, current_task.process_id))
    return (schedule, 0.0)

def SJF_scheduling(process_list, alpha):
    class BurstTimeHistory:
        def __init__(self):
            self.burst_times = []

        def add_burst_time(self, process_id, burst_time):
            if len(self.burst_times) < process_id + 1:
                self.burst_times.append(burst_time)
            else:
                self.burst_times[process_id] = burst_time

        def get_last_burst_time(self, process_id):
            if len(self.burst_times) < process_id + 1:
                return -1
            return self.burst_times[process_id]
    wt = [0,0,0,0]
    schedule = []
    first_process = process_list[0]
    first_task = Task(first_process.id, first_process.burst_time, first_process.arrive_time)
    task_list = [first_task]
    current_time = 0
    current_task = first_task
    history = BurstTimeHistory()
    prediction = BurstTimeHistory()
    prediction.add_burst_time(current_task.process_id, 5)
    moreProcesses = True
    numTasks = 0
    while moreProcesses or len(task_list) > 0:
        if current_task != None:
            schedule.append((current_time, current_task.process_id))
            numTasks += 1
            current_time += current_task.cpu_time_requested
            current_task.cpu_time_left = 0
            time_spent_doing_task = current_task.cpu_time_requested
            history.add_burst_time(current_task.process_id, current_task.cpu_time_requested)

            current_task_position = -1
            for i, task in enumerate(task_list):
                if current_task.process_id == task.process_id:
                    current_task_position = i
            task_list.__delitem__(current_task_position)

            # Increment waiting times for all the tasks that are in the task_list
            for task in task_list:
                if task != current_task:
                    wt[task.process_id] += time_spent_doing_task
                    print 'Increasing wait time of process ' + str(task.process_id) + ' by time_spend_doing_task:' + str(time_spent_doing_task)
            current_task = None
        else:
            # No need to increase wait times as there are no elements in the task queue
            current_time += 1
            time_spent_doing_task = 1

        new_processes, moreProcesses = get_new_processes(process_list, current_time - time_spent_doing_task, current_time)

        for process in new_processes:
            if process.arrive_time < current_time:
                print 'Increasing wait time of process ' + str(process.id) + ' by ' + str(current_time - process.arrive_time)
                wt[process.id] += current_time - process.arrive_time

        add_to_process_list(new_processes, task_list)
        shortest_job = get_shortest_job(task_list, history, prediction, alpha)

        if shortest_job[0] != -1:
            for task in task_list:
                if task.process_id == shortest_job[0]:
                    prediction.add_burst_time(task.process_id, shortest_job[1])
                    current_task = task

    average_wait_time = 0
    for wait_time in wt:
        average_wait_time += wait_time
    average_wait_time /= 4
    return (schedule,average_wait_time)

def get_shortest_job(task_list, history, prediction, alpha):
    shortest_job_time = (-1, 100000000)

    for task in task_list:
        tn = history.get_last_burst_time(task.process_id)
        if tn == -1:
            #task has never been executed
            toenplus1 = 5
        else:
            toen = prediction.get_last_burst_time(task.process_id)
            if toen == -1:
                print 'Shouldnt happen'

            toenplus1 = alpha * tn + (1 - alpha) * toen

        if toenplus1 < shortest_job_time[1]:
            shortest_job_time = (task.process_id, toenplus1)

    return shortest_job_time

def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result

def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])
