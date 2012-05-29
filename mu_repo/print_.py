'''
Created on 17/05/2012

@author: Fabio Zadrozny
'''
import sys

START_COLOR = '${START_COLOR}'
RESET_COLOR = '${RESET_COLOR}'



try:
    def _InitWin32():

        #===========================================================================================
        # Console
        #===========================================================================================
        class _Console(object):

            def __init__(self):
                import win32console

                colors = dict(
                    BLACK=[],
                    BLUE=['BLUE'],
                    CYAN=['GREEN', 'BLUE'],
                    GREEN=['GREEN'],
                    MAGENTA=['RED', 'BLUE'],
                    RED=['RED'],
                    WHITE=['RED', 'GREEN', 'BLUE'],
                    YELLOW=['RED', 'GREEN'],
                )


                self._foreground_map = color_map = { '' : 0 }
                for color_name, color_components in colors.iteritems():
                    if color_components:
                        value = getattr(win32console, 'FOREGROUND_INTENSITY')
                    else:
                        value = 0
                    for component in color_components:
                        value |= getattr(win32console, 'FOREGROUND_' + component)
                    color_map[color_name] = value

                #Some of the calls below could raise exceptions, in which case we should
                #fallback to another approach!
                self._output_handle = win32console.GetStdHandle(win32console.STD_OUTPUT_HANDLE)
                self._reset = self._output_handle.GetConsoleScreenBufferInfo()['Attributes']
                self._console = win32console.PyConsoleScreenBufferType(self._output_handle)

            def SetColor(self, foreground_color):
                self._console.SetConsoleTextAttribute(self._foreground_map[foreground_color])

            def Reset(self):
                self._console.SetConsoleTextAttribute(self._reset)

        return _Console()

    console = _InitWin32()


except:
    #If anything fails there, use the version that prints ascii chars.

    #===============================================================================================
    # Console
    #===============================================================================================
    class _Console(object):

        color_map = {
            'BLACK'   : 30,
            'BLUE'    : 34,
            'CYAN'    : 36,
            'GREEN'   : 32,
            'MAGENTA' : 35,
            'RED'     : 31,
            'WHITE'   : 37,
            'YELLOW'  : 33,
        }

        def _Escape(self, code):
            sys.stdout.write('\033[' + code)

        def SetColor(self, foreground_color):
            self._Escape('%dm' % self.color_map[foreground_color])

        def Reset(self):
            self._Escape('0m')


    console = _Console()


_ignore_print = 0


#===================================================================================================
# PushIgnorePrint
#===================================================================================================
def PushIgnorePrint():
    global _ignore_print
    _ignore_print += 1


#===================================================================================================
# PopIgnorePrint
#===================================================================================================
def PopIgnorePrint():
    global _ignore_print
    _ignore_print -= 1



#===================================================================================================
# Print
#===================================================================================================
def Print(*args, **kwargs):
    if _ignore_print:
        return

    assert 'file' not in kwargs
    f = sys.stdout
    try:
        msg = ' '.join(args)
    except:
        msg = ' '.join(str(x) for x in args)

    i = msg.find(START_COLOR)
    while i >= 0:
        write_without_color = msg[:i]
        f.write(write_without_color)

        msg = msg[i + len(START_COLOR):]
        i = msg.find(RESET_COLOR)
        if i >= 0:
            write_in_colors = msg[:i]
            msg = msg[i + len(RESET_COLOR):]
        else:
            write_in_colors = msg
            msg = '' #No RESET after start: go until end of string.

        console.SetColor('CYAN')
        try:
            f.write(write_in_colors)
        finally:
            console.Reset()
        i = msg.find(START_COLOR)

    f.write(msg)
    f.write('\n')

