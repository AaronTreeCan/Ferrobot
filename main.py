# When skipping, use 3000 speed X-axis only?

# Function to delete last input

# G04 (Pause GCode) #Fifth vector in toolpath that states gcode number
# (g01 or g04 being run)


# Multithreading/Multicoring?? GeeksforGeeks Tutorial

# Package libraries into program (python runtime, code, libraries)

import time
import PySimpleGUI as sg
import numpy
import pages.code_editor
import pages.viewport
import welcome_page
import editor_page
import printer
import camera
import pages
import parse
import syringe
import threading
import tkinter as tki
import os


edit = False
global camera_open
camera_open = False
start = True
thread0 = None
thread1 = None
thread2 = None
thread3 = None

curr_flowrate = ''
curr_volumn = ''
# Add threading events
camera.stopevent_flag = threading.Event()
camera.capture_flag = threading.Event()

# Everything up to this point imports libraries, and defines constants and
# variables
DISPLAY_CAMERA_IMAGE = None

# If either a camera or a printer is connected, wait 3 seconds. This
# allows the device to initialize.
if camera.CAMERA_CONNECTED or printer.PRINTER_CONNECTED:
    time.sleep(3)

save_directory = "/home/ferro/Desktop/ferro-7-19/captures" # this is for saving captures using pi camera

# Function to generate the next numbered file name
def get_next_file_name(directory, base_name="capture", extension="jpg"):
    files = os.listdir(directory)
    existing_numbers = [
        int(f.split('_')[1].split('.')[0]) for f in files
        if f.startswith(base_name) and f.endswith(f".{extension}")
    ]
    next_number = max(existing_numbers) + 1 if existing_numbers else 1
    return f"{base_name}_{next_number}.{extension}"

# sg.Input(key='LoadFilePath'), sg.FileBrowse(file_types=(("GCode Files", "*.gcode"),)),
file_name = get_next_file_name(save_directory)
file_path = os.path.join(save_directory, file_name)
# Ensure the save directory exists
os.makedirs(save_directory, exist_ok=True)
# Event Loop to process "Fevents" and get the "values" of the inputs

global add_ind, all_images, cur_ind, cur_move_ind
add_ind = 0
cur_ind = 0
cur_move_ind = 0
all_images = []

