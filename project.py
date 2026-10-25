import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

FILE_NAME = "expenses.csv"

CATEGORIES = [
    "Food", "Travel", "Shopping", "Bills",
    "Education", "Health", "Entertainment", "Other"
]


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Expense Tracker")
        self.root.geometry("850x550")

        self.expenses = []
        self.next_id = 1

        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.category_var = tk.StringVar(value="Food")
        self.amount_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")
        self.total_var = tk.StringVar()

        self.build_ui()
        self.load_expenses()
        self.refresh_table()

    def build_ui(self):
        ttk.Label(
            self.root,
            text="Personal Expense Tracker",
            font=("Arial", 20, "bold")
        ).pack(pady=12)

        form = ttk.LabelFrame(
            self.root, text="Add Expense", padding=10
        )
        form.pack(fill="x", padx=15, pady=8)

        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(
            row=0, column=0, padx=5, pady=5
        )
        ttk.Entry(
            form, textvariable=self.date_var, width=18
        ).grid(row=1, column=0, padx=5, pady=5)

        ttk.Label(form, text="Category").grid(
            row=0, column=1, padx=5, pady=5
        )
        ttk.Combobox(
            form,
            textvariable=self.category_var,
            values=CATEGORIES,
            state="readonly",
            width=16
        ).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Amount (₹)").grid(
            row=0, column=2, padx=5, pady=5
        )
        ttk.Entry(
            form, textvariable=self.amount_var, width=18
        ).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(form, text="Description").grid(
            row=0, column=3, padx=5, pady=5
        )
        ttk.Entry(
            form, textvariable=self.description_var, width=22
        ).grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(
            form, text="Add Expense", command=self.add_expense
        ).grid(row=2, column=0, columnspan=4, pady=10)

        controls = ttk.Frame(self.root)
        controls.pack(fill="x", padx=15, pady=5)

        ttk.Label(
            controls, text="Filter:"
        ).pack(side="left", padx=5)

        filter_box = ttk.Combobox(
            controls,
            textvariable=self.filter_var,
            values=["All"] + CATEGORIES,
            state="readonly",
            width=16
        )
        filter_box.pack(side="left")
        filter_box.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_table()
        )

        ttk.Button(
            controls,
            text="Delete Selected",
            command=self.delete_selected
        ).pack(side="right", padx=5)

        columns = (
            "date", "category", "amount", "description"
        )

        self.tree = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("date", text="Date")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount (₹)")
        self.tree.heading("description", text="Description")

        self.tree.column("date", width=120, anchor="center")
        self.tree.column("category", width=140, anchor="center")
        self.tree.column("amount", width=130, anchor="e")
        self.tree.column("description", width=350)

        self.tree.pack(
            fill="both", expand=True, padx=15, pady=10
        )

        ttk.Label(
            self.root,
            textvariable=self.total_var,
            font=("Arial", 12, "bold")
        ).pack(pady=10)

    def add_expense(self):
        expense_date = self.date_var.get().strip()
        category = self.category_var.get()
        description = self.description_var.get().strip()

        try:
            parsed_date = date.fromisoformat(expense_date)
            if parsed_date.isoformat() != expense_date:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error", "Enter date as YYYY-MM-DD."
            )
            return

        try:
            amount = float(self.amount_var.get())
            if not (0 < amount < float("inf")):
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error", "Enter a valid positive amount."
            )
            return

        if not description:
            messagebox.showerror(
                "Error", "Enter an expense description."
            )
            return

        expense = {
            "id": self.next_id,
            "date": expense_date,
            "category": category,
            "amount": amount,
            "description": description
        }

        self.expenses.append(expense)
        self.next_id += 1

        if not self.save_expenses():
            self.expenses.pop()
            self.next_id -= 1
            return

        self.amount_var.set("")
        self.description_var.set("")
        self.refresh_table()

    def delete_selected(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Warning", "Select an expense to delete."
            )
            return

        if not messagebox.askyesno(
            "Confirm", "Delete the selected expense?"
        ):
            return

        expense_id = int(selected[0])
        original = self.expenses[:]

        self.expenses = [
            item for item in self.expenses
            if item["id"] != expense_id
        ]

        if not self.save_expenses():
            self.expenses = original
            return

        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        selected_category = self.filter_var.get()

        visible = [
            item for item in self.expenses
            if selected_category == "All"
            or item["category"] == selected_category
        ]

        for item in visible:
            self.tree.insert(
                "",
                "end",
                iid=str(item["id"]),
                values=(
                    item["date"],
                    item["category"],
                    f'{item["amount"]:.2f}',
                    item["description"]
                )
            )

        total = sum(item["amount"] for item in visible)
        self.total_var.set(
            f"Total Expenses: ₹{total:,.2f}"
        )

    def load_expenses(self):
        if not os.path.exists(FILE_NAME):
            return

        try:
            with open(
                FILE_NAME, "r", newline="", encoding="utf-8"
            ) as file:
                reader = csv.DictReader(file)
                required = {
                    "id", "date", "category",
                    "amount", "description"
                }

                if not reader.fieldnames or not required.issubset(
                    reader.fieldnames
                ):
                    raise ValueError("Invalid CSV format.")

                loaded = []

                for row in reader:
                    amount = float(row["amount"])
                    expense_date = date.fromisoformat(row["date"])
                    expense_id = int(row["id"])

                    if (
                        expense_id < 1
                        or not (0 < amount < float("inf"))
                        or row["category"] not in CATEGORIES
                        or not row["description"].strip()
                    ):
                        raise ValueError("Invalid expense record.")

                    loaded.append({
                        "id": expense_id,
                        "date": expense_date.isoformat(),
                        "category": row["category"],
                        "amount": amount,
                        "description": row["description"]
                    })

                self.expenses = loaded
                self.next_id = max(
                    (item["id"] for item in loaded),
                    default=0
                ) + 1

        except (OSError, csv.Error, ValueError, KeyError) as error:
            messagebox.showerror(
                "Loading Error",
                f"Could not load expenses.csv:\n{error}\n"
                "The original file was not overwritten."
            )
            self.expenses = []
            self.next_id = 1

    def save_expenses(self):
        temp_file = FILE_NAME + ".tmp"
        fields = [
            "id", "date", "category",
            "amount", "description"
        ]

        try:
            with open(
                temp_file, "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.DictWriter(
                    file, fieldnames=fields
                )
                writer.writeheader()
                writer.writerows(self.expenses)
                file.flush()
                os.fsync(file.fileno())

            os.replace(temp_file, FILE_NAME)
            return True

        except OSError as error:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except OSError:
                pass

            messagebox.showerror(
                "Save Error",
                f"Could not save expenses:\n{error}"
            )
            return False


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()    