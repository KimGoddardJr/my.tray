#!/usr/bin/env python3

import re
# from gi.repository import Gio
import configparser
import os
from glob import glob
from draw_items import menu_image

start_embassad = 'https://www.migrationsverket.se/ansokanbokning/valjtyp?4&enhet=U0145&sprak=sv&callback=https:/www.swedenabroad.se'

start_dogecoin = '/opt/dogecoin-1.14.3/bin/dogecoin-qt'

virt_audio = '/home/kg/Dropbox/DEVEL/argos-workgroup/opt/_launchers_HOME/virtual-audio.sh'

reload_pulse = '/home/kg/Dropbox/DEVEL/argos-workgroup/opt/_launchers_HOME/reload_pulse.sh'

cur_path = os.path.dirname(os.path.realpath(__file__))
argos_dir = "{}/../_launchers_HOME/desktop.files".format(cur_path)
glob_pattern = os.path.join(argos_dir, '*')
argos_files = sorted(glob(glob_pattern))

applications = {}
icons = {}

parser = configparser.ConfigParser()
parser.read(argos_files)


for section_name in parser.sections():
    category = parser.get(section_name, 'family')
    family = parser.get(section_name, 'family')

    if not applications.get(category):
        applications[category] = {}
    
    if not icons.get(category):
        icons[category] = ''

    if not applications[category].get(section_name):
        applications[category][section_name] = {}    

    for name, value in parser.items(section_name):
        applications[category][section_name][name] = value
        if name == 'categoryicon' or (name == 'icon' and icons[category] == ''):
            icons[category] = value

print(menu_image)
print("Custom Stuff")
print("--Open Svenska Embassad | href={}".format(start_embassad))

print("--Start Dogecoin | bash='{}' terminal=true".format(start_dogecoin))

print("--Restart Virtual Audio | bash='{}' terminal=true".format(virt_audio))

print("--Reload Pulse | bash='{}' terminal=true".format(reload_pulse))

for category, apps in sorted(applications.items()):
    #print(category)
    print("{} | useMarkup=false image={}".format(category, icons[category]))
    for name, app in sorted(apps.items()):
        #if app['alt'].lower() == 'true':
        print("--{} | useMarkup=false image={} bash='{}' terminal=true".format(name, app['icon'],app['launcher']))

    """
    ocio = ',ociounset' if app['ocio'].lower() == 'true' else ''

    print("--{} | useMarkup=false image={} bash='{}' param1='{}{}' param2='{}' terminal=false".format(name, app['icon'], app['launcher'], app['param1'], ocio, app['param2']))
    if app['alt'].lower() == 'true':
        print("--{} | useMarkup=false image={} bash='{}' param1='{}{}' param2='{}' alternate=true terminal=true ".format(name, app['icon'], app['launcher'], app['param1'], ocio, app['param2']))

    if app['ocio'].lower() == 'true':
        ocio = ',ocio'
        print("--{} ocio | useMarkup=false image={} bash='{}' param1='{}{}' param2='{}' terminal=false".format(name, app['icon'], app['launcher'], app['param1'], ocio, app['param2']))
        if app['alt'].lower() == 'true':
            print("--{} ocio | useMarkup=false image={} bash='{}' param1='{}{}' param2='{}' alternate=true terminal=true ".format(name, app['icon'], app['launcher'], app['param1'], ocio, app['param2']))
    """
