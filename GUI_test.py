import tkinter as tk
from tkinter import simpledialog, messagebox
import speech_recognition as sr

# Create the main window
root = tk.Tk()
root.title("Object and Action Input")

def speech_to_text_object():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        messagebox.showinfo("Listening", "Please say the name of the object...")
        audio = recognizer.listen(source)

    try:
        object_name = recognizer.recognize_google(audio)
        object_entry.delete(0, tk.END)
        object_entry.insert(0, object_name)
        messagebox.showinfo("Recognized", f"Recognized object: {object_name}")
    except sr.UnknownValueError:
        messagebox.showwarning("Error", "Could not understand the audio.")
    except sr.RequestError as e:
        messagebox.showwarning("Error", f"Could not request results; {e}")

# Function to handle speech-to-text for action
def speech_to_text_action(object_name):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        messagebox.showinfo("Listening", f"Please say the action for '{object_name}'...")
        audio = recognizer.listen(source)

    try:
        action = recognizer.recognize_google(audio)
        messagebox.showinfo("Action", f"You have chosen to '{action}' the '{object_name}'.")
    except sr.UnknownValueError:
        messagebox.showwarning("Error", "Could not understand the audio.")
    except sr.RequestError as e:
        messagebox.showwarning("Error", f"Could not request results; {e}")

# Function to handle the Enter button click
def enter_object():
    object_name = object_entry.get()
    if object_name:
        action = simpledialog.askstring("Input", f"What action would you like to perform with {object_name}?")
        if action:
            messagebox.showinfo("Action", f"You have chosen to '{action}' the '{object_name}'.")
        else:
            messagebox.showwarning("No Action", "No action was entered.")
    else:
        messagebox.showwarning("No Object", "No object name was entered.")

# Create and pack the widgets
label = tk.Label(root, text="Enter the name of an object:")
label.pack(pady=10)

object_entry = tk.Entry(root, width=50)
object_entry.pack(pady=5)

enter_button = tk.Button(root, text="Enter", command=enter_object)
enter_button.pack(pady=10)

speech_button = tk.Button(root, text="Use Speech for Object", command=speech_to_text_object)
speech_button.pack(pady=10)

# Run the application
root.mainloop()