while True:
    event, values = editor_page.window.read()  # Get the PYSimpleGUI event.
    
    '''
    expo_time = 0.05

    thread0 = threading.Thread(target=camera.take_image, args=(file_path,), daemon=True) 

    thread1 = threading.Thread(target=camera.show_preview, daemon=True)

    thread2 = threading.Thread(target=camera.adjust_focus, daemon=True)

    thread3 = threading.Thread(target=camera.adjust_exposure2, args=(expo_time,), daemon=True)
    if start == False:
        thread1.start()

        thread2.start()
        thread2.join() 
        print('Auto Adjusted Focus')
        thread3.start()
        thread3.join() 
        print('Adjusted Exposure')
        start = False
    '''
    if values['element_offset'] == 'None':
        parse.MODE = 'N'
    elif values['element_offset'] == 'Magnet':
        parse.MODE = 'M'
    elif values['element_offset'] == 'Camera':
        parse.MODE = 'C'
    elif values['element_offset'] == 'Pipette':
        parse.MODE = 'P'
    
    if event == sg.WIN_CLOSED:    # if user closes window or clicks cancel
        if not editor_page.FILE_SAVED and editor_page.FILE_NAME != "Untitled":
            ans = sg.popup_yes_no("This file is unsaved! Do you wish to SAVE (YES!)?")
            if ans == "Yes":
                if parse.file_save_as(editor_page.FILE_NAME):
                    editor_page.set_file_saved(True)
                    break
        break

    if (event == '_code_editor_g01_x_' or
        event == '_code_editor_g01_y_' or
        event == '_code_editor_g01_z_' or
        event == '_code_editor_g01_f_'):
        editor_page.handle_coord_input(values["_code_editor_g01_x_"], "_code_editor_g01_x_")
        editor_page.handle_coord_input(values["_code_editor_g01_y_"], "_code_editor_g01_y_")
        editor_page.handle_coord_input(values["_code_editor_g01_z_"], "_code_editor_g01_z_")
        editor_page.handle_coord_input(values["_code_editor_g01_f_"], "_code_editor_g01_f_", maxVal=1000)
        editor_page.handle_code_editor_change_g01()
    elif (event == '_code_editor_g04_p_'):
        editor_page.handle_coord_input(values["_code_editor_g04_p_"], "_code_editor_g04_p_", maxVal=60000)
        editor_page.handle_code_editor_change_g04()
    elif (event == '_code_editor_submit_button_' or
          event == '_code_editor_submit_button2_'):
        editor_page.handle_code_editor_submit()
        editor_page.set_file_saved(False)
    elif (event == '_code_editor_delete_button_' or
          event == '_code_editor_delete_button2_'):
        editor_page.handle_code_editor_delete()
        editor_page.set_file_saved(False)
    elif (event == '_code_editor_delete_dxf_button_'):
        editor_page.handle_code_editor_delete_dxf()
        editor_page.set_file_saved(False)

    elif event == "_code_table_output_":
        editor_page.handle_code_output_click(event, values)
        editor_page.set_file_saved(False)

    elif event == 'Path':  # If the user left clicks on the grid
        x, y = values[event]
        if not pages.viewport.dragmode:
            if not pages.viewport.mouse_down:
                pages.viewport.mouse_down = True
                z = 10

                # check if user is intending to drag a vertex or a DXF obj
                is_anything_near, i = parse.anything_near_click((x,y))
                is_anything_near_2, j = pages.viewport.anything_near_click((x,y))

                if pages.viewport.Toggle_Zoom:
                    editor_page.zoom_in(x,y)
                    if pages.viewport.Toggle_Capture and parse.coord_set != None:
                        this_coord_num = 0
                        for this_coord_num in range(len(parse.coord_set)):  
                            this_coord = parse.coord_set[this_coord_num]
                            if cur_ind == 0 and add_ind == 0:
                                pages.viewport.render_capture(this_coord[0], this_coord[1])
                            else: 
                                if this_coord_num <= cur_ind:
                                    pages.viewport.render_old_capture(this_coord[0], this_coord[1])
                                else:
                                    pages.viewport.render_capture(this_coord[0], this_coord[1])
                    if pages.viewport.Toggle_Capture and parse.wrong_coord_set != None:
                        for wrong_coord in parse.wrong_coord_set:
                            pages.viewport.render_wrong_capture(wrong_coord[0], wrong_coord[1])
                    continue

                if pages.viewport.Toggle_Capture:
                    global camera_coords
                    camera_coords = parse.add_capture((x,y))
                    editor_page.set_file_saved(False)
                    continue

                elif is_anything_near:
                    # enter drag mode
                    pages.viewport.dragmode = True
                    fake_event = "e"
                    fake_values = {
                        fake_event: [i]
                    }
                    editor_page.handle_code_output_click(fake_event, fake_values)
                    editor_page.set_file_saved(False)
                    pages.viewport.dragmode_instr_idx = i
                    continue
                elif is_anything_near_2 and not pages.viewport.LOCK_DXFS:
                    # enter drag mode
                    pages.viewport.dragmode = True
                    pages.viewport.dragmode_dxf_idx = j
                    pages.viewport.dragmode_dxf_offset = pages.viewport.DXF_OBJS[j].get_offset((x, y))

                    continue

                # not clicking a vertex nor DXF obj, so add a new vertex
                else:
                    parse.add_travel((x, y))
                    pages.debug_terminal.debug_log(f'Added move at ({x}, {y}, {z})')
                    editor_page.set_file_saved(False)                   
                if printer.REALTIME_MODE:
                    printer.realtime_goto((x, y))
                    cur_move_ind += 1
                    
        else:
            # is drag mode
            if pages.viewport.dragmode_instr_idx is not None:
                parse.move_g01(pages.viewport.dragmode_instr_idx, (x, y))
                pages.viewport.render_grid()
            if pages.viewport.dragmode_dxf_idx is not None:
                pages.viewport.DXF_OBJS[pages.viewport.dragmode_dxf_idx].move((x, y), pages.viewport.dragmode_dxf_offset)
                pages.viewport.render_grid()
    elif event == 'Path+UP':  # If the user left clicks on the grid
        pages.viewport.dragmode = False
        pages.viewport.dragmode_instr_idx = None
        pages.viewport.dragmode_dxf_idx = None
        pages.viewport.mouse_down= False

    elif event == 'PathRightClick':  # If the user right clicks on the grid
        z = 25
        x, y = values['Path']
        is_anything_near, i = parse.anything_near_click((x, y))
        is_anything_near_2, j = pages.viewport.anything_near_click((x, y))
        if pages.viewport.Toggle_Zoom:
            editor_page.zoom_out(x,y)
            if pages.viewport.Toggle_Capture and parse.coord_set != None:
                this_coord_num = 0
                for this_coord_num in range(len(parse.coord_set)):  
                    this_coord = parse.coord_set[this_coord_num]
                    if cur_ind == 0 and add_ind == 0:
                        pages.viewport.render_capture(this_coord[0], this_coord[1])
                    else: 
                        if this_coord_num <= cur_ind:
                            pages.viewport.render_old_capture(this_coord[0], this_coord[1])
                        else:
                            pages.viewport.render_capture(this_coord[0], this_coord[1])
            if pages.viewport.Toggle_Capture and parse.wrong_coord_set != None:
                for wrong_coord in parse.wrong_coord_set:
                    pages.viewport.render_wrong_capture(wrong_coord[0], wrong_coord[1])

            continue
        
        if pages.viewport.Toggle_Capture:
            continue

        elif is_anything_near_2 and pages.viewport.LOCK_DXFS:
            parse.add_skip((x, y))
            pages.debug_terminal.debug_log(f'Added skip at ({x}, {y}, {z})')
            editor_page.set_file_saved(False)           
            if printer.REALTIME_MODE:
                printer.realtime_goto((x, y), skip=True)
                cur_move_ind += 1
        
        # Only add skip point if not clicking on a vertex or unlocked DXF obj
        elif not is_anything_near_2 and not pages.viewport.LOCK_DXFS:
            parse.add_skip((x, y))
            pages.debug_terminal.debug_log(f'Added skip at ({x}, {y}, {z})')
            editor_page.set_file_saved(False)           
            if printer.REALTIME_MODE:
                printer.realtime_goto((x, y), skip=True)
                cur_move_ind += 1

    elif event == 'Xin':
        editor_page.handle_coord_input(values["Xin"], "Xin")
    elif event == 'Yin':
        editor_page.handle_coord_input(values["Yin"], "Yin")
    elif event == 'Zin':
        editor_page.handle_coord_input(values["Zin"], "Zin")
    elif event == 'ZSk':
        editor_page.handle_coord_input(values["ZSk"], "ZSk")
    elif event =='_show_grid_':
        editor_page.handle_show_grid_toggle()
    elif event =='_realtime_mode_':
        editor_page.handle_realtime_toggle()
    elif event =='_lock_dxf_':
        editor_page.handle_lock_dxf_toggle()
    elif event =='_entire_view_':
        editor_page.handle_entire_view_toggle()
        if pages.viewport.Toggle_Capture and parse.coord_set != None:
            this_coord_num = 0
            for this_coord_num in range(len(parse.coord_set)):  
                this_coord = parse.coord_set[this_coord_num]
                if cur_ind == 0 and add_ind == 0:
                    pages.viewport.render_capture(this_coord[0], this_coord[1])
                else: 
                    if this_coord_num <= cur_ind:
                        pages.viewport.render_old_capture(this_coord[0], this_coord[1])
                    else:
                        pages.viewport.render_capture(this_coord[0], this_coord[1])
        if pages.viewport.Toggle_Capture and parse.wrong_coord_set != None:
            for wrong_coord in parse.wrong_coord_set:
                pages.viewport.render_wrong_capture(wrong_coord[0], wrong_coord[1])
    elif event =='toggle_zoom':
        editor_page.allow_zoom()
    elif event =='toggle_capture':
        editor_page.handle_capture_toggle()
    

    #elif event =='_preview_mode_':
    #    editor_page.handle_preview_mode_toggle()  

    # If the user manually enters a value into the Speed input.
    elif event == 'Spd':
        if values['Spd'].isnumeric(
        ) or not values['Spd']:  # Is the box numeric or empty?
            if values['Spd'] == '':  # Do nothing if the box is empty.
                pass
            else:
                # Convert from cm/s to cm/min, which is what the printer takes.
                parse.MOVE_SPEED = int(values['Spd']) * 60
        else:  # Otherwise, remove the last character
            editor_page.window['Spd'].update(value=values['Spd'][:-1])

    elif event == 'Add Move':  # If the user clicks "Add"
        # Check to make sure both manual inputs are filled.
        if values['Xin'] == '' or values['Yin'] == '':
            pages.debug_terminal.debug_log("Error! The X- or Y-Coordinate is empty!")
        elif parse.is_valid_coordinate(values['Xin']) and parse.is_valid_coordinate(values['Yin']) and parse.is_valid_coordinate(values['Zin']):
            editor_page.set_file_saved(False)
            pages.debug_terminal.debug_log(f'Added move at ({values["Xin"]}, {values["Yin"]})')
            # If no Z values were specified, use the defaults.
            if values['Zin'] == '':
                parse.add_travel((float(values['Xin']), float(values['Yin'])))
            # If Z-values were specified, use those, but cache the default in a 
            # variable called temp.
            else:
                temp = parse.Z_MOVE_HEIGHT
                parse.Z_MOVE_HEIGHT = float(values['Zin'])
                parse.add_travel((float(values['Xin']), float(values['Yin'])))
                Z_MOVE_HEIGHT = temp
                editor_page.window['Z_height'].update(value = values['Zin'])
                #editor_page.window.write_event_value('Z_height', '')

        else:
            pages.debug_terminal.debug_log(
                "Error! The X-, Y-, or Z Travel Coordinate is not a numeric value!")

    elif event == 'Add Skip':  # If the user clicks "Add". This is exactly the same as "Add", but using the Z skip values instead
        if values['Xin'] == '' or values['Yin'] == '':
            pages.debug_terminal.debug_log("Error! The X- or Y-Coordinate is empty!")
        elif parse.is_valid_coordinate(values['Xin']) and parse.is_valid_coordinate(values['Yin']) and parse.is_valid_coordinate(values['ZSk']):
            editor_page.set_file_saved(False)
            pages.debug_terminal.debug_log(f'Added skip at ({values["Xin"]}, {values["Yin"]})')
            if values['ZSk'] == '':
                parse.add_skip((float(values['Xin']), float(values['Yin'])))
            else:
                temp = parse.Z_SKIP_HEIGHT
                parse.Z_SKIP_HEIGHT = float(values['ZSk'])
                parse.add_skip((float(values['Xin']), float(values['Yin'])))
                parse.Z_SKIP_HEIGHT = temp

        else:
            pages.debug_terminal.debug_log(
                "Error! The X-, Y-, or Z Skip Coordinate is not a numeric value!")
            
    #elif camera.capture_flag:
    #    thread0.start()
    #    camera.capture_flag = False 

    elif printer.sending_serial: # if previous send command is not finished, continue it
        cur_move_ind = printer.send_via_serial(cur_move_ind)

    elif event == 'Send via Serial' and printer.PRINTER_CONNECTED:  # If "Send Via Serial" is pressed
        #printer.sending_serial = True
        cur_move_ind = printer.send_via_serial(cur_move_ind)

    # If no printer is connected, print an error message
    elif event == 'Send via Serial' and not printer.PRINTER_CONNECTED:
        pages.debug_terminal.debug_log(
            "Error! This feature is not available without a printer connected!")

    # If "Save To GCode" is pressed. This is the same as "Send Via Serial",
    # but the entire GCode is printed, rather than just the last, unexecuted
    # part. This is useful for saving one's work.

    elif event == 'Set Offset':
        editor_page.handle_set_offsets()
        editor_page.set_file_saved(False)
        if pages.viewport.Toggle_Capture and parse.coord_set != None:
            this_coord_num = 0
            for this_coord_num in range(len(parse.coord_set)):  
                this_coord = parse.coord_set[this_coord_num]
                if cur_ind == 0 and add_ind == 0 :
                    pages.viewport.render_capture(this_coord[0], this_coord[1])
                else: 
                    if this_coord_num <= cur_ind:
                        pages.viewport.render_old_capture(this_coord[0], this_coord[1])
                    else:
                        pages.viewport.render_capture(this_coord[0], this_coord[1])
        if pages.viewport.Toggle_Capture and parse.wrong_coord_set != None:
            for wrong_coord in parse.wrong_coord_set:
                pages.viewport.render_wrong_capture(wrong_coord[0], wrong_coord[1])

    elif event == 'Set Camera Offset':
        editor_page.handle_set_camera_offsets()
        editor_page.set_file_saved(False)
        if pages.viewport.Toggle_Capture and parse.coord_set != None:
            this_coord_num = 0
            for this_coord_num in range(len(parse.coord_set)):  
                this_coord = parse.coord_set[this_coord_num]
                if cur_ind == 0 and add_ind == 0:
                    pages.viewport.render_capture(this_coord[0], this_coord[1])
                else: 
                    if this_coord_num <= cur_ind:
                        pages.viewport.render_old_capture(this_coord[0], this_coord[1])
                    else:
                        pages.viewport.render_capture(this_coord[0], this_coord[1])
        if pages.viewport.Toggle_Capture and parse.wrong_coord_set != None:
            for wrong_coord in parse.wrong_coord_set:
                pages.viewport.render_wrong_capture(wrong_coord[0], wrong_coord[1])

    elif event == 'Take Image':
        
        file_path = sg.popup_get_file('Save Image', save_as=True, no_window=True, default_extension='jpg', file_types=(("JPEG Files", "*.jpg"), ("All Files", "*.*")))
        print(pages.viewport.Toggle_Capture)
        if file_path:           
            if not pages.viewport.Toggle_Capture:
                camera.take_image(file_path)
            else:
                if camera_coords != None:                 
                    all_images, cur_ind  = camera.take_multiple_images(file_path, camera_coords, add_ind, all_images)
                    add_ind+=(len(camera_coords)-add_ind)   
                else:
                      pages.debug_terminal.debug_log("Specify capture points")
        else:
            pages.debug_terminal.debug_log("Canceled")

    elif event == '<< Previous':
        cur_ind = camera.display_previous_image(all_images, cur_ind)
           
    elif event == 'Next >>':
        cur_ind = camera.display_next_image(all_images, cur_ind)  
    
    elif event == 'Adjust Z height':
        this_coords = parse.set_Z_offset(int(values['Z_height']))
        print([printer.PRINTER_HEAD_POS[0], printer.PRINTER_HEAD_POS[1]])
        if printer.PRINTER_HEAD_POS[0] == 0 and printer.PRINTER_HEAD_POS[1] == 0:
            coord = [7, 6]
        else:
            coord = [printer.PRINTER_HEAD_POS[0], printer.PRINTER_HEAD_POS[1]]
        printer.realtime_goto(coord, skip=False)

    elif event == 'Adjust res':
        camera.adjust_res(int(values['X_res']), int(values['Y_res']))

    elif event == 'Adjust Exposure':
        camera.adjust_exposure(float(values['Expo_Length']))

    # If the Home button is pressed, send the home GCode (G28)
    elif event == 'Autohome' and printer.PRINTER_CONNECTED:
        printer.SER.write(str.encode("G28W\r\n"))
        pages.debug_terminal.debug_log('Homing...')
    elif event == 'New':
        if not editor_page.FILE_SAVED:
            ans = sg.popup_ok_cancel("This file is unsaved! Do you wish to continue?")
            if ans != "OK":
                continue
        parse.file_open("Untitled")
        parse.INSTRUCTIONS.clear()
        pages.viewport.DXF_OBJS.clear()
        
        pages.code_output.render_code_output()
        pages.viewport.render_grid()
        editor_page.set_file_name("Untitled")
        editor_page.set_file_saved(True)
        add_ind = 0
        cur_ind = 0
        cur_move_ind = 0
        all_images = []


    elif event == 'Open':
        if not editor_page.FILE_SAVED:
            ans = sg.popup_ok_cancel("This file is unsaved! Do you wish to continue?")
            if ans != "OK":
                continue

        filename = sg.popup_get_file('message will be shown', no_window=True)
        # values['LoadFilePath']
        if not filename == '' and not filename is None:
            if parse.file_open(filename):
                editor_page.set_file_name(filename)
                editor_page.set_file_saved(True)

                pages.code_output.render_code_output()
                pages.viewport.render_grid()

    elif event == '_save_button_':
        if editor_page.FILE_NAME == "Untitled":
            sg.popup_error("File is new -- please click Save As!")
            continue
        if parse.file_save_as(editor_page.FILE_NAME):
            editor_page.set_file_saved(True)

    elif event == 'SaveFilePath': # on Save As
        filename = values["SaveFilePath"]
        if parse.file_save_as(filename):
            editor_page.set_file_name(filename)
            editor_page.set_file_saved(True)

    elif event == 'Add Delay':
        editor_page.set_file_saved(False)
        delay = sg.popup_get_text(
            'Enter the delay time in miliseconds', title="Textbox")
        if delay is None or delay == "":
            continue
        parse.INSTRUCTIONS.append(parse.InstructionG04(p=int(float(delay))))
        pages.code_output.render_code_output()
        pages.viewport.render_vertices()
        pages.debug_terminal.debug_log(f'Added delay for {delay} miliseconds')

        # ToolPath.append
        ############ PYSimpleGUI ends here############

    elif (event == '_debug_term_clear_button_'):
        editor_page.handle_debug_term_clear()
        editor_page.set_file_saved(False)

    elif event == 'Import DXF':
        file_types = [("DXF Files", "*.dxf")]
        filename = sg.popup_get_file('Select a DXF file to import', no_window=True, file_types=file_types)
        pages.viewport.save_dxf(filename)
        pages.viewport.render_grid()



    elif event == 'Submit via Serial': # this is for the syringe
        volumn = values["-VOLUMN-"]
        flowrate = values["-FLOWRATE-"]
        selected_syringe = values["-SYRINGE-"]
        velocity = syringe.velocityCalc(flowrate)
        distance = syringe.distanceCalc(velocity)
        
        if pages.viewport.Toggle_Pull:
            parse.add_pull(velocity, distance)
        if pages.viewport.Toggle_Push:
            parse.add_push(velocity, distance)
        #printer.send_via_serial()

    elif event == 'SaveSyringePath':
        filename = values['SaveSyringePath']
        if parse.syringe_save_as(filename):
            continue
    elif event == '-VOLUMN-':
        editor_page.handle_coord_input(values['-VOLUMN-'], '-VOLUMN-', maxVal=1000)
        try:
            volumn = int(values["-VOLUMN-"])
            selected_syringe = values["-SYRINGE-"]
            
            if selected_syringe == '0.5mL':
                editor_page.handle_coord_input(values['-VOLUMN-'], '-VOLUMN-', maxVal=500)
        except ValueError:
            editor_page.window["-VOLUMN-"].update(value='')

    
    elif event == '-FLOWRATE-':
        editor_page.handle_coord_input(values['-FLOWRATE-'], '-FLOWRATE-', maxVal=1000)
        try:
            flowrate = int(values['-FLOWRATE-'])        
            if 400 <= flowrate <= 1001:
                editor_page.window["-SYRINGE-"].update(value='1mL')
            elif 0 <= flowrate <= 399:
                editor_page.window["-SYRINGE-"].update(value='0.5mL')
            else:
                editor_page.window["-SYRINGE-"].update(value='N/A')  # Clear selection if out of range
                editor_page.window["-FLOWRATE-"].update(value='')
        except ValueError:
            editor_page.window["-SYRINGE-"].update(value='N/A')
            editor_page.window["-FLOWRATE-"].update(value='')

    elif event == 'toggle_pullpush':
        pages.viewport.Toggle_Pull = not pages.viewport.Toggle_Pull
        pages.viewport.Toggle_Push = not pages.viewport.Toggle_Push
        
# If the window is closed.

editor_page.window.close()  # Close the PYSimpleGUI window.
camera.cleanup_camera()
printer.cleanup_printer()

