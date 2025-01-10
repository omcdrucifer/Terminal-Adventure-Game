import os
import sys
import time
import select
from typing import Optional, Any

# Try importing Windows-specific module
try:
    import msvcrt
except ImportError:
    msvcrt = None

# Try importing Unix-specific modules
try:
    import tty
    import termios
except ImportError:
    tty = None
    termios = None

class KeyboardInput:
    def __init__(self) -> None:
        self.is_windows: bool = os.name == 'nt'
        self.msvcrt: Optional[Any] = msvcrt if self.is_windows else None
        self.tty: Optional[Any] = tty if not self.is_windows else None
        self.termios: Optional[Any] = termios if not self.is_windows else None

    def get_key(self) -> Optional[str]:
        if self.is_windows:
            if self.msvcrt and hasattr(self.msvcrt, 'kbhit') and self.msvcrt.kbhit():
                if hasattr(self.msvcrt, 'getch'):
                    return self.msvcrt.getch().decode('utf-8').upper()
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
                
            start = time.time()
            while time.time() - start < timeout:
                if hasattr(self.msvcrt, 'kbhit') and self.msvcrt.kbhit():
                    if hasattr(self.msvcrt, 'getch'):
                        return self.msvcrt.getch().decode('utf-8').upper()
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
