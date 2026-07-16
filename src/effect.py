import tkinter as tk
from ctypes import windll
import threading

class ScreenEffect(tk.Tk):
    def __init__(self):
        super().__init__()
        
        try:
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.attributes('-transparentcolor', 'black')
        self.attributes('-alpha', 1.0)
        
        self.state('zoomed')
        self.update_idletasks()
        
        self.w = self.winfo_width()
        self.h = self.winfo_height()
        
        self.geometry(f"{self.w}x{self.h}+0+0")
        self.config(bg='black')
        
        self.canvas = tk.Canvas(self, width=self.w, height=self.h, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        try:
            hwnd = windll.user32.GetParent(self.winfo_id())
            style = windll.user32.GetWindowLongW(hwnd, -20)
            windll.user32.SetWindowLongW(hwnd, -20, style | 0x00000020 | 0x00080000)
        except Exception:
            pass
        
        self.left_line = self.canvas.create_line(self.w/2, self.h, self.w/2, self.h, fill='#00ffcc', width=2, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        self.right_line = self.canvas.create_line(self.w/2, self.h, self.w/2, self.h, fill='#00ffcc', width=2, capstyle=tk.ROUND, joinstyle=tk.ROUND)

        self.progress = 0.0
        self.state = "animate"
        self.flash_count = 0
        self.fade_alpha = 1.0
        
        self.animate()

    def get_points(self, t, is_left):
        W2 = self.w / 2
        H = self.h
        total_len = W2 + H + W2
        
        current_len = t * total_len
        pts = [W2, H]
        
        sign = -1 if is_left else 1
        
        if current_len <= W2:
            pts.extend([W2 + sign * current_len, H])
        else:
            pts.extend([W2 + sign * W2, H])
            rem1 = current_len - W2
            if rem1 <= H:
                pts.extend([W2 + sign * W2, H - rem1])
            else:
                pts.extend([W2 + sign * W2, 0])
                rem2 = rem1 - H
                if rem2 <= W2:
                    pts.extend([W2 + sign * W2 - sign * rem2, 0])
                else:
                    pts.extend([W2, 0])
        return pts

    def animate(self):
        if self.state == "animate":
            self.progress += 0.02
            if self.progress >= 1.0:
                self.progress = 1.0
                self.state = "flash"
            
            pts_left = self.get_points(self.progress, is_left=True)
            pts_right = self.get_points(self.progress, is_left=False)
            
            self.canvas.coords(self.left_line, *pts_left)
            self.canvas.coords(self.right_line, *pts_right)
            
            self.after(16, self.animate)
            
        elif self.state == "flash":
            self.flash_count += 1
            if self.flash_count % 2 == 1:
                self.canvas.itemconfig(self.left_line, fill='white', width=3)
                self.canvas.itemconfig(self.right_line, fill='white', width=3)
            else:
                self.canvas.itemconfig(self.left_line, fill='#00ffcc', width=2)
                self.canvas.itemconfig(self.right_line, fill='#00ffcc', width=2)
                
            if self.flash_count >= 6:
                self.state = "fade"
            self.after(80, self.animate)
            
        elif self.state == "fade":
            self.fade_alpha -= 0.05
            if self.fade_alpha <= 0:
                self.destroy()
            else:
                self.attributes('-alpha', self.fade_alpha)
                self.after(30, self.animate)

def play_effect():
    app = ScreenEffect()
    app.mainloop()

def trigger_effect():
    # Run in a separate thread so it doesn't block the main app
    t = threading.Thread(target=play_effect, daemon=True)
    t.start()

if __name__ == '__main__':
    play_effect()
