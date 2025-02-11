import PySimpleGUI as sg

def debug_log(message):
    '''output debug message'''
    debug_terminal_output.print(message)
    print(message)

debug_terminal_output = sg.Multiline(
    size=(70, 15),
    expand_x=True,
    disabled=True
)



def debug_clear():
    '''clearing the debug terminal'''
    debug_terminal_output.update('')

syringe_terminal_output = sg.Multiline(
    size=(70, 30),
    expand_x=True,
    disabled=True)

def syringe_log(message):
    '''output debug message'''
    syringe_terminal_output.print(message)
    print(message)