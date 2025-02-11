import PySimpleGUI as sg

import pages
import pages.code_output
import pages.debug_terminal
import pages.viewport
import parse
import printer

def velocityCalc(flowrate, area = 17.9450914):
    velocity = round(((float(flowrate))/area)*1.03, 3)
    return velocity

def distanceCalc(velocity):
    return round(velocity *1.04, 3)
