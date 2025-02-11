import PySimpleGUI as sg

import pages.code_output

code_editor_g01 = sg.Column(
    [[
        sg.Text("G01", size=(3, 1)),
        sg.Text("X:", size=(1, 1)),
        sg.InputText(key='_code_editor_g01_x_', size=(10, 1), expand_y=True, enable_events=True),
        sg.Text("Y:", size=(1, 1)),
        sg.InputText(key='_code_editor_g01_y_', size=(10, 1), expand_y=True, enable_events=True),
        sg.Text("Z:", size=(1, 1)),
        sg.InputText(key='_code_editor_g01_z_', size=(10, 1), expand_y=True, enable_events=True),
        sg.Text("F:", size=(1, 1)),
        sg.InputText(key='_code_editor_g01_f_', size=(10, 1), expand_y=True, enable_events=True),
    ],
    [
        sg.Button("Update Changes", expand_y=True, key="_code_editor_submit_button_", visible=False),
        sg.Button("Delete Point", expand_y=True, key="_code_editor_delete_button_"),
        sg.Button("Delete all DXFs", expand_y=True, key="_code_editor_delete_dxf_button_")
    ]],
    key="_code_editor_g01_",
)

code_editor_g04 = sg.Column(
    [[
        sg.Text("G04", size=(3, 1)),
        sg.Text("P:", size=(1, 1)),
        sg.InputText(key='_code_editor_g04_p_', size=(10, 1), expand_y=True, enable_events=True),
    ],
    [
        sg.Button("Update Changes", expand_y=True, key="_code_editor_submit_button2_", visible=False),
        sg.Button("Delete", expand_y=True, key="_code_editor_delete_button2_")
    ]],
    key="_code_editor_g04_",
    visible=False
)
