# smartpower
## Warning !
this project is in beta state , while it might work, it is not bug-free certified
## what is that ?
it is an python script that control the cpu power in a 'smart' way, depending on multiples parameters, it can change :\
 - OPTIONNAL(not usefull, draw more energy) number of enabled cores
 - max tdp
 - max temp
 - MAYBE , freeze background apps
 - MAYBE , smart scenario based of the current hour of the day (if you have 50 % 1 hr before finishing your day it will be more permissive than if you have 80 in the morning)

this way, you save power with the minimal performance impact, designed for ryzen on laptops, no plan to support gpu power features
## requirements
- a ryzen cpu

- linux\
- `cpupower` package (preinstalled on most distros)
- `ryzenadj` if you have a ryzen cpu on a laptop , you have to install it for having the best experience
## usage
### for now
1 : grab the latest from release folder\
2 : for a better "security" in the main class in bg.py you can change the authkey and do it too in tui\
3 : run bg.py as root (i will create a systemd service to do it at boot)\
3 : to control it or configure it, use tui.py, no need to have root access\
### in future
Maybe , i will create a script to automatically install it and create service
## documentation
i will write one when i have time and put comments in my code

## license
you can use my code in your project, just mention me in the credits, thanks
## credits
- me
- stackoverflow
