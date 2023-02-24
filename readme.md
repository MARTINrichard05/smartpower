# smartpower

## what is that ?
it is an python script that control the cpu power in a 'smart' way, depending on multiples parameters, it can change :\
 - OPTIONNAL(not usefull, draw more energy) number of enabled cores
 - max tdp
 - max temp
 - MAYBE , freeze background apps
 - MAYBE , smart scenario based of the current hour of the day (if you have 50 % 1 hr before finishing your day it will be more permissive than if you have 80 in the morning)

this way, you save power with the minimal performance impact, designed for ryzen on laptops, no plan to support gpu power features\
i am using it on my aura 15 gen 2 with a r7 5700u, working great

## Warning !
this project is in beta state , while it might work, it is not 100% bug-free certified
## support
 i d'ont guarantee you that i will help you but if there is any problem or question, just go to the issues section and ask for help, i will respond when i have time

## requirements
- a ryzen cpu(no plans to support intels cpu)
- linux\
- `cpupower` package (preinstalled on most distros)
- `ryzenadj` if you have a ryzen cpu on a laptop , you have to install it for having the best experience
## usage
use `SmartPowerCtrl.py` for command line, `SmartPowerCtrlTui.py` to use a Tui(first release), the daemon is started automatically
### install
just run install.sh as root and when the service is loaded hit ctrl+C (it will be stuck)
### update
just run update.sh as root and when the service is loaded hit ctrl+C (it will be stuck)
to update from version before beta 6 to beta 6 or upper you have to run `update_configs.py` too as root to keep your settings and put them into the new storage scheme

## documentation
i will write one when i have time and put comments in my code\
this is because in 3 weeks i'm gonna have my exams, after that i will be a bit more active

## license
you can use my code in your project, just mention me in the credits, thanks
## credits
- me
- stackoverflow
