import PySimpleGUI as sg

import parse
import ezdxf
import math
import numpy as np

SHOW_GRID = True
EPSILON = 0.000001 # prevents divide by zero errors. Put it in denominator of all fractions.



l_printer = True
LOCK_DXFS = False
Toggle_Zoom = False
Toggle_Capture = False
Toggle_Pull = False
Toggle_Push = True

larger_printer_checkbox = sg.Checkbox("Entire view", default=l_printer, enable_events=True, key="_entire_view_")
lock_dxf_checkbox = sg.Checkbox("Lock dxfs", default=LOCK_DXFS, enable_events=True, key="_lock_dxf_")
toggle_zoom_checkbox = sg.Checkbox("Toggle Zoom", default=Toggle_Zoom, enable_events=True, key="toggle_zoom")
toggle_capture_checkbox = sg.Checkbox("Toggle Capture", default=Toggle_Capture, enable_events=True, key="toggle_capture")
toggle_pullpush_checkbox = sg.Checkbox("Toggle Pull (Deselect for Push)", default=Toggle_Capture, enable_events=True, key="toggle_pullpush")


global grid, max_coord, max_coordx, max_coordy

max_coord = 200
max_coordx = 200
max_coordy = 200
grid = sg.Graph(
    (500, 500),
    (0, 0),
    (max_coord, max_coord),
    background_color='white',
    key='Path',
    enable_events=True,
    drag_submits=True
    
)
show_grid_checkbox = sg.Checkbox("Show Grid", default=SHOW_GRID, enable_events=True, key="_show_grid_")
dragmode = False
dragmode_instr_idx = None
dragmode_dxf_idx = None
dragmode_dxf_offset = None
mouse_down = False

def init():
    # Allow the mouse's right click to be used. (For Macs)
    grid.bind("<Button-2>", 'RightClick')
    # Allow the mouse's right click to be used.
    grid.bind("<Button-3>", 'RightClick')

