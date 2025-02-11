import PySimpleGUI as sg

import pages
import pages.code_output
import pages.debug_terminal
import pages.viewport
import parse
import printer
import camera

import cv2
from picamera2 import Picamera2
import threading
import datetime
import imutils
import numpy as np

# Initialize the camera
#camera = Picamera2()
#camera.start()

def make_editor_window():
    editor_menu_bar = sg.Column([
        [
            sg.Button('New'), 
            sg.Button('Open'), 
            sg.pin(sg.Button('Save', key="_save_button_")), 
            sg.Input(key='SaveFilePath', enable_events=True, visible=False), 
            sg.FileSaveAs(
                "Save as",
                key="_export_gcode_", 
                file_types=(("GCode Files", "*.gcode"),), 
                enable_events=True), 
            sg.Button('Send via Serial'),
            sg.Button('Autohome'),
            sg.Button('Import DXF')
        ],
    ])
    editor_most_left_col = sg.Column([[sg.Text("200", size=(3,35), key='_max_y_')], [sg.Text("0", size=(3, 1), key='_min_y_')], [sg.Text(' ', size=(3, 16), expand_y=False)]])

    editor_left_col = sg.Column([
        [pages.viewport.grid],
        [sg.Text("0", size=(67, 1), key='_min_x_'), sg.Text("200", size=(3, 2), key='_max_x_')],
        [pages.viewport.show_grid_checkbox, printer.realtime_mode_checkbox, 
         pages.viewport.larger_printer_checkbox, pages.viewport.lock_dxf_checkbox, 
         pages.viewport.toggle_zoom_checkbox],
        [pages.viewport.toggle_capture_checkbox],

        [
            sg.Text('X Coordinate:', size=(10, 1), expand_y=True), 
            sg.Text('Y Coordinate:', size=(10, 1), expand_y=True), 
            sg.Text('Z Move:', size=(10, 1), expand_y=True), 
            sg.Text('Z Skip:', size=(10, 1), expand_y=True), 
            sg.Text('Speed (mm/min):', size=(20, 1), expand_y=True)
        ],
        [
            sg.InputText(key='Xin', size=(10, 1), expand_y=True, enable_events=True, default_text='0'), 
            sg.InputText(key='Yin', size=(10, 1), expand_y=True, enable_events=True, default_text='0'), 
            sg.InputText(key='Zin', size=(10, 1), expand_y=True, enable_events=True, default_text='10'), 
            sg.InputText(key='ZSk', size=(10, 1), expand_y=True, enable_events=True, default_text='25'), 
            sg.InputText(key='Spd', size=(10, 1), expand_y=True, enable_events=True, default_text='20')
        ],
        [sg.Button('Add Move'), sg.Button("Add Skip"), sg.Button('Add Delay')],
        
        [
            sg.Text('X Offset:', size=(10, 1), expand_y=True), 
            sg.Text('Y Offset:', size=(10, 1), expand_y=True), 
            sg.Text('Z Offset:', size=(10, 1), expand_y=True), 
        ],
        [
            sg.InputText(key='Xoff', size=(10, 1), expand_y=True, enable_events=True, default_text='20'), 
            sg.InputText(key='Yoff', size=(10, 1), expand_y=True, enable_events=True, default_text='-20'), 
            sg.InputText(key='Zoff', size=(10, 1), expand_y=True, enable_events=True, default_text='0'), 
        ],
        [sg.Combo(['Pipette', 'Camera','Magnet'], key='element_offset',readonly=True,default_value='Magnet')],
        #[sg.Radio('Pipettor', group_id=1, default=True, key='_pipettor_mode_'), sg.Radio('Magnet stack', group_id=1, default=False, key='_magnet_mode_'), sg.Radio('Camera', group_id=1, default=False, key='_camera_mode_')]
        #[sg.Button("Set Offset"), (sg.Text("Offset: (0, 0, 0)", key="_offset_")), sg.Button("Set Camera Offset"), (sg.Text("Offset: (0, 0)", key="_camera_offset_"))]
    
    ])

    editor_right_col = sg.Column([
        [sg.Text("Code Table")],
        [pages.code_output.code_table_output],
        [pages.code_editor.code_editor_g01, pages.code_editor.code_editor_g04],
        [sg.Text("Debug Terminal")],
        [pages.debug_terminal.debug_terminal_output],
        [sg.Button("Clear All", key='_debug_term_clear_button_')],
        [sg.Text("Last edited 06/26/2024")]])

    editor_layout = [
        [editor_menu_bar],
        [editor_most_left_col, editor_left_col, editor_right_col],
    ]
    
    camera_left_col = sg.Column([[sg.Image(size=(720, 480), key='-IMAGE-')], [sg.Button('<< Previous'), sg.Button("Next >>")]])
    '''
    camera_left_col = sg.Column([
        [sg.Button('Open Camera', expand_y=True, key="_open_camera_")], 
        [sg.Image(size=(480, 480), key='-IMAGE-')]])
    '''
    #camera_left_col = sg.Column([[sg.Button('Open Camera')], [sg.Button('Show preview')]]),
    
    camera_right_col = sg.Column([

        [sg.Text('Exposure(s)', size=(20, 1), expand_x=True, expand_y=True)],        
        [sg.InputText(key='Expo_Length', size=(20, 1), expand_x=True, expand_y=True, enable_events=True, default_text='0.05')], 
        [sg.Button('Change Exposure', key = 'Adjust Exposure')],
        
        [sg.Text('Z height', size=(20, 1), expand_x=True, expand_y=True)],        
        [sg.InputText(key='Z_height', size=(20, 1), expand_x=True, expand_y=True, enable_events=True, default_text='25')], 
        [sg.Button('Change Z height', key = 'Adjust Z height')],

        [sg.Text('X resolution', size=(10, 1), expand_x=True, expand_y=True), sg.Text('Y resolution', size=(10, 1), expand_x=True, expand_y=True)],        
        [sg.InputText(key='X_res', size=(10, 1), expand_x=True, expand_y=True, enable_events=True, default_text='1080'), sg.InputText(key='Y_res', size=(10, 1), expand_x=True, expand_y=True, enable_events=True, default_text='720')], 
        [sg.Button('Change resolution', key = 'Adjust res')],

        [sg.Text('Number of Images', size=(20, 1), expand_x=True, expand_y=True)], 
        [sg.InputText(key='Number_of_Images', size=(20, 1), expand_x=True, expand_y=True, enable_events=True, default_text='1')], 
        [sg.Text('Period Between Capture(s)', size=(25, 1), expand_x=True, expand_y=True)],
        [sg.InputText(key='Period_Between_Capture', size=(20, 1), expand_x=True, expand_y=True, enable_events=True, default_text='1')], 
        
        [sg.Button('Auto Focus', key ='Adjust Focus')],
        [sg.Button('Take Image', key = 'Take Image')],
        [sg.Image(key='camera_feed')]
    ])
    
    camera_layout = [[camera_left_col, camera_right_col]]



    syringeSelection = sg.Column([
    [sg.Text('Select an syringe:')],
    [sg.Combo(['1mL', '0.5mL','N/A'], key='-SYRINGE-',readonly=True,default_value='N/A')],
    [sg.Button('Submit via Serial'),sg.Input(key='SaveSyringePath', enable_events=True, visible=False),
    sg.FileSaveAs("Save as",key="_export_gcode_", file_types=(("GCode Files", "*.gcode"),), enable_events=True) , sg.Button('Clear')]
    ])
    ParamSetup = sg.Column([[sg.Text('Volumn(uL):'),sg.InputText(key='-VOLUMN-', size=(20,1),expand_x=True, expand_y=True, enable_events=True, default_text = '0')],
                         [sg.Text('Flow Rate(uL/min):'),sg.InputText(key='-FLOWRATE-',size=(20,1),expand_x=True, expand_y=True, enable_events=True, default_text = '0')]])
    
    PushPull = sg.Column([[pages.viewport.toggle_pullpush_checkbox]])
    
    Record = sg.Column([[pages.debug_terminal.syringe_terminal_output]])


    syringeLayout = [[syringeSelection, ParamSetup, PushPull],[Record]]


    layout = [sg.TabGroup([[
        sg.Tab('Editor', editor_layout),
        sg.Tab('Camera', camera_layout),
        sg.Tab('GCode Output', [[pages.code_output.code_string_output]]),
        sg.Tab('Syringe Setup', syringeLayout)
    ]])],
    return sg.Window("filename", layout, size=(1200, 1000), finalize=True, resizable=False)

