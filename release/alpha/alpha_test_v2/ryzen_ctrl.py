# output codes:
#  0 - okay
#  1 - unknown
#  2 - need to be root
#  3 - unsafe (set safe to 0 to be able to do it (why would you?)
#  4 - this folder (cpu) does not exist

import os
import subprocess


safe = 1 # prevent a total lock of the system (tdp bellow 4W or disabling all cores)

cpufolder = '/sys/devices/system/cpu/'


if subprocess.check_output(['whoami'], shell=True, text=True).split('\n')[:-1][0] == 'root':
    edit = 1
else:
    edit = 0

def corestate(core, state):  # core numbers starts with 0 but the core 0 cannot be disabled is safe = 1
    if edit == 1 :
        if os.path.isdir(cpufolder + 'cpu' + str(core)):
            if core == 0:
                if safe == 0: # safety
                    os.system('echo ' + str(state) + ' > ' + cpufolder + 'cpu' + str(core) + '/online')
                    return 0
                else :
                    return 3
            else:
                os.system('echo ' + str(state) + ' > ' + cpufolder + 'cpu' + str(core) + '/online')
        else:
            return 4
    else :
        return 2


def getinfo(data):
    if data == 'max_freq':
        cmdoutput = subprocess.check_output(['cpupower frequency-info | grep "Maximum Frequency:"'], shell=True, text=True).split(' ')
        output = [cmdoutput[-2], cmdoutput[-1].split('\n')[0][:-1]]
        return output
    elif data == 'min_freq':
        cmdoutput = subprocess.check_output(['cpupower frequency-info | grep "Lowest Frequency:"'], shell=True, text=True).split(' ')
        output = [cmdoutput[-2], cmdoutput[-1].split('\n')[0][:-1]]
        return output
    elif data == 'governors':
        cmdoutput = subprocess.check_output(['cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors'], shell=True, text=True).split(' ')
        return cmdoutput[:-1]
    elif data == 'governor':
        cmdoutput = subprocess.check_output(['cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor'], shell=True, text=True)
        return cmdoutput[:-1]
    elif data == 'current_freq':
        cmdoutput = subprocess.check_output(['cat /proc/cpuinfo | grep "cpu MHz"'], shell=True, text=True).split('\n')
        output = []
        for i in range(len(cmdoutput)):
            output.append(cmdoutput[i].split(' ')[-1])
        return output
    elif data == 'running_cores':
        cmdoutput = subprocess.check_output(['cat /proc/cpuinfo | grep "processor"'], shell=True, text=True).split('\n')[:-1]
        output = []
        for i in range(len(cmdoutput)):
            output.append(cmdoutput[i].split(' ')[-1])
        return output
    else:
        return 1


def set(data, value):  # all in MHz
    if edit == 1:
        if data == 'max_freq':
            os.system('cpupower frequency-set --max ' + str(value) + 'MHz')
        if data == 'min_freq':
            os.system('cpupower frequency-set --min ' + str(value) + 'MHz')
        if data == 'governor':
            os.system('cpupower frequency-set --governor ' + str(value))
        if data == 'current_freq':
            os.system('cpupower frequency-set --freq' + str(value) + 'MHz')
        if data == 'temp':
            if int(value) < 45:
                return 3
            elif int(value) > 100:
                return 3
            else:
                os.system('ryzenadj -f '+str(value))

        if data == 'tdp':  # give the tdp in mW
            if int(value) < 3500:# safety for not locking up the system
                return 3
            else:
                if int(value) > 25001:
                    os.system('ryzenadj --stapm-limit=' + str(value) + ' --fast-limit=' + str(value) + ' --slow-limit=' + str(value) + '-g 100000 -k 200000') # if you want some more power , will unlock the amp limit, BE CAREFULL
                else :
                    os.system('ryzenadj --stapm-limit=' + str(value) + ' --fast-limit=' + str(value) + ' --slow-limit=' + str(value))
        else:
            return 1
    else:
        return 2