def render_grid():
    '''responsible for drawiyellowng the yellow and purple lines representing the tool's movement.'''
    # Maybe make this efficient?
    table_data = []
    grid.erase()
    if SHOW_GRID:
        max_coord = 200


        if Toggle_Capture:
            max_coord_x = int(np.min((max_coord + parse.CAMERA_X, max_coord)))
            max_coord_y = int(np.min((max_coord + parse.CAMERA_Y, max_coord)))
        else:
            max_coord_x = max_coord
            max_coord_y = max_coord

        for rect_y in range(0, int(parse.OFFSET_Y), 1):
            grid.draw_line((0, rect_y), (max_coord_x, rect_y), color="orange", width=1)
        for rect_y in range(int(parse.OFFSET_Y), max_coord_y, 1):
            grid.draw_line((0, rect_y), (int(parse.OFFSET_X), rect_y), color="orange", width=1)
        for rect_y in range(int(parse.OFFSET_Y), max_coord_y, 1):
            grid.draw_line((int(parse.OFFSET_X), rect_y), (max_coord_x, rect_y), color="#ddd", width=1)
        
        for rect_y in range(max_coord_y, max_coord, 1):    
            grid.draw_line((0, rect_y), (max_coord, rect_y), color="red", width=1)
        for rect_y in range(0, max_coord_y, 1):    
            grid.draw_line((max_coord_x, rect_y), (max_coord, rect_y), color="red", width=1)
        
        for rect_x in range(0, int(parse.OFFSET_X), 1):
            grid.draw_line((rect_x, 0), (rect_x, max_coord_y), color="orange", width=1)
        for rect_x in range(int(parse.OFFSET_X),  max_coord_x,1):
            grid.draw_line((rect_x, 0), (rect_x, int(parse.OFFSET_Y)), color="orange", width=1)
        for rect_x in range(int(parse.OFFSET_X), max_coord_x, 1):
            grid.draw_line((rect_x, int(parse.OFFSET_Y)), (rect_x, max_coord_y), color="#ddd", width=1)
        for rect_x in range(0, max_coord, 1):    
            grid.draw_line((rect_x, max_coord_y), (rect_x, max_coord), color="red", width=1)
        for rect_x in range(max_coord_x, max_coord, 1):    
            grid.draw_line((rect_x, 0), (rect_x, max_coord_y), color="red", width=0.1)

        for rect_y in range(0, int(parse.OFFSET_Y), 5):
            grid.draw_line((0, rect_y), (int(parse.OFFSET_X), rect_y), color="orange", width=1)
        for rect_y in range(int(parse.OFFSET_Y), max_coord_y, 5):
            grid.draw_line((int(parse.OFFSET_X), rect_y), (max_coord_x, rect_y), color="black", width=1)

        for rect_y in range(max_coord_y, max_coord, 5):    
            grid.draw_line((max_coord_x, rect_y), (max_coord, rect_y), color="red", width=1)

        for rect_x in range(0, int(parse.OFFSET_X), 5):
            grid.draw_line((rect_x, 0), (rect_x, int(parse.OFFSET_Y)), color="orange", width=1)
        for rect_x in range(int(parse.OFFSET_X), max_coord_x, 5):
            grid.draw_line((rect_x, int(parse.OFFSET_Y)), (rect_x, max_coord_y), color="black", width=1)

        for rect_x in range(max_coord_x, max_coord, 5):
            grid.draw_line((rect_x, max_coord_y), (rect_x, max_coord), color="red", width=1)

    table_data.clear()

    prev_x = -1
    prev_y = -1
    prev_z = -1

    for instr in parse.INSTRUCTIONS:
        if isinstance(instr, parse.InstructionG01):
            x = instr.data["x"]
            y = instr.data["y"]
            z = instr.data["z"]
            if prev_x == -1:
                prev_x = x
                prev_y = y
                prev_z = z
            
            if z == parse.Z_MOVE_HEIGHT and prev_z == parse.Z_MOVE_HEIGHT: # is move line?
                grid.draw_line((prev_x, prev_y),
                                (x, y), color='blue', width=1)
            elif z > parse.Z_MOVE_HEIGHT and prev_z > parse.Z_MOVE_HEIGHT: # is skip line?
                grid.draw_line((prev_x, prev_y),
                                (x, y), color='cyan', width=1)
            else:
                grid.draw_line((prev_x, prev_y),
                                (x, y), color='#0080ff', width=1)
            
            # .append() for table
        prev_x = x
        prev_y = y
        prev_z = z
    render_vertices()
    for dxf_obj in DXF_OBJS:
        dxf_obj.render() 

    # if CAMERA_CONNECTED:
        # display_camera_image = grid.draw_image(data=Image, location=(0,100))    # draw new image
        # grid.send_figure_to_back(display_camera_image)
    # print("LESS2")


def render_vertices():
    for i, instr in enumerate(parse.INSTRUCTIONS):
        if isinstance(instr, parse.InstructionG01):
            
            x = instr.data["x"]
            y = instr.data["y"]
            render_vertex(x, y)
        elif isinstance(instr, parse.InstructionG04):
            # find previous G01
            x, y = parse.instructions_get_prev_g01_from_index(i)
            render_wait_vertex(x, y)
            

def render_wait_vertex(x, y, emphasized=False):
    grid.draw_circle(
        (x, y),
        radius=1,
        fill_color = "#ff0000" if emphasized else "#00ff00",
        line_color= "black"
    )

def render_vertex(x, y, emphasized=False):
    grid.draw_rectangle(
        (x + 0.7, y + 0.7),
        (x - 0.7, y - 0.7),
        fill_color = "#ff0000" if emphasized else "#0000ff",
        line_width=0
    )

def render_capture(x,y,emphasized = False):
    grid.draw_circle(
        (x, y),
        radius= 2,
        fill_color = None,
        line_color= "green",
        line_width= 2
    )
    grid.draw_circle(
        (x, y),
        radius=1,
        fill_color = "#00FF00",
        line_color= "green"
    )

def render_old_capture(x,y,emphasized = False):
    grid.draw_circle(
        (x, y),
        radius= 2,
        fill_color = None,
        line_color= "blue",
        line_width= 2
    )
    grid.draw_circle(
        (x, y),
        radius=1,
        fill_color = "#00FF00",
        line_color= "blue"
    )

def render_wrong_capture(x, y):
    grid.draw_line(
        (x-2,y-2), (x+2,y+2),
        color= "red",
        width= 2
    )
    grid.draw_line(
        (x-2,y+2), (x+2,y-2),
        color= "red",
        width= 2
    )

