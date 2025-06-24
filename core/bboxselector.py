import tkinter as tk
import PIL
import PIL.ImageTk

class BboxSelector():
    def select(self, img, bboxes, thickness=1, active_thickness=3, padding=2):
        self._root = tk.Tk()
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)
        self._root.lift()

        self._canvas = tk.Canvas(width=self._root.winfo_screenwidth(), height=self._root.winfo_screenheight(), bg="gray", bd=0, highlightthickness=0)
        self._canvas.pack()
        
        bg_img = img.point(lambda pxl: pxl * 0.75)
        self._bg_img = PIL.ImageTk.PhotoImage(bg_img)
        self._canvas.create_image(0, 0, image=self._bg_img, anchor="nw")

        self._bboxes = bboxes
        self._bbox = [-1, -1, -1, -1] # Crop area presented as x1, y1, x2, y2
        self._rects = {}
        self._canvas.bind("<Motion>", self._handle_motion)
        self._canvas.bind("<Button-1>", self._handle_button)
        self._canvas.bind("<ButtonRelease-1>", self._handle_button_release)

        self.padding = padding
        self.thickness = thickness
        self.active_thickness = active_thickness

        self._draw_bboxes()
        self._root.mainloop()

    def _handle_motion(self, e):
        for i, bbox in enumerate(self._bboxes):
            self._canvas.itemconfig(self._rects[i], width=self.thickness)

            if (bbox[0] <= e.x <= bbox[2]) and (bbox[1] <= e.y <= bbox[3]):
                self._canvas.itemconfig(self._rects[i], width=self.active_thickness)

    def _handle_button(self, e):
        for i, bbox in enumerate(self._bboxes):
            if (bbox[0] <= e.x <= bbox[2]) and (bbox[1] <= e.y <= bbox[3]):
                self._canvas.itemconfig(self._rects[i], width=self.active_thickness-1)

    def _handle_button_release(self, e):
        for i in self._bboxes:
            if (i[0] <= e.x <= i[2]) and (i[1] <= e.y <= i[3]):
                self._bbox = i
                self._root.destroy()
                break

    def _draw_bboxes(self):
        for i, bbox in enumerate(self._bboxes):
            self._rects[i] = self._canvas.create_rectangle(bbox, outline="#f0f0f0", width=self.thickness)

    def get_bbox(self):
        xmin = min(self._bbox[0], self._bbox[2])
        xmax = max(self._bbox[0], self._bbox[2])
        ymin = min(self._bbox[1], self._bbox[3])
        ymax = max(self._bbox[1], self._bbox[3])
        bbox = [ xmin, ymin, xmax, ymax ]
        return bbox
