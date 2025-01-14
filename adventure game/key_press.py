import os
import sys
import time
import select
from typing import Optional

try:
    import msvcrt  # type: ignore
except ImportError:
    msvcrt = None

try:
    import tty
    import termios
except ImportError:
    tty = None
    termios = None

class KeyboardInput:
    def __init__(self):
        self.is_windows = os.name == "nt"
        self.msvcrt = msvcrt if self.is_windows else None
        self.tty = tty if not self.is_windows else None
        self.termios = termios if not self.is_windows else None

    def get_key(self) -> Optional[str]:
        if self.is_windows:
            if self.msvcrt and self.msvcrt.kbhit():  # type: ignore
                return self.msvcrt.getch().decode("utf-8").upper()  # type: ignore
            return None
        else:
            if not (self.tty and self.termios):
                return None

            fd = sys.stdin.fileno()
            old_settings = self.termios.tcgetattr(fd)
            try:
                self.tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
                return ch.upper()
            finally:
                self.termios.tcsetattr(fd, self.termios.TCSADRAIN, old_settings)

    def check_for_key(self, timeout: float = 0.1) -> Optional[str]:
        if self.is_windows:
            if not self.msvcrt:
                return None

            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.msvcrt.kbhit():  # type: ignore
                    return self.msvcrt.getch().decode("utf-8").upper()  # type: ignore
                time.sleep(0.01)
        else:
            if not (self.tty and self.termios):
                return None

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