window = None
code_editor_selected_row = 0

FILE_SAVED = False
FILE_NAME = ""

def show_offset_window(title):
    pop_window = sg.Window(title, [
        [sg.Text("Enter the X, Y, and Z offsets")],
        [
            sg.Text('X Offset:', size=(10, 1), expand_y=True),
            sg.Text('Y Offset:', size=(10, 1), expand_y=True),
            sg.Text('Z Offset:', size=(10, 1), expand_y=True)
        ],
        [
            sg.InputText(key='XOff', size=(10, 1), expand_y=True, enable_events=True, default_text='0'), 
            sg.InputText(key='YOff', size=(10, 1), expand_y=True, enable_events=True, default_text='0'), 
            sg.InputText(key='ZOff', size=(10, 1), expand_y=True, enable_events=True, default_text='0')
        ],
        [sg.OK(), sg.Cancel()]
    ])
    do_loop = True

    while do_loop:

        event, values = pop_window.read()


        if event == sg.WIN_CLOSED:    # if user closes window or clicks cancel
            return
        elif event == 'XOff':  # If the user manually enters a value into the X input
            handle_coord_input(values["XOff"], "XOff", win=pop_window)
        elif event == 'YOff':  # If the user manually enters a value into the X input
            handle_coord_input(values["YOff"], "YOff", win=pop_window)
        elif event == 'ZOff':  # If the user manually enters a value into the X input
            handle_coord_input(values["ZOff"], "ZOff", win=pop_window)

        elif event == '-FLOWRATE-':
            handle_coord_input(values["-FLOWRATE-"], "-FLOWRATE-")

        elif event == '-VOLUMN-':
            handle_coord_input(values["-VOLUMN-"], "-VOLUMN-")

        elif event == 'Cancel':
            do_loop = False
            pop_window.close()
            return (0, 0, 0)

        elif event == 'OK':
            if values['XOff'] == '' or values['YOff'] == '' or values['ZOff'] == '':
                pages.debug_terminal.debug_log(
                    "Error! One or more of the offset coordinates are empty!")
                do_loop = False
                pop_window.close()
                return (0, 0, 0)

            if (parse.is_valid_coordinate(values['XOff']) and
                parse.is_valid_coordinate(values['YOff']) and
                parse.is_valid_coordinate(values['ZOff'])):
                x_offset = float(values['XOff'])
                y_offset = float(values['YOff'])
                z_offset = float(values['ZOff'])
                pages.debug_terminal.debug_log("Set offsets to X= " + str(x_offset) +
                          " Y = " + str(y_offset) + " Z = " + str(z_offset))
                do_loop = False
                pop_window.close()
                # Disable Loop and PopWindow, THEN return!
                return (float(values['XOff']), float(
                    values['YOff']), float(values['ZOff']))

            pages.debug_terminal.debug_log(
                "Error! The X-, Y-, or Z Offset Coordinate is not a numeric value!")
            do_loop = False
            pop_window.close()
            return (0, 0, 0)

