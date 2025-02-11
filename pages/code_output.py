import PySimpleGUI as sg

import parse

code_table_output = sg.Table(
    key="_code_table_output_",
    values=[],
    size=(50, 25),
    expand_x=True,
    enable_events=True,
    headings=["Operation", "X (mm)", "Y (mm)", "Z (mm)",
              "Speed (mm/min)", "P (ms)"]
)
code_string_output = sg.Multiline(
    size=(50, 30),
    expand_x=True,
    disabled=True,
)

def render_code_output():
    '''responsible for printing all the GCode to table outputs'''
    table_data = []
    code_data = parse.INSTRUCTIONS_HEADER

    for instr in parse.INSTRUCTIONS:
        table_data.append(instr.tableify())
        code_data = code_data + instr.stringify(do_comment=True) + "\n"

    code_table_output.update(values=table_data)
    code_table_output.set_vscroll_position(1)
    code_string_output.Update(code_data)

def render_camera_output():
    '''responsible for printing all the Camera GCode to table outputs'''
    table_data = []
    code_data = parse.INSTRUCTIONS_HEADER

    for instr in parse.INSTRUCTIONS:
        table_data.append(instr.tableify())
        code_data = code_data + instr.stringify(do_camera_comment=True) + "\n"

    code_table_output.update(values=table_data)
    code_table_output.set_vscroll_position(1)
    code_string_output.Update(code_data)