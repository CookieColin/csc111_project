import decision_tree
import tkinter as tk

root = tk.Tk()
root.title("Movie Rec System")

lbl = tk.Label(root, text="label 1")
lbl.grid(row=0, column=0)


def on_click():
    #print('clicked!')
    lbl.config(text="button clicked")


btn = tk.Button(root, text="button 1", command=on_click)
btn.grid(row=1, column=1)

root.mainloop()
