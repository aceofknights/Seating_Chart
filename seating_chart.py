import tkinter as tk
from tkinter import messagebox, simpledialog
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

            # Header with table name and controls for renaming and deleting the table
            header_frame = tk.Frame(table_frame)
            header_frame.pack()

            table_label = tk.Label(
                header_frame, text=f"{table['name']} (Seats: {table['seats']})"
            )
            table_label.pack(side="left")

            rename_button = tk.Button(
                header_frame,
                text="Rename",
                command=lambda t=table: self.rename_table(t),
            )
            rename_button.pack(side="left")

            delete_button = tk.Button(
                header_frame,
                text="Delete",
                command=lambda t=table: self.delete_table(t),
            )
            delete_button.pack(side="left")

            # Seat controls for each seat in the table
            for i in range(table["seats"]):
                seat_frame = tk.Frame(table_frame)
                seat_frame.pack()

                student_label = tk.Label(seat_frame, text=f"Seat {i + 1}:")
                student_label.pack(side="left")

                # Student entry field with StringVar to bind to the table seat
                student_name = tk.StringVar(
                    value=table["students"][i] if table["students"][i] else ""
                )
                student_entry = tk.Entry(
                    seat_frame, textvariable=student_name, width=20
                )

                # Lock indicator
                if table["locked"][i]:  # Locked seats are visually distinct
                    student_entry.config(state="disabled", bg="lightgray")
                else:
                    student_entry.config(bg="white")

                student_entry.pack(side="left")

                # Lock button to lock and save the student in this seat
                lock_button = tk.Button(
                    seat_frame,
                    text="Lock" if not table["locked"][i] else "Unlock",
                    command=lambda t=table, idx=i, entry=student_entry: self.toggle_lock(
                        t, idx, entry
                    ),
                )
                lock_button.pack(side="left")

            # Add and Remove seat buttons
            seat_control_frame = tk.Frame(table_frame)
            seat_control_frame.pack()

            add_seat_button = tk.Button(
                seat_control_frame,
                text="Add Seat",
                command=lambda t=table: self.add_seat(t),
            )
            add_seat_button.pack(side="left")

            remove_seat_button = tk.Button(
                seat_control_frame,
                text="Remove Seat",
                command=lambda t=table: self.remove_seat(t),
            )
            remove_seat_button.pack(side="left")

    def toggle_lock(self, table, seat_index, entry):
        if table["locked"][seat_index]:
            # Unlock the seat
            table["locked"][seat_index] = False
            entry.config(state="normal", bg="white")
        else:
            # Lock the seat and save the student name
            table["students"][seat_index] = entry.get()
            table["locked"][seat_index] = True
            entry.config(state="disabled", bg="lightgray")
        self.update_display()

    def add_seat(self, table):
        # Add a new seat with None as the student and unlocked
        table["seats"] += 1
        table["students"].append(None)
        table["locked"].append(False)
        self.update_display()

    def remove_seat(self, table):
        # Remove the last seat only if there are seats available
        if table["seats"] > 0:
            table["seats"] -= 1
            table["students"].pop()
            table["locked"].pop()
            self.update_display()
        else:
            messagebox.showerror("Remove Seat Error", "No seats left to remove.")

    def randomize_seats(self):
        # Get the list of student names from the input field
        student_names = self.students_entry.get().split(",")
        student_names = [name.strip() for name in student_names if name.strip()]

        if not student_names:
            messagebox.showwarning("No Students", "Please enter student names.")
            return

        # Collect only unlocked seats and corresponding names to be randomized
        unlocked_seats = []
        names_to_randomize = []

        # Separate locked and unlocked seats, and gather names for unlocked seats only
        for table in self.tables:
            for i in range(table["seats"]):
                if table["locked"][i]:  # If the seat is locked, skip it entirely
                    continue
                elif table["students"][
                    i
                ]:  # If there's an existing name in an unlocked seat, clear it
                    table["students"][i] = None
                unlocked_seats.append((table, i))  # Add unlocked seats to the list

        # Fill names_to_randomize with student_names, limited by the number of unlocked seats
        names_to_randomize = student_names[: len(unlocked_seats)]

        # Shuffle the names and assign them to unlocked seats
        random.shuffle(names_to_randomize)
        for (table, seat_index), student in zip(unlocked_seats, names_to_randomize):
            table["students"][seat_index] = student

        # Clear any remaining unlocked seats if there are extra seats
        for table, seat_index in unlocked_seats[len(names_to_randomize) :]:
            table["students"][seat_index] = None

        # Update display to reflect changes
        self.update_display()

    def rename_table(self, table):
        # Prompt for a new name
        new_name = simpledialog.askstring(
            "Rename Table", f"Enter a new name for {table['name']}:"
        )
        if new_name:
            table["name"] = new_name
            self.update_display()

    def delete_table(self, table):
        # Remove the table from the list
        self.tables.remove(table)
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