def x_grid_lables(f_printer):
    min_x_coord = parse.OFFSET_X - parse.CAMERA_X
    if f_printer:
        max_x_coord = 100-min_x_coord
    else:
        max_x_coord = 200-min_x_coord

    return [min_x_coord, max_x_coord]

def y_grid_lables(f_printer):
    min_y_coord = parse.OFFSET_Y - parse.CAMERA_Y
    if f_printer:
        max_y_coord = 100-min_y_coord
    else:
        max_y_coord = 200-min_y_coord

    return [min_y_coord, max_y_coord]

def show_camera_offset_window(title):
    pop_window = sg.Window(title, [
        [sg.Text("Enter the X, Y camera offsets")],
        [
            sg.Text('Camera X:', size=(10, 1), expand_y=True),
            sg.Text('Camera Y:', size=(10, 1), expand_y=True),
        ],
        [
            sg.InputText(key='camera_XOff', size=(10, 1), expand_y=True, enable_events=True, default_text='0'), 
            sg.InputText(key='camera_YOff', size=(10, 1), expand_y=True, enable_events=True, default_text='0'), 
        ],
        [sg.OK(), sg.Cancel()]
    ])
    do_loop = True

    while do_loop:

        event, values = pop_window.read()


        if event == sg.WIN_CLOSED:    # if user closes window or clicks cancel
            return
        elif event == 'camera_XOff':  # If the user manually enters a value into the X input
            handle_coord_input(values["camera_XOff"], "camera_XOff", win=pop_window)
        elif event == 'camera_YOff':  # If the user manually enters a value into the X input
            handle_coord_input(values["camera_YOff"], "camera_YOff", win=pop_window)

        elif event == 'Cancel':
            do_loop = False
            pop_window.close()
            return (0, 0)

        elif event == 'OK':
            if values['camera_XOff'] == '' or values['camera_YOff'] == '':
                pages.debug_terminal.debug_log(
                    "Error! One or more of the offset coordinates are empty!")
                do_loop = False
                pop_window.close()
                return (0, 0)

            if (parse.is_valid_coordinate(values['camera_XOff']) and
                parse.is_valid_coordinate(values['camera_YOff'])):
                x_offset = float(values['camera_XOff'])
                y_offset = float(values['camera_YOff'])
                pages.debug_terminal.debug_log("Set camera offsets to X= " + str(x_offset) + " Y = " + str(y_offset))
                do_loop = False
                pop_window.close()
                # Disable Loop and PopWindow, THEN return!
                return (float(values['camera_XOff']), float(
                    values['camera_YOff']))

            pages.debug_terminal.debug_log(
                "Error! The X- or Y Offset Coordinate is not a numeric value!")
            do_loop = False
            pop_window.close()
            return (0, 0)

