import datetime
import sqlite3
from tkcalendar import DateEntry
from tkinter import *
import tkinter.messagebox as mb
import tkinter.ttk as ttk
from ttkthemes import ThemedStyle
from dateutil import parser
from tkinter import simpledialog


class RoundedButton(Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.config(relief=FLAT, borderwidth=0, bg="royal blue")
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.config(bg="dodger blue")

    def on_leave(self, e):
        self.config(bg="royal blue")

class ExpenseDatabase:
    def __init__(self, db_name):
        self.connector = sqlite3.connect(db_name)
        self.cursor = self.connector.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ET (
                ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                Date DATETIME,
                Payee TEXT,
                Description TEXT,
                Amount FLOAT,
                ModeOfPayment TEXT,
                Budget FLOAT
            )
        ''')
        self.connector.commit()

    def insert_expense(self, date, payee, desc, amnt, MoP):
        self.cursor.execute('''
            INSERT INTO ET (Date, Payee, Description, Amount, ModeOfPayment) VALUES (?, ?, ?, ?, ?)
        ''', (date, payee, desc, amnt, MoP))
        self.connector.commit()

    def delete_expense(self, expense_id):
        self.cursor.execute('DELETE FROM ET WHERE ID = ?', (expense_id,))
        self.connector.commit()

    def delete_all_expenses(self):
        self.cursor.execute('DROP TABLE IF EXISTS ET')
        self.connector.commit()

class ExpenseFeature:
    def __init__(self, db, gui):
        self.db = db
        self.gui = gui

    def perform(self):
        pass

class AddExpense(ExpenseFeature):
    def perform(self):
        if not self.gui.date.get() or not self.gui.payee.get() or not self.gui.desc.get() or not self.gui.amnt.get() or not self.gui.MoP.get():
            mb.showerror('Fields empty!', "Please fill all the missing fields before pressing the add button!")
        else:
            self.db.insert_expense(self.gui.date.get_date(), self.gui.payee.get(), self.gui.desc.get(), self.gui.amnt.get(), self.gui.MoP.get())
            self.gui.clear_flds()
            self.gui.list_all_exp()
            mb.showinfo('Expense added', 'The expense whose details you just entered has been added to the database')

class ViewExpenseDetails(ExpenseFeature):
    def perform(self):
        if not self.gui.table.selection():
            mb.showerror('No expense selected', 'Please select an expense from the table to view its details')
            return
        current_selected_expense = self.gui.table.item(self.gui.table.focus())
        values = current_selected_expense['values']
        expenditure_date = datetime.date(int(values[1][:4]), int(values[1][5:7]), int(values[1][8:]))
        self.gui.date.set_date(expenditure_date)
        self.gui.payee.set(values[2])
        self.gui.desc.set(values[3])
        self.gui.amnt.set(values[4])
        self.gui.MoP.set(values[5])

class ETApp:
    def __init__(self, root, db_name):
        self.root = root
        self.root.title('Expense Tracker')
        self.root.geometry('1200x550')
        self.root.resizable(0, 0)

        self.style = ThemedStyle(self.root)
        self.style.set_theme("equilux")

        self.db = ExpenseDatabase(db_name)

        self.title_label = Label(root, text='EXPENSE TRACKER', font=('Helvetica', 18, 'bold'))
        self.title_label.pack(side=TOP, fill=X)

        self.cret_widgets()

    def cret_widgets(self):
        self.desc = StringVar()
        self.amnt = DoubleVar()
        self.payee = StringVar()
        self.MoP = StringVar(value='Cash')

        self.cret_data_ent_frm()
        self.cret_btns_frm()
        self.cret_tree_frm()

    def cret_data_ent_frm(self):
        data_entry_frame = Frame(self.root)
        data_entry_frame.place(x=0, y=30, relheight=0.95, relwidth=0.25)

        Label(data_entry_frame, text='Date (M/DD/YY) :', font=('Helvetica', 10)).place(x=10, y=50)
        self.date = DateEntry(data_entry_frame, date=datetime.datetime.now().date(), font='Helvetica 10 bold')
        self.date.place(x=160, y=50)

        Label(data_entry_frame, text='Payee\t             :', font=('Helvetica', 10)).place(x=10, y=230)
        Entry(data_entry_frame, font='Helvetica 10 bold', width=31, textvariable=self.payee).place(x=10, y=260)

        Label(data_entry_frame, text='Description           :', font=('Helvetica', 10)).place(x=10, y=100)
        Entry(data_entry_frame, font='Helvetica 10 bold', width=31, textvariable=self.desc).place(x=10, y=130)

        Label(data_entry_frame, text='Amount\t             :', font=('Helvetica', 10)).place(x=10, y=180)
        Entry(data_entry_frame, font='Helvetica 10 bold', width=14, textvariable=self.amnt).place(x=160, y=180)

        Label(data_entry_frame, text='Mode of Payment:', font=('Helvetica', 10)).place(x=10, y=310)
        dd1 = OptionMenu(data_entry_frame, self.MoP, *['Cash', 'Cheque', 'Credit Card', 'Debit Card', 'Paytm', 'Google Pay', 'Razorpay'])
        dd1.place(x=160, y=305)
        dd1.configure(width=10, font='Helvetica 10 bold')

        add_button = RoundedButton(data_entry_frame, text='Add expense', command=self.add_an_exp, font=('Helvetica', 10), width=30)
        add_button.place(x=10, y=395)

        show_individual_button = RoundedButton(data_entry_frame, text='Show Individual Expense', font=('Helvetica', 10), width=30, command=self.show_indiv_exp)
        show_individual_button.place(x=10, y=495)

    def cret_btns_frm(self):
        buttons_frame = Frame(self.root)
        buttons_frame.place(relx=0.25, rely=0.05, relwidth=0.75, relheight=0.21)

        delete_button = RoundedButton(buttons_frame, text='Delete Expense', font=('Helvetica', 10), width=25, command=self.rem_exp)
        delete_button.place(x=30, y=5)
        delete_all_button = RoundedButton(buttons_frame, text='Delete All Expenses', font=('Helvetica', 10), width=25, command=self.rem_all_exp)
        delete_all_button.place(x=335, y=5)
        view_button = RoundedButton(buttons_frame, text="View Selected Expense's Details", font=('Helvetica', 10), width=25, command=self.view_exp_det)
        view_button.place(x=30, y=65)
        edit_button = RoundedButton(buttons_frame, text='Edit Selected Expense', command=self.edit_exp, font=('Helvetica', 10), width=25)
        edit_button.place(x=335, y=65)
        total_expense=RoundedButton(buttons_frame, text='Show total expense', command=self.show_total_expense, font=('Helvetica', 10), width=25)
        total_expense.place(x=640, y=65)
        set_budget=RoundedButton(buttons_frame, text='Set budget', command=self.set_budget, font=('Helvetica', 10), width=25)
        set_budget.place(x=640, y=5)

    def cret_tree_frm(self):
        tree_frame = Frame(self.root)
        tree_frame.place(relx=0.25, rely=0.26, relwidth=0.75, relheight=0.74)

        # Treeview
        self.table = ttk.Treeview(tree_frame, selectmode='browse', columns=('ID', 'Date', 'Payee', 'Description', 'Amount', 'Mode of Payment'))

        X_Scroller = Scrollbar(self.table, orient=HORIZONTAL, command=self.table.xview)
        Y_Scroller = Scrollbar(self.table, orient=VERTICAL, command=self.table.yview)
        X_Scroller.pack(side=BOTTOM, fill=X)
        Y_Scroller.pack(side=RIGHT, fill=Y)

        self.table.config(yscrollcommand=Y_Scroller.set, xscrollcommand=X_Scroller.set)

        self.table.heading('#1', text='S No.', anchor=CENTER)
        self.table.heading('#2', text='Date', anchor=CENTER)
        self.table.heading('#3', text='Payee', anchor=CENTER)
        self.table.heading('#4', text='Description', anchor=CENTER)
        self.table.heading('#5', text='Amount', anchor=CENTER)
        self.table.heading('#6', text='Mode of Payment', anchor=CENTER)

        self.table.column('#0', width=0, stretch=NO)
        self.table.column('#1', width=50, stretch=NO)
        self.table.column('#2', width=95, stretch=NO)
        self.table.column('#3', width=150, stretch=NO)
        self.table.column('#4', width=325, stretch=NO)
        self.table.column('#5', width=105, stretch=NO)
        self.table.column('#6', width=125, stretch=NO)

        self.table.place(relx=0, y=0, relheight=1, relwidth=1)

    def show_indiv_exp(self):
        input_window = Toplevel(self.root)
        input_window.title('Show Individual Expense')

        criteria_var = StringVar(value="date")
        date_radio = Radiobutton(input_window, text="Date", variable=criteria_var, value="date")
        date_radio.grid(row=0, column=0, padx=10, pady=10)
        payee_radio = Radiobutton(input_window, text="Payee", variable=criteria_var, value="payee")
        payee_radio.grid(row=1, column=0, padx=10, pady=10)
        mode_radio = Radiobutton(input_window, text="Mode of Payment", variable=criteria_var, value="mode")
        mode_radio.grid(row=2, column=0, padx=10, pady=10)
        desc_radio = Radiobutton(input_window, text="Description", variable=criteria_var, value="desc")
        desc_radio.grid(row=3, column=0, padx=10, pady=10)

        input_entry = Entry(input_window)
        input_entry.grid(row=0, column=1, padx=10, pady=10)

        search_button = Button(input_window, text="Search", command=lambda: self.show_exp_by_crit(criteria_var.get(), input_entry.get()))
        search_button.grid(row=0, column=2, padx=10, pady=10)

        def on_close():
            input_window.destroy()

        close_button = Button(input_window, text="Close", command=on_close)
        close_button.grid(row=1, column=1, padx=10, pady=10)

    def show_exp_by_crit(self, criteria, value):
        if criteria == "date":
            expenses = self.db.cursor.execute("SELECT * FROM ET WHERE Date=?", (value,))
        elif criteria == "payee":
            expenses = self.db.cursor.execute("SELECT * FROM ET WHERE Payee=?", (value,))
        elif criteria == "mode":
            expenses = self.db.cursor.execute("SELECT * FROM ET WHERE ModeOfPayment=?", (value,))
        elif criteria == "desc":
            expenses = self.db.cursor.execute("SELECT * FROM ET WHERE Description=?", (value,))

        data = expenses.fetchall()
        self.table.delete(*self.table.get_children())
        for values in data:
            self.table.insert('', END, values=values)

    def list_all_exp(self):
        self.table.delete(*self.table.get_children())
        all_data = self.db.cursor.execute('SELECT * FROM ET')
        data = all_data.fetchall()
        for values in data:
            self.table.insert('', END, values=values)

    def view_exp_det(self):
        view_expense = ViewExpenseDetails(self.db, self)
        view_expense.perform()

    def clear_flds(self):
        today_date = datetime.datetime.now().date()
        self.desc.set('')
        self.payee.set('')
        self.amnt.set(0.0)
        self.MoP.set('Cash')
        self.date.set_date(today_date)
        self.table.selection_remove(*self.table.selection())

    def rem_exp(self):
        if not self.table.selection():
            mb.showerror('No record selected!', 'Please select a record to delete!')
            return
        current_selected_expense = self.table.item(self.table.focus())
        values_selected = current_selected_expense['values']
        surety = mb.askyesno('Are you sure?', f'Are you sure that you want to delete the record of {values_selected[2]}')
        if surety:
            self.db.delete_expense(values_selected[0])
            self.list_all_exp()
            mb.showinfo('Record deleted successfully!', 'The record you wanted to delete has been deleted successfully')

    def rem_all_exp(self):
        surety = mb.askyesno('Are you sure?', 'Are you sure that you want to delete all the expense items from the database?', icon='warning')
        if surety:
            self.table.delete(*self.table.get_children())
            self.db.delete_all_expenses()
            mb.showinfo('All expenses deleted!', 'All the expenses have been deleted from the database successfully')

    def edit_exp(self):
        if not self.table.selection():
            mb.showerror('No record selected!', 'Please select a record to edit!')
            return

        current_selected_expense = self.table.item(self.table.focus())
        values_selected = current_selected_expense['values']

        id = values_selected[0]
        edited_date = values_selected[1]
        edited_payee = values_selected[2]
        edited_desc = values_selected[3]
        edited_amnt = values_selected[4]
        edited_MoP = values_selected[5]


        self.date.set_date(parser.parse(edited_date))
        self.payee.set(edited_payee)
        self.desc.set(edited_desc)
        self.amnt.set(edited_amnt)
        self.MoP.set(edited_MoP)


        self.add_button = RoundedButton(self.root, text='Edit Expense', command=self.save_edited_exp)
        self.add_button.place(x=10, y=395)

    def save_edited_exp(self):
        edited_date = self.date.get_date()
        edited_payee = self.payee.get()
        edited_desc = self.desc.get()
        edited_amnt = self.amnt.get()
        edited_MoP = self.MoP.get()

        if not edited_date or not edited_payee or not edited_desc or not edited_amnt or not edited_MoP:
            mb.showerror('Fields empty!', "Please fill all the missing fields before saving the changes!")
        else:
            if not self.table.selection():
                mb.showerror('No record selected', 'Please select a record from the table to edit!')
            else:
                current_selected_expense = self.table.item(self.table.focus())
                values = current_selected_expense['values']
                expenditure_date = values[1]
                self.db.cursor.execute('''
                    UPDATE ET SET Date = ?, Payee = ?, Description = ?, Amount = ?, ModeOfPayment = ? WHERE ID = ?
                ''', (edited_date, edited_payee, edited_desc, edited_amnt, edited_MoP, values[0]))
                self.db.connector.commit()

                self.clear_flds()
                self.list_all_exp()
                mb.showinfo('Expense edited', 'The expense details have been updated in the database')


                self.add_button.destroy()


    def add_an_exp(self):
        add_expense = AddExpense(self.db, self)
        add_expense.perform()
        self.list_all_exp()

    def show_total_expense(self):
        self.db.cursor.execute("SELECT SUM(Amount) FROM ET")
        total_expense = self.db.cursor.fetchone()[0]

        mb.showinfo("Total Monthly Expense", f"Total expense till now is: {total_expense}")


    def set_budget(self):
        self.p_name = simpledialog.askstring("Input", "Enter payee name:")
        self.setbudget = simpledialog.askfloat("Input", f"Enter budget for {self.p_name}:")

        if self.setbudget is not None:  # Check if the user provided a valid budget
            # Create a new table for budgets if it doesn't exist
            self.db.cursor.execute('''
                CREATE TABLE IF NOT EXISTS Budgets (
                    payee_id INT NOT NULL,
                    budget FLOAT NOT NULL,
                    FOREIGN KEY (payee_id) REFERENCES ET (ID)
                )
            ''')

            # Insert the budget data
            self.db.cursor.execute("INSERT INTO Budgets (payee_id, budget) VALUES ((SELECT ID FROM ET WHERE Payee = ?), ?)",
                                  (self.p_name, self.setbudget))
            self.db.connector.commit()
            mb.showinfo("Budget Set", f"Budget for {self.p_name} set to {self.setbudget}")

            

    def budget(self):
        self.p_name = simpledialog.askstring("Input", "Enter payee name:")

        if self.p_name is not None:  # Check if the user provided a valid payee name
            self.db.cursor.execute("SELECT SUM(Amount) FROM ET WHERE Payee = %s", (self.p_name,))
            P_expense = self.db.cursor.fetchone()[0]
            self.db.cursor.execute("SELECT Budget FROM ET WHERE Payee = %s", (self.p_name,))
            budget = self.db.cursor.fetchone()[0]

            if P_expense is not None and budget is not None:
                if P_expense > budget:
                    mb.showinfo("Over Budget", f"{self.p_name} is over budget by {P_expense - budget}.")
                else:
                    mb.showinfo("Budget Status", f"{self.p_name} is within budget.")
            else:
                mb.showerror("Error", "Payee or budget information not found.")

def main():
    root = Tk()
    app = ETApp(root, "ET.db")
    app.list_all_exp()
    root.mainloop()

if __name__ == '__main__':
    main()
