import tkinter as tk
from datetime import datetime, timedelta
from loguru import logger

logger.add('stopwatch.log')

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

        self.bind_everything()
        self.update_clock()

    def bind_everything(self) -> None:
        self.bind('<Button-1>', self.click)
        self.bind('<B1-Motion>', self.drag)
        self.bind('<ButtonRelease-1>', self.release)
        self.bind('<Double-Button-1>', self.quit_app)

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
        now = datetime.now()
        h = now.hour
        m = now.minute

        is_long_break_hour = (h % 3 == 0)

        if is_long_break_hour and m < 35:
            state = "BREAK"
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
        
        self.after(200, self.update_clock)

if __name__ == '__main__':
    app = Stopwatch()
    app.mainloop()