# Create the Window25
def init(filename):
    global window
    max_coord = 100
    window = make_editor_window()
    #window.finalize()
    set_file_name(filename)
    set_file_saved(True)
    printer.init()

    if not parse.file_open(filename):
        sg.popup_error("ERROR in parsing Gcode file! See log for details.")

    pages.viewport.init()
    set_file_saved(True)
    pages.code_output.render_code_output()
    pages.viewport.render_grid()

def set_code_editor_liveness(is_up_to_date):
    global window
    window["_code_editor_submit_button_"].update(visible=not is_up_to_date)
    window["_code_editor_submit_button2_"].update(visible=not is_up_to_date)

def handle_code_output_click(event, values):
    global code_editor_selected_row
    set_code_editor_liveness(True)
    if len(values[event]) > 0:
        row = values[event][0]
        if not row is None and row >= 0:
            code_editor_selected_row = row
            instr = parse.INSTRUCTIONS[row]
            if isinstance(instr, parse.InstructionG01):
                pages.viewport.render_vertices()
                pages.viewport.render_vertex(instr.data["x"], instr.data["y"], emphasized=True)
                window["_code_editor_g01_"].update(visible=True)
                window["_code_editor_g04_"].update(visible=False)

                window["_code_editor_g01_x_"].update(instr.data["x"])
                window["_code_editor_g01_y_"].update(instr.data["y"])
                window["_code_editor_g01_z_"].update(instr.data["z"])
                window["_code_editor_g01_f_"].update(instr.data["f"])
            if isinstance(instr, parse.InstructionG04):
                pages.viewport.render_vertices()
                x, y = parse.instructions_get_prev_g01_from_index(row)
                pages.viewport.render_wait_vertex(x, y, emphasized=True)
                window["_code_editor_g01_"].update(visible=False)
                window["_code_editor_g04_"].update(visible=True)

                window["_code_editor_g04_p_"].update(instr.data["p"])

def handle_code_editor_change_g01():
    set_code_editor_liveness(False)

def handle_code_editor_change_g04():
    set_code_editor_liveness(False)

def handle_code_editor_submit():
    global window
    instr = parse.INSTRUCTIONS[code_editor_selected_row]
    if isinstance(instr, parse.InstructionG01):
        window["_code_editor_g01_"].update(visible=True)
        window["_code_editor_g04_"].update(visible=False)

        try:
            instr.data["x"] = float(window["_code_editor_g01_x_"].get())
            instr.data["y"] = float(window["_code_editor_g01_y_"].get())
            instr.data["z"] = float(window["_code_editor_g01_z_"].get())
            instr.data["f"] = float(window["_code_editor_g01_f_"].get())
            pages.debug_terminal.debug_log(f'Changed vertex to ({instr.data["x"]}, {instr.data["y"]})')
        except:
            pages.debug_terminal.debug_log("incorrect coordinates")

    if isinstance(instr, parse.InstructionG04):
        window["_code_editor_g01_"].update(visible=False)
        window["_code_editor_g04_"].update(visible=True)

        try:
            instr.data["p"] = int(window["_code_editor_g04_p_"].get())
            pages.debug_terminal.debug_log(f'Changed wait to ({instr.data["p"]})')
        except:
            pages.debug_terminal.debug_log("incorrect coordinates")


    set_code_editor_liveness(True)
    pages.viewport.oprender_grid()
    pages.code_output.render_code_output()