def adjust_max(point, max_top_left, max_bottom_right):
    if point[0] < max_top_left[0]:
        max_top_left[0] = point[0]
    if point[0] > max_bottom_right[0]:
        max_bottom_right[0] = point[0]
    if point[1] < max_bottom_right[1]:
        max_bottom_right[1] = point[1]
    if point[1] > max_top_left[1]:
        max_top_left[1] = point[1]

class dxf_obj:
    def __init__(self, modelspace):
        self.modelspace = modelspace
        self.offset = (0,0)
        self.zoom = 1
    
    def get_offset(self, coord):
        return (coord[0] - self.offset[0], coord[1] - self.offset[1])

    def move(self, coord, offset):
        self.offset = (coord[0] - offset[0], coord[1] - offset[1])

    def render(self):
        if LOCK_DXFS:
            color_dxf = "#a00000"
        else:
            color_dxf = "red"

        # to find bounding box of dxf
        max_top_left = [1000, -1000]
        max_bottom_right = [-1000, 1000]

        for entity in self.modelspace:
            if entity.dxftype() == 'LWPOLYLINE':
                entity.explode()

        for entity in self.modelspace:
            if entity.dxftype() == 'LINE':
                start_point = (entity.dxf.start[0] * self.zoom + self.offset[0], entity.dxf.start[1] * self.zoom + self.offset[1])
                end_point = (entity.dxf.end[0] * self.zoom + self.offset[0], entity.dxf.end[1] * self.zoom + self.offset[1])
                grid.draw_line(start_point, end_point, color=color_dxf, width=1)

                adjust_max(start_point, max_top_left, max_bottom_right)
                adjust_max(end_point, max_top_left, max_bottom_right)
            elif entity.dxftype() == 'ARC':
                center_point = (entity.dxf.center[0] * self.zoom + self.offset[0], entity.dxf.center[1] * self.zoom + self.offset[1])
                radius = entity.dxf.radius * self.zoom
                top_left = (center_point[0] - radius, center_point[1] + radius)
                bottom_right = (center_point[0] + radius, center_point[1] - radius)
                adjust_max(top_left, max_top_left, max_bottom_right)
                adjust_max(bottom_right, max_top_left, max_bottom_right)

                # compute the starting angles
                start_point = (entity.start_point[0] * self.zoom + self.offset[0], entity.start_point[1] * self.zoom + self.offset[1])
                end_point = (entity.end_point[0] * self.zoom + self.offset[0], entity.end_point[1] * self.zoom + self.offset[1])
                start_angle =math.degrees(math.atan((start_point[1] - center_point[1])/(start_point[0] - center_point[0] + EPSILON)))
                if (start_point[0] - center_point[0] < 0):
                    start_angle += 180 
                end_angle =math.degrees(math.atan((end_point[1] - center_point[1])/(end_point[0] - center_point[0] + EPSILON)))
                if (end_point[0] - center_point[0] < 0):
                    end_angle += 180 
                
                # always go counter clockwise
                if end_angle > start_angle:
                    extent = end_angle - start_angle
                else:
                    extent = (end_angle + 360) - start_angle

                grid.draw_arc(top_left, bottom_right, extent, start_angle, style="arc", arc_color=color_dxf, line_width=1)
            else:
                print("unrecognized dxftype!", entity.dxftype())
        self.max_top_left = max_top_left
        self.max_bottom_right = max_bottom_right

    def delete(self):
        global DXF_OBJS
        try:
            DXF_OBJS.remove(self)
            print(f"DXF object {self} has been deleted.")
        except ValueError:
            print(f"DXF object {self} not found in list.")

DXF_OBJS = []
    
def save_dxf(filename):
    if filename:  # Check if filename is not None
        try:
            doc = ezdxf.readfile(filename)
            modelspace = doc.modelspace()
            DXF_OBJS.append(dxf_obj(modelspace))
        except Exception as e:
            print(f"Error reading DXF file: {e}")
    else:
        print("No file selected or file selection canceled.")

def anything_near_click(coord):
    for i, dxf_obj in enumerate(DXF_OBJS):
        if coord[0] > dxf_obj.max_top_left[0] and coord[0] < dxf_obj.max_bottom_right[0] and coord[1] < dxf_obj.max_top_left[1] and coord[1] > dxf_obj.max_bottom_right[1]:
            return True, i
    return False, -1
