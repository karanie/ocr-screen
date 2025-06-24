import tkinter as tk
import PIL
import PIL.ImageTk

class BboxGrabber():
    def grab(self, img):
        self._root = tk.Tk()
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.lift()

        self._canvas = tk.Canvas(width=self._root.winfo_screenwidth(), height=self._root.winfo_screenheight(), bg="gray", bd=0, highlightthickness=0)
        self._canvas.pack()
        
        bg_img = img.point(lambda pxl: pxl * 0.75)
        self._bg_img = PIL.ImageTk.PhotoImage(bg_img)
        self._canvas.create_image(0, 0, image=self._bg_img, anchor="nw")

        self._bbox = [-1, -1, -1, -1] # Crop area presented as x1, y1, x2, y2
        self._canvas.bind("<Button-1>", self._handle_button)
        self._canvas.bind("<Motion>", self._handle_motion)
        self._canvas.bind("<ButtonRelease-1>", self._handle_button_release)

        self._root.mainloop()

    def _handle_button(self, e):
        p1 = self._bbox[0:2]
        if p1[0] + p1[1] < 0: # if first point hasn't been set
            self._bbox[0:2] = [e.x, e.y]
            self._rect = self._canvas.create_rectangle([*self._bbox[0:2], e.x, e.y], outline="#f0f0f0", width=2)

    def _handle_motion(self, e):
        p1 = self._bbox[0:2]
        if p1[0] + p1[1] >= 0: # if first point has been set
            self._canvas.coords(self._rect, *self._bbox[0:2], e.x, e.y)

    def _handle_button_release(self, e):
        self._bbox[2:4] = [e.x, e.y]
        self._root.destroy()

    def get_bbox(self):
        xmin = min(self._bbox[0], self._bbox[2])
        xmax = max(self._bbox[0], self._bbox[2])
        ymin = min(self._bbox[1], self._bbox[3])
        ymax = max(self._bbox[1], self._bbox[3])
        positive_bbox = [ xmin, ymin, xmax, ymax ]
        return positive_bbox