def handle_code_editor_delete():
    if code_editor_selected_row < len(parse.INSTRUCTIONS):
        parse.INSTRUCTIONS.pop(code_editor_selected_row)
        pages.debug_terminal.debug_log(f'Deleted instruction.')
        set_code_editor_liveness(True)
        pages.viewport.render_grid()
        pages.code_output.render_code_output()

def handle_code_editor_delete_dxf():
    pages.viewport.DXF_OBJS = [] # clear all DXF OBJS
    pages.viewport.render_grid() # rerender the grid to update
    return # try this - chai
    global code_editor_selected_row
    if code_editor_selected_row < len(pages.viewport.DXF_OBJS):
        dxf_to_delete = pages.viewport.DXF_OBJS[code_editor_selected_row]
        dxf_to_delete.delete()
        pages.debug_terminal.debug_log(f'Deleted DXF object')
        pages.viewport.render_grid()
        pages.code_output.render_code_output()
        set_code_editor_liveness(True)

def handle_coord_input(coord, coordKey, maxVal=1000, win=None):
    global window
    if (win is None):
        win = window
    if not coord == '':  # Is the text box not empty?
        if coord[-1].isnumeric():  # Is the last digit entered numeric?
            if coord.isnumeric():
                # Is the number greater than Max? (Size of the printer bed)
                if float(coord) > maxVal:
                    # If so, cap the value.
                    win[coordKey].update(value=str(maxVal))
        else:  # If the last digit entered is not numeric
            if coord[-1] == '.' or not coord:
                # If the last digit is a decimal point, or if the box is
                # empty, do nothing.
                pass
            else:  # Otherwise, remove the last digit entered.
                win[coordKey].update(value=coord[:-1])


# def handle_flowrate_input(coord, coordKey, maxVal=100, win=None):
#     global window
#     if (win is None):
#         win = window
#     if not coord == '':  # Is the text box not empty?
#         if coord[-1].isnumeric():  # Is the last digit entered numeric?
#             if coord.isnumeric():
#                 # Is the number greater than 100? (Size of the printer bed)
#                 if float(coord) > maxVal:
#                     # If so, cap the value at 100.
#                     win[coordKey].update(value=str(maxVal))
#         else:  # If the last digit entered is not numeric
#             if coord[-1] == '.' or not coord:
#                 # If the last digit is a decimal point, or if the box is
#                 # empty, do nothing.
#                 pass
#             else:  # Otherwise, remove the last digit entered.
#                 win[coordKey].update(value=coord[:-1])

# def handle_volumn_input(coord, coordKey, maxVal=100, win=None):
#     global window
#     if (win is None):
#         win = window
#     if not coord == '':  # Is the text box not empty?
#         if coord[-1].isnumeric():  # Is the last digit entered numeric?
#             if coord.isnumeric():
#                 # Is the number greater than 100? (Size of the printer bed)
#                 if float(coord) > maxVal:
#                     # If so, cap the value at 100.
#                     win[coordKey].update(value=str(maxVal))
#         else:  # If the last digit entered is not numeric
#             if coord[-1] == '.' or not coord:
#                 # If the last digit is a decimal point, or if the box is
#                 # empty, do nothing.
#                 pass
#             else:  # Otherwise, remove the last digit entered.
#                 win[coordKey].update(value=coord[:-1])


def handle_show_grid_toggle():
    pages.viewport.SHOW_GRID = not pages.viewport.SHOW_GRID
    pages.viewport.render_grid()

def handle_realtime_toggle():
    global window
    printer.REALTIME_MODE = not printer.REALTIME_MODE
    window["_realtime_mode_"].update()

def handle_lock_dxf_toggle():
    global window
    pages.viewport.LOCK_DXFS = not pages.viewport.LOCK_DXFS
    window["_lock_dxf_"].update()
    pages.viewport.render_grid()
    
