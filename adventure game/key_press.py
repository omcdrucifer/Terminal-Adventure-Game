import os
import sys
import time
import select

class KeyboardInput:
    def __init__(self):
        self.is_windows = os.name == 'nt'
        if self.is_windows:
            import msvcrt
        else:
            import tty
            import termios
        self.msvcrt = msvcrt if self.is_windows else None
        self.tty = tty if not self.is_windows else None
        self.termios = termios if not self.is_windows else None

    def get_key(self):
        if self.is_windows:
            if self.msvcrt.kbhit():
                return self.msvcrt.getch().decode('utf-8').upper()
            return None
        else:
            fd = sys.stdin.fileno()
            old_settings = self.termios.tcgetattr(fd)
            try:
                self.tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                return ch.upper()
            finally:
                self.termios.tcsetattr(fd, self.termios.TCSADRAIN, old_settings)

    def check_for_key(self, timeout=0.1):
        if self.is_windows:
            start = time.time()
            while time.time() - start < timeout:
                if self.msvcrt.kbhit():
                    return self.msvcrt.getch().decode('utf-8').upper()
                time.sleep(0.01)
        else:
            fd = sys.stdin.fileno()
            old_settings = self.termios.tcgetattr(fd)
            try:
                self.tty.setraw(fd)
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                if rlist:
                    return sys.stdin.read(1).upper()
            finally:
                self.termios.tcsetattr(fd, self.termios.TCSADRAIN, old_settings)
        return None
