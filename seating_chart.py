import tkinter as tk
from tkinter import messagebox
import random
import pickle
from typing import List, Dict


class SeatingChart:
    def __init__(self, root):
        self.root = root
        self.root.title("Seating Chart")

        self.tables = []  # Stores tables with seats and students

        # UI for adding tables
        self.table_name_label = tk.Label(root, text="Table Name:")
        self.table_name_label.pack()
        self.table_name_entry = tk.Entry(root)
        self.table_name_entry.pack()

        self.table_seats_label = tk.Label(root, text="Number of Seats:")
        self.table_seats_label.pack()
        self.table_seats_entry = tk.Entry(root)
        self.table_seats_entry.pack()

        self.add_table_button = tk.Button(
            root, text="Add Table", command=self.add_table
        )
        self.add_table_button.pack()

        # UI for students and randomization
        self.students_entry = tk.Entry(root)
        self.students_entry.pack()
        self.students_entry.insert(0, "Enter student names (comma-separated)")

        self.randomize_button = tk.Button(
            root, text="Randomize Seats", command=self.randomize_seats
        )
        self.randomize_button.pack()

        self.save_button = tk.Button(root, text="Save Setup", command=self.save_setup)
        self.save_button.pack()

        self.load_button = tk.Button(root, text="Load Setup", command=self.load_setup)
        self.load_button.pack()

        # Display Area for tables and seating
        self.tables_frame = tk.Frame(root)
        self.tables_frame.pack()

    def add_table(self):
        table_name = self.table_name_entry.get()
        try:
            num_seats = int(self.table_seats_entry.get())
            if not table_name:
                raise ValueError("Table name cannot be empty")
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            return

        # Create a new table with seats and an empty list of students and locked status
        table = {
            "name": table_name,
            "seats": num_seats,
            "students": [None] * num_seats,  # Initialize seats as empty
            "locked": [False] * num_seats,  # Lock status of each seat
        }
        self.tables.append(table)
        self.update_display()

    def update_display(self):
        # Clear the display frame and redisplay all tables and seating arrangements
        for widget in self.tables_frame.winfo_children():
            widget.destroy()

        for table in self.tables:
            table_frame = tk.Frame(self.tables_frame)
            table_frame.pack(pady=10)

            table_label = tk.Label(
                table_frame, text=f"{table['name']} (Seats: {table['seats']})"
            )
            table_label.pack()

            for i in range(table["seats"]):
                seat_frame = tk.Frame(table_frame)
                seat_frame.pack()

                student_label = tk.Label(seat_frame, text=f"Seat {i + 1}:")
                student_label.pack(side="left")

                student_name = tk.StringVar(
                    value=table["students"][i] if table["students"][i] else ""
                )
                student_entry = tk.Entry(
                    seat_frame, textvariable=student_name, width=20
                )
                student_entry.pack(side="left")
                student_entry.bind(
                    "<FocusOut>",
                    lambda e, t=table, idx=i: self.update_student_name(
                        t, idx, student_entry.get()
                    ),
                )

                lock_var = tk.BooleanVar(value=table["locked"][i])
                lock_checkbox = tk.Checkbutton(
                    seat_frame,
                    text="Lock",
                    variable=lock_var,
                    command=lambda t=table, idx=i, var=lock_var: self.update_lock_status(
                        t, idx, var.get()
                    ),
                )
                lock_checkbox.pack(side="left")

    def update_student_name(self, table, seat_index, name):
        table["students"][seat_index] = name

    def update_lock_status(self, table, seat_index, is_locked):
        table["locked"][seat_index] = is_locked

    def randomize_seats(self):
        for table in self.tables:
            unlocked_students = [
                student
                for i, student in enumerate(table["students"])
                if student and not table["locked"][i]
            ]
            random.shuffle(unlocked_students)

            # Reassign only unlocked seats
            for i in range(table["seats"]):
                if not table["locked"][i] and unlocked_students:
                    table["students"][i] = unlocked_students.pop(0)

        self.update_display()

    def save_setup(self):
        with open("seating_chart.pkl", "wb") as file:
            pickle.dump(self.tables, file)
        messagebox.showinfo("Save Setup", "Seating chart saved successfully.")

    def load_setup(self):
        try:
            with open("seating_chart.pkl", "rb") as file:
                self.tables = pickle.load(file)
            self.update_display()
            messagebox.showinfo("Load Setup", "Seating chart loaded successfully.")
        except FileNotFoundError:
            messagebox.showerror("Load Error", "No saved setup found.")


# Run the GUI application
root = tk.Tk()
app = SeatingChart(root)
root.mainloop()