def handle_entire_view_toggle():
    global window
    #max_coord = 100
    pages.viewport.l_printer = not pages.viewport.l_printer
    
    if pages.viewport.l_printer:
        pages.viewport.max_coordx = 200
        pages.viewport.max_coordy = 200
        pages.viewport.grid.erase()
        window['Path'].change_coordinates((0,0), (pages.viewport.max_coordx, pages.viewport.max_coordy))
        window["_min_x_"].update(value=str(0))
        window["_min_y_"].update(value=str(0))
        window["_max_x_"].update(value=str(int(pages.viewport.max_coordx)))
        window["_max_y_"].update(value=str(int(pages.viewport.max_coordy)))
        
    else:
        pages.viewport.max_coordx = 200 + parse.CAMERA_X
        pages.viewport.max_coordy = 200 + parse.CAMERA_Y
        pages.viewport.grid.erase()
        window['Path'].change_coordinates((int(parse.OFFSET_X),int(parse.OFFSET_Y)), (pages.viewport.max_coordx, pages.viewport.max_coordy))
        window["_min_x_"].update(value=str(int(parse.OFFSET_X)))
        window["_min_y_"].update(value=str(int(parse.OFFSET_Y)))
        window["_max_x_"].update(value=str(int(pages.viewport.max_coordx)))
        window["_max_y_"].update(value=str(int(pages.viewport.max_coordy)))
    
    
    
    pages.viewport.render_grid()
    
    
    #pages.viewport.render_grid()

def handle_set_offsets():
    global window
    # No clue why this workaround is needed. I can't seem to change the
    # Offsets in the function itself. I need to use return().
    result = show_offset_window("Select Offsets")
    if result is None:
        return
    parse.set_offset(result)
    window["_offset_"].update(value=f"Offset: ({result[0]}, {result[1]}, {result[2]})")
    pages.code_output.render_code_output()
    pages.viewport.render_grid()

def handle_set_camera_offsets():
    global window
    # No clue why this workaround is needed. I can't seem to change the
    # Offsets in the function itself. I need to use return().
    result = show_camera_offset_window("Select Camera Offsets")
    if result is None:
        return
    parse.set_camera_offset(result)
    window["_camera_offset_"].update(value=f"Offset: ({result[0]}, {result[1]})")
    pages.code_output.render_code_output()
    pages.viewport.render_grid()

def handle_capture_toggle():
    global window
    pages.viewport.Toggle_Capture = not pages.viewport.Toggle_Capture
    pages.viewport.render_grid()

def clean_file_name(filename):
    f1 = filename.split("/")[-1]
    f2 = filename.split("\\")[-1]
    if len(f1) < len(f2):
        return f1
    else:
        return f2
def update_save_button():
    global window
    if window.is_closed():
        return

    if FILE_NAME == "Untitled":
        window["_save_button_"].update(visible=False)
    else:
        window["_save_button_"].update(visible=True)

def set_file_saved(is_file_saved):
    global window
    global FILE_SAVED
    global FILE_NAME
    FILE_SAVED = is_file_saved
    update_save_button()

    if window.is_closed():
        return

    if FILE_SAVED:
        window.set_title(clean_file_name(FILE_NAME))
    else:
        window.set_title(clean_file_name(FILE_NAME) + " [unsaved]")

def set_file_name(window_name):
    global window
    global FILE_NAME
    FILE_NAME = window_name
    update_save_button()

    if window.is_closed():
        return

    if FILE_SAVED:
        window.set_title(clean_file_name(FILE_NAME))
    else:
        window.set_title(clean_file_name(FILE_NAME) + " [unsaved]")

def handle_debug_term_clear():
    pages.debug_terminal.debug_clear()

def allow_zoom():
    global window
    pages.viewport.Toggle_Zoom = not pages.viewport.Toggle_Zoom


def zoom_in(x, y, step=20):
    pages.viewport.grid.erase()

    if pages.viewport.max_coordx - step > 40:
        pages.viewport.max_coordx -= step
    if pages.viewport.max_coordy - step > 40:
        pages.viewport.max_coordy -= step

    if pages.viewport.max_coordx - step < 40:
        pages.viewport.max_coordx = 40
    if pages.viewport.max_coordy - step < 40:
        pages.viewport.max_coordy = 40
    
    half_coordx = pages.viewport.max_coordx // 2
    half_coordy = pages.viewport.max_coordy // 2
    new_x0 = max(0, x - half_coordx)
    new_y0 = max(0, y - half_coordy)
    new_x1 = new_x0 + pages.viewport.max_coordx
    new_y1 = new_y0 + pages.viewport.max_coordy

    # Ensure new_x1 and new_y1 do not exceed the grid limits
    if new_x1 > 200:
        new_x1 = 200
        new_x0 = new_x1 - pages.viewport.max_coordx
    if new_y1 > 200:
        new_y1 = 200
        new_y0 = new_y1 - pages.viewport.max_coordy

    window["_min_x_"].update(value=str(int(new_x0)))
    window["_min_y_"].update(value=str(int(new_y0)))
    window["_max_x_"].update(value=str(int(new_x1)))
    window["_max_y_"].update(value=str(int(new_y1)))
    
    window['Path'].change_coordinates((new_x0, new_y0), (new_x1, new_y1))
    pages.viewport.render_grid()


