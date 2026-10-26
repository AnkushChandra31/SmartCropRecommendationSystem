"""Simple message-box helper functions."""

from tkinter import messagebox


def show_input_error():
    messagebox.showerror("Invalid Input", "Please enter valid numbers in all fields.")
