import PySimpleGUI as sg
import editor_page
import parse

def make_welcome_window():
    welcome_left_col = sg.Column([
        [sg.Image("welcome-d.png")],
    ])
    welcome_right_col = sg.Column([
        [sg.Button('New Project', size=(15,2))],
        [sg.Button('Open Project', size=(15,2))],
        [sg.Button('Open Examples', size=(15, 2))],
    ])

    welcome_layout = [
        [sg.VPush()],
        [sg.Push(), welcome_left_col, welcome_right_col, sg.Push()],
        [sg.VPush()],
    ]
    return sg.Window("Ferrobotics Device Controller", welcome_layout, finalize=True)

welcome_window = make_welcome_window()

while True:

    event, values = welcome_window.read()


    if event == sg.WIN_CLOSED:    # if user closes window or clicks cancel
        break
    elif event == 'New Project':
        editor_page.init("Untitled")
        welcome_window.close()

    elif event == 'Open Project':

        filename = sg.popup_get_file('message will be shown', no_window=True)
        # values['LoadFilePath']
        if not filename == '' and not filename is None:
            editor_page.init(filename)
            welcome_window.close()
