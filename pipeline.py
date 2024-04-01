from functions import sleep_if, copy_if_missing, google_copy, run_catgt, generate_file_lists, pi_process, prep_phy, \
    copy_phy_output
import os
import shutil
import pandas as pd
import numpy as np
from time import sleep
from file_paths import root_file_paths
import tkinter as tk
import tkinter.font as font
from threading import Thread

halt = False


class PipelineStop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("300x200")
        self.root.title('Pipeline')
        my_font = font.Font(size=16)
        self.button = tk.Button(
            master=self.root,
            text='Stop Pipeline Smoothly',
            font=my_font,
            width=40,
            height=12,
            bg="white",
            fg="black",
            command=self.halt)
        self.button.pack()
        self.root.mainloop()

    def halt(self):
        global halt
        halt = True
        self.root.destroy()


def check_halt():
    global halt
    if halt:
        print('Stopped pipeline via button')
        raise Exception('Stopped pipeline via button')


def run_pipeline():
    sleepy = True
    if not sleepy:
        t1 = Thread(target=PipelineStop)
        t1.start()

    step_list = [
        copy_if_missing,  # Copies files to external drive if they haven't already
        # google_copy,  # Copies files to google cloud if they haven't already
        run_catgt,  # Runs CatGT on any new sessions
        # pi_process,  # Processed the pi files and generally finishes the dataset after sorting
        copy_phy_output,  # Copies data post manual curation to external drive and to a backup folder
        prep_phy,  # Gets raw data ready for manual curation
    ]
    while True:
        for step in step_list:
            sleep_if(sleepy)
            print(f'starting {step.__name__}')
            step()
            check_halt()
        sleep(10)


if __name__ == '__main__':
    run_pipeline()
