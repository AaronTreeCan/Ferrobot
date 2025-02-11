import serial
import serial.tools.list_ports
import os
import threading
import time
import pages.viewport
import parse
import pages.debug_terminal
import camera
import PySimpleGUI as sg

PRINTER_CONNECTED = len(serial.tools.list_ports.comports()) > 0
SER = None

REALTIME_MODE = False
PRINTER_HEAD_POS = (0, 0, 0) # last position of printer head

sending_serial = False
global curr_index
curr_index = 0

def init():
    global SER

    if PRINTER_CONNECTED:  # Initialize the printer
        port = str(serial.tools.list_ports.comports()[0])
        port_name = port.split(' ', 1)[0]
        # print(str(serial.tools.list_ports.comports()[0]))
        print(port_name)

        SER = serial.Serial(port_name, 115200)
        SER.write(str.encode("M84 X Y Z S12000\r\n"))
        SER.write(str.encode("G90\r\n"))  # Use absolute positioning
        SER.write(str.encode("G21\r\n"))  # Use millimeters
        #SER.write(str.encode("G01 X0 Y0 F300 \r\n"))




def send_via_serial(curr_index):
    SER.write(str.encode("\r\n"))
    if curr_index == len(parse.INSTRUCTIONS):
        pages.debug_terminal.debug_log("No instructions to follow")
    else:
        for instr in parse.INSTRUCTIONS[curr_index:]: #store how many instructions we have passed so far and pick it up after executing capture commands
            curr_index += 1
            if instr.data["z"] == parse.Z_MOVE_HEIGHT:
                SER.write(str.encode(instr.stringify() + "\r\n"))
            elif instr.data["z"] == parse.Z_SKIP_HEIGHT:
                if curr_index >= 2:
                    prev_g01 = parse.INSTRUCTIONS[curr_index-2]
                    instr_x0 = prev_g01.data["x"]
                    instr_y0 = prev_g01.data["y"]
                    print([instr_x0, instr_y0])
                    instr0 = parse.InstructionG01(pos_x=instr_x0, pos_y=instr_y0, pos_z=parse.Z_SKIP_HEIGHT, f=int(parse.MOVE_SPEED))
                    SER.write(str.encode(instr0.stringify() + "\r\n"))
                    SER.write(str.encode(instr.stringify() + "\r\n"))
                
                    instr1 = parse.InstructionG01(pos_x=instr.data["x"], pos_y=instr.data["y"], pos_z=parse.Z_MOVE_HEIGHT, f=int(parse.MOVE_SPEED))
                    SER.write(str.encode(instr1.stringify() + "\r\n"))
                else:
                    instr0 = parse.InstructionG01(pos_x=0, pos_y=0, pos_z=parse.Z_SKIP_HEIGHT, f=int(parse.MOVE_SPEED))
                    SER.write(str.encode(instr0.stringify() + "\r\n"))
                    SER.write(str.encode(instr.stringify() + "\r\n"))
                
                    instr1 = parse.InstructionG01(pos_x=instr.data["x"], pos_y=instr.data["y"], pos_z=parse.Z_MOVE_HEIGHT, f=int(parse.MOVE_SPEED))
                    SER.write(str.encode(instr1.stringify() + "\r\n"))
            
            if not isinstance(instr, parse.InstructionG0) and not isinstance(instr, parse.InstructionG91):
                pages.debug_terminal.debug_log(instr.stringify())
            if isinstance(instr, parse.InstructionG01):
                global PRINTER_HEAD_POS
                
                PRINTER_HEAD_POS = (
                        instr.data["x"],
                        instr.data["y"],
                        instr.data["z"])
                
            if isinstance(instr, parse.InstructionG0) and pages.viewport.Toggle_Pull:
                PRINTER_HEAD_POS[2] += ( 
                    instr.data["z"]
                )
                pages.debug_terminal.syringe_log(instr.stringify())
            if isinstance(instr, parse.InstructionG0) and pages.viewport.Toggle_Push:
                PRINTER_HEAD_POS[2] -= ( 
                    instr.data["z"]
                )
                pages.debug_terminal.instr_x1syringe_log(instr.stringify())
            if curr_index == len(parse.INSTRUCTIONS) -1 : 
                sending_serial = False
    return curr_index

def cleanup_printer():
    if PRINTER_CONNECTED:  # If a printer is connected, disable the fans and the steppers.
        SER.write(str.encode("M107\r\n"))  # Fan Off
        SER.write(str.encode("M84 X Y Z S1\r\n"))  # Disable steppers

realtime_mode_checkbox = sg.Checkbox("Realtime Mode", default=False, enable_events=True, key="_realtime_mode_")

def  realtime_goto(coord, skip=False):
    x, y = coord
    global PRINTER_HEAD_POS
    prev_x, prev_y, prev_z = PRINTER_HEAD_POS
    print(parse.Z_MOVE_HEIGHT)
    if not skip:
        instructions = [parse.InstructionG01(
            pos_x=x,
            pos_y=y,
            pos_z=parse.Z_MOVE_HEIGHT,
            f=parse.MOVE_SPEED
        )]
    else:
        instructions = [
            parse.InstructionG01(
                pos_x=prev_x,
                pos_y=prev_y,
                pos_z=parse.Z_SKIP_HEIGHT,
                f=3000
            ),
            parse.InstructionG01(
                pos_x=x,
                pos_y=y,
                pos_z=parse.Z_SKIP_HEIGHT,
                f=parse.MOVE_SPEED
            ),
            parse.InstructionG01(
                pos_x=x,
                pos_y=y,
                pos_z=parse.Z_MOVE_HEIGHT,
                f=3000
            ),
        ]
    for instr in instructions:
        SER.write(str.encode(instr.stringify() + "\r\n"))
        pages.debug_terminal.debug_log("realtime mode goto: " + instr.stringify())
        if isinstance(instr, parse.InstructionG01):
            PRINTER_HEAD_POS = (
                instr.data["x"],
                instr.data["y"],
                instr.data["z"]
            )

