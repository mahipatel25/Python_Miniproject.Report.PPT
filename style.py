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
        self.root.geometry("1000x650")
        self.root.minsize(820, 560)
        self.root.configure(bg="#f3f6fb")

        self.expenses = []
        self.next_id = 1

        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.category_var = tk.StringVar(value=CATEGORIES[0])
        self.amount_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")
        self.total_var = tk.StringVar(value="₹0.00")
        self.count_var = tk.StringVar(value="0 expenses")

        self.configure_styles()
        self.build_ui()
        self.load_expenses()
        self.refresh_table()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TFrame", background="#f3f6fb"
        )
        style.configure(
            "TLabel", background="#f3f6fb",
            foreground="#25324b", font=("Segoe UI", 10)
        )
        style.configure(
            "Title.TLabel", background="#f3f6fb",
            foreground="#172b4d", font=("Segoe UI", 23, "bold")
        )
        style.configure(
            "Subtitle.TLabel", background="#f3f6fb",
            foreground="#64748b", font=("Segoe UI", 10)
        )
        style.configure(
            "Card.TLabelframe", background="#ffffff",
            bordercolor="#dbe4f0", relief="solid", borderwidth=1
        )
        style.configure(
            "Card.TLabelframe.Label", background="#ffffff",
            foreground="#243b63", font=("Segoe UI", 11, "bold")
        )
        style.configure(
            "Card.TLabel", background="#ffffff",
            foreground="#25324b", font=("Segoe UI", 10)
        )
        style.configure(
            "TEntry", padding=8, fieldbackground="#ffffff",
            foreground="#172b4d", bordercolor="#cbd5e1"
        )
        style.configure(
            "TCombobox", padding=7, fieldbackground="#ffffff",
            foreground="#172b4d"
        )
        style.configure(
            "Primary.TButton", background="#2563eb",
            foreground="#ffffff", padding=(14, 9),
            font=("Segoe UI", 10, "bold"), borderwidth=0
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#1d4ed8"), ("pressed", "#1e40af")],
            foreground=[("disabled", "#e2e8f0")]
        )
        style.configure(
            "Secondary.TButton", background="#e8eef8",
            foreground="#25416b", padding=(12, 8),
            font=("Segoe UI", 9, "bold"), borderwidth=0
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#d8e4f5")]
        )
        style.configure(
            "Danger.TButton", background="#fee2e2",
            foreground="#b91c1c", padding=(12, 8),
            font=("Segoe UI", 9, "bold"), borderwidth=0
        )
        style.map(
            "Danger.TButton",
            background=[("active", "#fecaca")]
        )
        style.configure(
            "Treeview", background="#ffffff",
            fieldbackground="#ffffff", foreground="#25324b",
            rowheight=34, font=("Segoe UI", 10),
            bordercolor="#e2e8f0", borderwidth=0
        )
        style.configure(
            "Treeview.Heading", background="#eaf0f9",
            foreground="#334b70", font=("Segoe UI", 9, "bold"),
            padding=10, relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#1e3a8a")]
        )

    def build_ui(self):
        page = ttk.Frame(self.root, padding=(22, 18))
        page.pack(fill="both", expand=True)

        header = ttk.Frame(page)
        header.pack(fill="x", pady=(0, 18))

        title_area = ttk.Frame(header)
        title_area.pack(side="left", fill="x", expand=True)

        ttk.Label(
            title_area, text="Personal Expense Tracker",
            style="Title.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            title_area,
            text="Keep track of your spending, one expense at a time.",
            style="Subtitle.TLabel"
        ).pack(anchor="w", pady=(4, 0))

        total_card = tk.Frame(
            header, bg="#dbeafe", highlightbackground="#bfdbfe",
            highlightthickness=1, padx=18, pady=12
        )
        total_card.pack(side="right", padx=(12, 0))
        tk.Label(
            total_card, text="TOTAL SPENDING",
            bg="#dbeafe", fg="#1d4ed8",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="e")
        tk.Label(
            total_card, textvariable=self.total_var,
            bg="#dbeafe", fg="#1e3a8a",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor="e", pady=(3, 0))

        form = ttk.LabelFrame(
            page, text="  Add a new expense  ",
            style="Card.TLabelframe", padding=(16, 14)
        )
        form.pack(fill="x", pady=(0, 16))

        # Use a 12-column grid so the amount field stays compact while
        # the description field gets more space. Every label sits directly
        # above its own input, with consistent padding and alignment.
        form.columnconfigure(0, weight=2, uniform="expense_fields")
        form.columnconfigure(1, weight=2, uniform="expense_fields")
        form.columnconfigure(2, weight=1, uniform="expense_fields")
        form.columnconfigure(3, weight=4, uniform="expense_fields")

        fields = [
            ("Date (YYYY-MM-DD)", self.date_var, "entry"),
            ("Category", self.category_var, "category"),
            ("Amount (₹)", self.amount_var, "amount"),
            ("Description", self.description_var, "entry"),
        ]

        for col, (label, variable, kind) in enumerate(fields):
            ttk.Label(form, text=label, style="Card.TLabel").grid(
                row=0, column=col, sticky="w", padx=8, pady=(0, 7)
            )
            if kind == "category":
                widget = ttk.Combobox(
                    form, textvariable=variable, values=CATEGORIES,
                    state="readonly", style="TCombobox"
                )
            else:
                widget = ttk.Entry(
                    form, textvariable=variable, style="TEntry",
                    justify="right" if kind == "amount" else "left"
                )
            widget.grid(
                row=1, column=col, sticky="ew", padx=8, pady=(0, 12),
                ipady=2
            )

        ttk.Button(
            form, text="+  Add Expense", style="Primary.TButton",
            command=self.add_expense
        ).grid(row=2, column=0, columnspan=4, sticky="ew", padx=8, pady=(3, 0))

        toolbar = ttk.Frame(page)
        toolbar.pack(fill="x", pady=(0, 9))

        ttk.Label(
            toolbar, text="Your transactions",
            font=("Segoe UI", 13, "bold")
        ).pack(side="left")

        ttk.Label(toolbar, text="Filter:", style="Subtitle.TLabel").pack(
            side="right", padx=(10, 6)
        )
        filter_box = ttk.Combobox(
            toolbar, textvariable=self.filter_var,
            values=["All"] + CATEGORIES, state="readonly", width=15
        )
        filter_box.pack(side="right")
        filter_box.bind(
            "<<ComboboxSelected>>", lambda _event: self.refresh_table()
        )

        table_card = tk.Frame(
            page, bg="#ffffff", highlightbackground="#dbe4f0",
            highlightthickness=1
        )
        table_card.pack(fill="both", expand=True)

        columns = ("date", "category", "amount", "description")
        table_area = ttk.Frame(table_card)
        table_area.pack(fill="both", expand=True, padx=1, pady=1)

        self.tree = ttk.Treeview(
            table_area, columns=columns, show="headings",
            selectmode="browse"
        )
        self.tree.heading("date", text="DATE", anchor="center")
        self.tree.heading("category", text="CATEGORY", anchor="center")
        self.tree.heading("amount", text="AMOUNT (₹)", anchor="center")
        self.tree.heading("description", text="DESCRIPTION", anchor="center")
        self.tree.column("date", width=150, minwidth=150, anchor="center", stretch=False)
        self.tree.column("category", width=170, minwidth=170, anchor="center", stretch=False)
        self.tree.column("amount", width=190, minwidth=190, anchor="center", stretch=False)
        self.tree.column("description", width=420, minwidth=250, anchor="center", stretch=True)

        scrollbar = ttk.Scrollbar(
            table_area, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd", background="#f7faff")

        bottom = ttk.Frame(page)
        bottom.pack(fill="x", pady=(12, 0))

        ttk.Label(
            bottom, textvariable=self.count_var,
            style="Subtitle.TLabel"
        ).pack(side="left")

        ttk.Button(
            bottom, text="Delete Selected",
            style="Danger.TButton", command=self.delete_selected
        ).pack(side="right")
        ttk.Button(
            bottom, text="Show All",
            style="Secondary.TButton", command=self.show_all
        ).pack(side="right", padx=(0, 8))

    def add_expense(self):
        expense_date = self.date_var.get().strip()
        category = self.category_var.get().strip()
        amount_text = self.amount_var.get().strip()
        description = self.description_var.get().strip()

        try:
            parsed_date = date.fromisoformat(expense_date)
            if parsed_date.isoformat() != expense_date:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid date", "Enter a valid date in YYYY-MM-DD format."
            )
            return

        try:
            amount = float(amount_text)
            if not (0 < amount < float("inf")):
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid amount", "Enter a valid amount greater than zero."
            )
            return

        if category not in CATEGORIES:
            messagebox.showerror("Invalid category", "Please select a category.")
            return

        if not description:
            messagebox.showerror(
                "Missing description", "Please enter a description."
            )
            return

        expense = {
            "id": self.next_id,
            "date": expense_date,
            "category": category,
            "amount": amount,
            "description": description,
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
            messagebox.showinfo(
                "Select an expense", "Please select an expense to delete."
            )
            return

        if not messagebox.askyesno(
            "Confirm deletion", "Delete the selected expense?"
        ):
            return

        expense_id = int(selected[0])
        original = self.expenses[:]
        self.expenses = [
            item for item in self.expenses if item["id"] != expense_id
        ]

        if not self.save_expenses():
            self.expenses = original
            return

        self.refresh_table()

    def show_all(self):
        self.filter_var.set("All")
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

        for index, item in enumerate(visible):
            self.tree.insert(
                "", "end", iid=str(item["id"]),
                values=(
                    item["date"], item["category"],
                    f'{item["amount"]:,.2f}', item["description"]
                ),
                tags=("even" if index % 2 == 0 else "odd",)
            )

        total = sum(item["amount"] for item in visible)
        self.total_var.set(f"₹{total:,.2f}")
        self.count_var.set(
            f"{len(visible)} expense{'s' if len(visible) != 1 else ''}"
        )

    def load_expenses(self):
        if not os.path.exists(FILE_NAME):
            return

        try:
            with open(FILE_NAME, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                required = {"id", "date", "category", "amount", "description"}
                if not reader.fieldnames or not required.issubset(reader.fieldnames):
                    raise ValueError("The CSV file has an unexpected format.")

                loaded = []
                for row in reader:
                    expense_id = int(row["id"])
                    parsed_date = date.fromisoformat(row["date"])
                    amount = float(row["amount"])
                    category = row["category"]
                    description = row["description"]

                    if (
                        expense_id < 1
                        or not (0 < amount < float("inf"))
                        or category not in CATEGORIES
                        or not description.strip()
                    ):
                        raise ValueError("The CSV file contains invalid data.")

                    loaded.append({
                        "id": expense_id,
                        "date": parsed_date.isoformat(),
                        "category": category,
                        "amount": amount,
                        "description": description,
                    })

                self.expenses = loaded
                self.next_id = max(
                    (item["id"] for item in loaded), default=0
                ) + 1
        except (OSError, csv.Error, ValueError, KeyError) as error:
            messagebox.showerror(
                "Could not load expenses",
                f"Could not read expenses.csv:\n{error}\n"
                "The existing file has not been overwritten."
            )
            self.expenses = []
            self.next_id = 1

    def save_expenses(self):
        temp_name = FILE_NAME + ".tmp"
        fields = ["id", "date", "category", "amount", "description"]

        try:
            with open(temp_name, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=fields)
                writer.writeheader()
                writer.writerows(self.expenses)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temp_name, FILE_NAME)
            return True
        except OSError as error:
            try:
                if os.path.exists(temp_name):
                    os.remove(temp_name)
            except OSError:
                pass
            messagebox.showerror(
                "Save failed",
                f"Could not save expenses:\n{error}\n"
                "Check folder permissions and available disk space."
            )
            return False


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
