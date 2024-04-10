
class Utils:

    def __init__(self):
        pass

    def colors(self, color):
        if color == 'GREEN':
            GREEN = '\u001b[32m'
            return GREEN
        elif color == 'GREEN2':
            GREEN2 = '\033[92m'
            return GREEN2
        elif color == 'ENDC':
            ENDC = '\033[0m'
            return ENDC
        elif color == 'BOLD':
            BOLD = '\033[1m'
            return BOLD
        elif color == 'UNDERLINE':
            UNDERLINE = '\033[4m'
            return UNDERLINE
        elif color == 'RED':
            RED = '\u001b[31m'
            return RED

print(Utils().colors('BOLD') + Utils().colors('GREEN2') + "test" + Utils().colors('ENDC'))
