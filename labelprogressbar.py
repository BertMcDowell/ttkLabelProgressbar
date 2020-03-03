# -*- coding: utf-8 -*-

# Copyright (c) Bert McDowell 2020
# For license see LICENSE
from threading import Timer

from tkinter import ttk
from tkinter import *

__version__ = "0.1"
__author__  = "Bert McDowell <bertmcdowell@gmail.com>"
__all__     = ["LabelProgressbar"]

HORIZONTAL = 'horizontal'
VERTICAL = 'vertical'

class LabelProgressbar(ttk.Frame):
    __inititialized = False
    __style = None

    def __initialize_custom_style(self):
        LabelProgressbar.__style = ttk.Style()

    def __init__(self,master=None,*args,**kwargs):
        if not LabelProgressbar.__inititialized:
            self.__initialize_custom_style()
            LabelProgressbar.__inititialized = True

        ttk.Frame.__init__(self, master, *args)

        self._is_running = False
        self._timer = None
        self._interval = .02

        self._frame = ttk.Frame(master=self, relief=RIDGE)
        self._frame.pack(fill=BOTH, expand=True, pady=2, padx=2)

        self._canvas = Canvas(master=self._frame)
        self._canvas.bind("<Configure>", self._configure)
        self._canvas.pack(fill=BOTH, expand=True, pady=2, padx=2)

        self._bar = self._canvas.create_rectangle(0, 0, 100, 40, fill = "lightgray")
        self._label = self._canvas.create_text(4, 4, anchor="nw", angle=0)

        if kwargs.pop('orient', HORIZONTAL) == HORIZONTAL:
            self._orient = HORIZONTAL
        else:
            self._orient = VERTICAL

        self._progress = 0
        self._length = kwargs.pop('length', 100)
        self._step = kwargs.pop('step', 1)

    def _getProgress(self):
        return self._progress / self._length

    def _update(self):
        progress = self._getProgress()
        if self._orient == HORIZONTAL:
            self._canvas.coords(self._bar, 2, 2, (self._canvas.winfo_width() - 3) * progress, self._canvas.winfo_height() - 3)
            self._canvas.coords(self._label, 4, (self._canvas.winfo_height() - 3) * 0.5)
        else: 
            self._canvas.coords(self._bar, 2, 2, self._canvas.winfo_width() - 3, (self._canvas.winfo_height() - 3) * progress)

    def _configure(self, event):
        self._update()

    def _run(self):
        if self.is_running:
            self._progress = (self._progress + self._step) % self._length
            self._update()

            self._timer = Timer(self._interval, self._run)
            self._timer.start()
        else:
            self._timer = None

    def start(self):
        if not self._is_running:
            self._timer = Timer(self._interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._is_running = False

    def set(self,text):
        self._canvas.itemconfig(self._label, text=text)
        self._update()


# Test:
def _test():

    root=Tk()
    root.title("Example")
    progressbar=LabelProgressbar(root)
    progressbar.set("Text")
    progressbar.pack(fill=BOTH,expand=True, padx=2, pady=2)

    progressbar.start()

    root.geometry('1080x1080')
    root.mainloop()

if __name__ == '__main__':
    _test()