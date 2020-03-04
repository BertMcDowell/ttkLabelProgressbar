# -*- coding: utf-8 -*-

# Copyright (c) Bert McDowell 2020
# For license see LICENSE
from threading import Thread
from threading import Condition
from threading import Lock

from tkinter import ttk
from tkinter import *

__version__ = "0.1"
__author__  = "Bert McDowell <bertmcdowell@gmail.com>"
__all__     = ["LabelProgressbar"]

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
        self._condition = Condition()
        self._lock = Lock()
        self._intervalDefault = 50 / 1000
        self._interval = self._intervalDefault

        self._frame = ttk.Frame(master=self, relief=RIDGE)
        self._frame.pack(fill=BOTH, expand=True, pady=2, padx=2)

        self._canvas = Canvas(master=self._frame)
        self._canvas.bind("<Configure>", self._configure)
        self._canvas.pack(fill=BOTH, expand=True, pady=2, padx=2)

        self._bar = self._canvas.create_rectangle(0, 0, 100, 40, fill = "lightgray")
        self._label = self._canvas.create_text(4, 4, anchor="nw", angle=0)

        self._value = kwargs.pop('value', 100)
        self._maximum = kwargs.pop('maximum', 100)
        self._step = kwargs.pop('step', 1.0)
        self._text = kwargs.pop('text', '%')

        if kwargs.pop('orient', HORIZONTAL) == HORIZONTAL:
            self._orient = HORIZONTAL
        else:
            self._orient = VERTICAL

        self._updateText()

    def _getProgress(self):
        return self._value / self._maximum

    def _updateBar(self):
        progress = self._getProgress()
        if self._orient == HORIZONTAL:
            self._canvas.coords(self._bar, 2, 2, (self._canvas.winfo_width() - 3) * progress, self._canvas.winfo_height() - 3)
        else: 
            self._canvas.coords(self._bar, 2, 2, self._canvas.winfo_width() - 3, (self._canvas.winfo_height() - 3) * progress)

    def _updateLabel(self):
        if self._orient == HORIZONTAL:
            self._canvas.coords(self._label, (self._canvas.winfo_height() - 3) * 0.5, (self._canvas.winfo_height() - 3) * 0.5)
            self._canvas.itemconfig(self._label, angle=0)
        else: 
            self._canvas.coords(self._label, (self._canvas.winfo_height() - 3) * 0.5, (self._canvas.winfo_height() - 3) * 0.5)
            self._canvas.itemconfig(self._label, angle=90)

    def _updateText(self):
        if self._text == '%':
            self._canvas.itemconfig(self._label, text='{:03d}%'.format(int(self._getProgress() * 100)))
            self._updateLabel()

    def _configure(self, event):
        self._updateBar()
        self._updateLabel()

    def _run(self):
        self._condition.acquire()
        while self._is_running:
            self.step()
            self._condition.wait(self._interval)
        self._condition.release()

    def start(self, interval=None):
        """Begin autoincrement mode: schedules a recurring timer event that calls 
           Progressbar.step() every interval milliseconds. 
           If omitted, interval defaults to 50 milliseconds."""
        if interval is not None and isinstance(interval, (int, float, complex)):
            self._interval = interval / 1000

        if not self._is_running:
            self._is_running = True
            self._timer = Thread(target=self._run)
            self._timer.start()
            self.event_generate("<<ProgressbarStart>>", data={"widget" : self})

    def step(self, amount=None):
        """Increments the progress bar’s value by amount.
            amount defaults to 1.0 if omitted."""
        self._lock.acquire()
        if amount is not None and isinstance(amount, (int, float, complex)):
            self._value += amount
        else:
            self._value += self._step
        if self._value > self._maximum:
            self._value = 0.0
        elif self._value < 0.0:
            self._value = self._maximum
        self._updateBar()
        self._updateText()
        self._lock.release()
        self.event_generate("<<ProgressbarStep>>", data={"widget" : self})

    def stop(self):
        """Stop autoincrement mode: cancels any recurring timer event initiated 
           by Progressbar.start() for this progress bar."""
        if self._timer and self._timer.is_alive():
            self._is_running = False
            try:
                self._condition.notify()
            except RuntimeError as exception:
                print(exception)
            self._timer.join(self._interval)
        self._interval = self._intervalDefault
        self._timer = None

    def set(self,text):
        self._lock.acquire()
        self._text=text
        if self._text == '%':
            self._updateText()
        else:
            self._canvas.itemconfig(self._label, text=text)
            self._updateLabel()
        self._lock.release()

    def get(self):
        return self._canvas.itemconfig(self._label, option="text")

# Test:
def _test():

    root=Tk()
    root.title("Example")
    progressbar=LabelProgressbar(root)
    progressbar.pack(fill=BOTH,expand=True, padx=2, pady=2)

    startbtn = Button(text="Start", width=30, command= lambda progressbar=progressbar: progressbar.start())
    startbtn.pack(side=RIGHT, padx=2)

    stepbtn = Button(text="Step", width=30, command= lambda progressbar=progressbar: progressbar.step())
    stepbtn.pack(side=RIGHT, padx=2)

    stopbtn = Button(text="Stop", width=30, command= lambda progressbar=progressbar: progressbar.stop())
    stopbtn.pack(side=RIGHT, padx=2)

    root.geometry('1080x1080')
    root.mainloop()

if __name__ == '__main__':
    _test()