def zoom_out(x, y, step=20):
    pages.viewport.grid.erase()

    step = int(step)
    
    if pages.viewport.max_coordx + step < 200:
        pages.viewport.max_coordx += step
    if pages.viewport.max_coordy + step < 200:
        pages.viewport.max_coordy += step
    if pages.viewport.max_coordx + step >= 200:
        pages.viewport.max_coordx = 200
    if pages.viewport.max_coordy + step >= 200:
        pages.viewport.max_coordy = 200
    
    half_coordx = pages.viewport.max_coordx // 2
    half_coordy = pages.viewport.max_coordy // 2
    new_x0 = max(0, x - half_coordx)
    new_y0 = max(0, y - half_coordy)
    new_x1 = new_x0 + pages.viewport.max_coordx
    new_y1 = new_y0 + pages.viewport.max_coordy

    # Ensure new_x1 and new_y1 do not exceed the grid limits
    if new_x1 > 200:
        new_x1 = 200
        new_x0 = new_x1 - pages.viewport.max_coordx
    if new_y1 > 200:
        new_y1 = 200
        new_y0 = new_y1 - pages.viewport.max_coordy

    window["_min_x_"].update(value=str(int(new_x0)))
    window["_min_y_"].update(value=str(int(new_y0)))
    window["_max_x_"].update(value=str(int(new_x1)))
    window["_max_y_"].update(value=str(int(new_y1)))

    window['Path'].change_coordinates((new_x0, new_y0), (new_x1, new_y1))
    pages.viewport.render_grid()


#Above is the addition/subtraction version below is the multiplication/division version (both are broken when trying to zoom 
# at the upper or righter edges of the grid. In particular, theres an issue with regards to rendering the new grid)

'''
def zoom_in(x, y, zoom_factor=1.2):
    pages.viewport.grid.erase()
    new_x0 = int(x - int(x / zoom_factor))
    new_y0 = int(y - int(y / zoom_factor))
    
    if pages.viewport.max_coord / zoom_factor > 40:
        pages.viewport.max_coord = int(pages.viewport.max_coord / zoom_factor)
    else:
        pages.viewport.max_coord = 40
    
    new_x1 = new_x0 + pages.viewport.max_coord
    new_y1 = new_y0 + pages.viewport.max_coord
    if new_x1 < 40:
        new_x1 = 40
        new_x0 = new_x1 - pages.viewport.max_coord
    if new_y1 < 40:
        new_y1 = 40
        new_y0 = new_y1 - pages.viewport.max_coord

    window['Path'].change_coordinates((new_x0, new_y0), (new_x1, new_y1))
    pages.viewport.render_grid()

def zoom_out(x, y, zoom_factor=1.2):
    pages.viewport.grid.erase()
    new_x0 = int(x - int(x * zoom_factor))
    new_y0 = int(y - int(y * zoom_factor))
    
    if pages.viewport.max_coord * zoom_factor < 200:
        pages.viewport.max_coord = int(pages.viewport.max_coord * zoom_factor)
    else:
        pages.viewport.max_coord = 200
        window['Path'].change_coordinates((0, 0), (pages.viewport.max_coord,pages.viewport.max_coord))
        pages.viewport.render_grid()

    
    new_x1 = new_x0 + pages.viewport.max_coord
    new_y1 = new_y0 + pages.viewport.max_coord
    if new_x1 > 200:
        new_x1 = 200
        new_x0 = new_x1 - pages.viewport.max_coord
        if new_x0 < 0:
            new_x0 = 0
    if new_y1 > 200:
        new_y1 = 200
        new_y0 = new_y1 - pages.viewport.max_coord
        if new_y0 < 0:
            new_y0 = 0
    
    window['Path'].change_coordinates((new_x0, new_y0), (new_x1, new_y1))
    pages.viewport.render_grid()
'''

