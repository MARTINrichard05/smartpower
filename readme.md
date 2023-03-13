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

## CURRENT STATE
until 22 march, i will be busy (exams) , after that i will start a big rewrite of my code , the current TUI kinda just works, bg.py is ... unreadable for any normal human (even me) ....\
when the rewrite will be finished, i will maybe change the name of the project(find something better), until that, i will check sometimes my github page but there will be no update/patches until that, sorrry
i saw that the ryzen-controller team moved to AATU (amd apu tuning utility), btw , it does not support linux(kinda sad) , this is why i will try to reimplement all their features (or most of) 
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
i will write one when i have time and put comments in my code

## license
you can use my code in your project, just mention me in the credits, thanks
## credits
- me
- stackoverflow
