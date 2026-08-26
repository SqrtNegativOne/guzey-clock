import os
import sys
import tkinter as tk
from datetime import datetime, timedelta
from loguru import logger

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, 'log')
os.makedirs(LOG_DIR, exist_ok=True)
logger.add(os.path.join(LOG_DIR, 'stopwatch.log'), rotation="10 MB", retention="10 days", enqueue=True)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

STOPWATCH_BACKGROUND = 'black'
LABEL_PAUSED_COLOUR = 'grey'
LABEL_WORK_COLOUR = 'white'
LABEL_BREAK_COLOUR = '#2ecc71'
STOPWATCH_FONT = ('Consolas', 12)
DEFAULT_ALPHA = 0.7
WIDTH = 200
HEIGHT = 10

from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1) # Updates all screen and window resolutions by ×1.5. Required for cleaner fonts.
windll.kernel32.SetConsoleTitleW("GuzeyClock") # Changes the title of the console window, if it exists.

class Stopwatch(tk.Tk):
    def __init__(self, *args, **kwargs) -> None:
        logger.info('Stopwatch initialised.')

        tk.Tk.__init__(self, *args, **kwargs)
        self.overrideredirect(True) 
        self.attributes('-topmost', True)

        self.config(bg=STOPWATCH_BACKGROUND)
        self.alpha: float = DEFAULT_ALPHA
        self.attributes('-alpha', self.alpha)
        self.minsize(width=WIDTH, height=HEIGHT)
        self.geometry('+0+0')
        
        self.label: tk.Label = tk.Label(
            self,
            text='00',
            foreground=LABEL_PAUSED_COLOUR,
            font=STOPWATCH_FONT,
            bg=STOPWATCH_BACKGROUND
        )
        self.label.pack()

        self.muted = False
        self.current_state = None

        self.bind_everything()
        self.update_clock()

    def bind_everything(self) -> None:
        self.bind('<Button-1>', self.click)
        self.bind('<B1-Motion>', self.drag)
        self.bind('<ButtonRelease-1>', self.release)
        self.bind('<Double-Button-1>', self.quit_app)
        self.bind('<m>', self.toggle_mute)
        self.bind('<M>', self.toggle_mute)

    def toggle_mute(self, event) -> None:
        self.muted = not self.muted
        logger.info(f"Sound effects {'muted' if self.muted else 'unmuted'}.")

    def click(self, event) -> None:
        self.x = event.x
        self.y = event.y
        self.attributes('-alpha', self.alpha - 0.15)

    def drag(self, event) -> None:
        x = event.x - self.x + self.winfo_x()
        y = event.y - self.y + self.winfo_y()
        self.geometry(f'+{x}+{y}')

    def release(self, event) -> None:
        self.attributes('-alpha', self.alpha)

    def quit_app(self, event) -> None:
        self.destroy()

    def update_clock(self) -> None:
        self.attributes('-topmost', True)
        now = datetime.now()
        h = now.hour
        m = now.minute

        is_long_break_hour = (h % 3 == 0)

        if is_long_break_hour and m < 35:
            state = "LONG_BREAK"
            next_min = 35
            color = LABEL_BREAK_COLOUR
        else:
            if 0 <= m < 5:
                state = "BREAK"
                next_min = 5
                color = LABEL_BREAK_COLOUR
            elif 5 <= m < 30:
                state = "WORK"
                next_min = 30
                color = LABEL_WORK_COLOUR
            elif 30 <= m < 35:
                state = "BREAK"
                next_min = 35
                color = LABEL_BREAK_COLOUR
            else:
                state = "WORK"
                next_min = 60 
                color = LABEL_WORK_COLOUR

        target = now.replace(second=0, microsecond=0)
        if next_min == 60:
            target = target.replace(minute=0) + timedelta(hours=1)
        else:
            target = target.replace(minute=next_min)

        remaining = target - now
        rem_s = int(remaining.total_seconds())
        rem_m, rem_s = divmod(rem_s, 60)

        display_text = f"{state}: {rem_m:02d}:{rem_s:02d} left"
        
        self.label.config(text=display_text, foreground=color)
        
        if self.current_state is not None and self.current_state != state:
            self.on_state_change(self.current_state, state)
        self.current_state = state
        
        self.after(200, self.update_clock)

    def on_state_change(self, old_state: str, new_state: str) -> None:
        logger.info(f"State changed from {old_state} to {new_state}")
        import os
        src_dir = os.path.dirname(os.path.abspath(__file__))
        if not self.muted:
            import winsound
            sound_file = None
            if old_state == "WORK" and new_state == "BREAK":
                sound_file = os.path.join(src_dir, "sounds", "work_to_break.wav")
            elif old_state == "BREAK" and new_state == "WORK":
                sound_file = os.path.join(src_dir, "sounds", "break_to_work.wav")
            elif old_state == "WORK" and new_state == "LONG_BREAK":
                sound_file = os.path.join(src_dir, "sounds", "work_to_long_break.wav")
            elif old_state == "LONG_BREAK" and new_state == "WORK":
                sound_file = os.path.join(src_dir, "sounds", "long_break_to_work.wav")
            
            if sound_file and os.path.exists(sound_file):
                winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)

        import subprocess
        import sys
        effect_script = os.path.join(src_dir, "effect.py")
        subprocess.Popen([sys.executable, effect_script], creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)

if __name__ == '__main__':
    app = Stopwatch()
    app.mainloop()