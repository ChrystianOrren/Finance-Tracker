import pandas as pd
import matplotlib.pyplot as plt
from customtkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import calendar
import datetime

class Vystar:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.data = []
        self.income = 0
        self.expenses = 0
        self.car_payment = 0
        self.subscriptions = -13.59 + -7.55 + -10 # Subject to change ( Dont want to download whole CSV for 2 transactions)
        self.fig = None
    
    def readData(self):
        self.data = pd.read_csv(self.filename)
        self.data = self.data.drop('Transaction ID', axis=1)
        self.data = self.data.drop('AccountNumber', axis=1)
        self.data = self.data.drop('AccountAliasName', axis=1)
        self.data = self.data.drop('CheckNumber', axis=1)
        self.data = self.data.drop('RunningBalance', axis=1)
        self.data = self.data.drop('Cleansed Transaction Description', axis=1)
        self.data = self.data.drop('Note', axis=1)

        # Add subscriptions (Spotify, Amazon)
        new_data = [
            {'PostingDate': '2024-07-21', 'TransactionType': 'All Debit', 'Description': 'Spotify USA', 'Amount': -13.59, 'Merchant Name': 'Spotify', 'Category': 'Entertainment'},
            {'PostingDate': '2024-07-16', 'TransactionType': 'All Debit', 'Description': 'Amazon Prime', 'Amount': -7.55, 'Merchant Name': 'Amazon', 'Category': 'Subscription'}
        ]
        new_df = pd.DataFrame(new_data)
        self.data = pd.concat([self.data, new_df], ignore_index=True)
    
    def printData(self):
        print(self.data)

    def calculateIncome(self):
        n = len(self.data)
        for i in range(n):
            if self.data.loc[i]['Category'] == 'Income' or  'ATM Deposit' in self.data.loc[i]['Description'] or 'BRANCH MESSENGER' in self.data.loc[i]['Description']:
                self.income += self.data.loc[i]['Amount']
            if "SCCU" in self.data.loc[i]['Description'] and "Payment" in self.data.loc[i]['Description']:
                self.car_payment = self.data.loc[i]['Amount']
                self.data.at[i, 'Description'] = 'Car Payment'
            if self.data.loc[i]['Merchant Name'] == 'Zelle':
                self.data.at[i, 'Description'] = 'Weed'
        self.income = round(self.income, 2)
        
    def createChart(self):
        n = len(self.data)
        days = calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]
        dates = [x+1 for x in range(days)]
        values = [0]*days

        # Fill In Data
        for i in range(n):
            if self.data.loc[i]['Category'] == 'Income' or  'ATM Deposit' in self.data.loc[i]['Description'] or 'BRANCH MESSENGER' in self.data.loc[i]['Description']:
                tmp_date = self.data.loc[i]['PostingDate'][8:]
                if tmp_date[0] == '0':
                    values[int(tmp_date[1])] = self.data.loc[i]['Amount']
                else:
                    values[int(tmp_date)] = self.data.loc[i]['Amount']

        # Create Line Graph
        plt.style.use('ggplot')
        self.fig, ax = plt.subplots(figsize=(9, 5))
        self.fig.patch.set_facecolor('#282828')
        ax.plot(dates, values, marker='o', linestyle='-', color='#7e5a9e', linewidth=3, markersize=6)  # Smaller marker size

        # Set background color
        self.fig.patch.set_facecolor('#282828')
        ax.set_facecolor('#282828')

        # Customize axis labels and title with Roboto Mono and white color
        ax.set_xlabel('Day of the Month', fontsize=12, fontweight='bold', color='white')
        ax.set_ylabel('Income', fontsize=12, fontweight='bold', color='white')
        ax.set_title('Income Throughout the Month', fontsize=14, fontweight='bold', color='white')

        # Customize tick parameters
        ax.tick_params(axis='both', which='major', labelsize=10, colors='white')

        # Ensure every day is labeled on the x-axis
        ax.set_xticks(dates)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: str(int(x))))

        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()

class USAA:
    def __init__(self, filename) -> None:
        self.filename = filename
        self.data = []
        self.expenses = 0
        self.fig = None

    def readData(self):
        self.data = pd.read_csv(self.filename)
        self.data = self.data.drop('Original Description', axis=1)

        # Filter out rows where Status is 'Declined'
        self.data = self.data[self.data['Status'] != 'Declined']

        # Reset index after dropping rows
        self.data.reset_index(drop=True, inplace=True)

    def printData(self):
        print(self.data)

    def calculateExpenses(self):
        n = len(self.data)
        for i in range(n):
            if self.data.loc[i]['Amount'] < 0:
                continue
            self.expenses += self.data.loc[i]['Amount']
        self.expenses = round(self.expenses, 2)

    def createExpensePieChart(self):
        values = []
        pieLabels = []
        n = len(self.data)

        for i in range(n):
            if self.data.loc[i]['Amount'] < 0: # ignore credit card payments
                continue
            if self.data.loc[i]['Status'] != 'Declined':
                if self.data.loc[i]['Category'] not in pieLabels:
                    pieLabels.append(self.data.loc[i]['Category'])
                    values.append(self.data.loc[i]['Amount'])
                else:
                    x = pieLabels.index(self.data.loc[i]['Category'])
                    values[x] += self.data.loc[i]['Amount']
        
        # Create pie chart
        self.fig = plt.figure(figsize=(10, 6))
        self.fig.patch.set_facecolor('#282828')
        patches, texts = plt.pie(values, startangle=90, shadow=True)
        
        # Create legend labels with category names and values
        legend_labels = [f"{category}: ${value:.2f}" for category, value in zip(pieLabels, values)]
        
        # Add legend
        plt.legend(patches, legend_labels, loc="best")
        

class GUI:
    def __init__(self, vystar, usaa) -> None:
        self.v = vystar
        self.u = usaa

        self.app = CTk(fg_color="#121212")
        self.app.state('zoomed')
        self.app.title("Chrystian's Finances")

        # Configure rows and columns
        self.app.rowconfigure(0, weight=1)
        self.app.columnconfigure([0, 1], weight=1)

        self.create_frames()

        self.create_title_labels()

        self.create_scrollable_frames()

        self.fill_scrollable_frames()

        self.create_charts()

        self.app.update()
        self.app.mainloop()

    def create_charts(self):
        # USAA CHART
        self.chart_canvas1 = FigureCanvasTkAgg(self.u.fig, master=self.left_frame)
        self.chart_canvas1.get_tk_widget().grid(row=3, column=0, pady=(0,5), padx=20, sticky='n')

        # Vystar Chart
        self.chart_canvas2 = FigureCanvasTkAgg(self.v.fig, master=self.right_frame)
        self.chart_canvas2.get_tk_widget().grid(row=3, column=0, pady=(10,10), padx=(10,10), sticky='n')

    def fill_scrollable_frames(self):
        font_size = 20
        text_color = '#fff'
        # USAA Frame
        for i in range(len(self.u.data)):
            self.transaction_date = CTkLabel(
                master=self.left_scrollable,
                text= self.u.data.iloc[i]['Date'],
                font=('Roboto Mono Bold', font_size),
                text_color=text_color
            )
            self.transaction_date.grid(row=i, column=0, pady=(10,0), padx=(10,10), sticky='n')
            self.transaction_amount = CTkLabel(
                master=self.left_scrollable,
                text= self.u.data.iloc[i]['Amount'],
                font=('Roboto Mono Bold', font_size),
                text_color=text_color
            )
            self.transaction_amount.grid(row=i, column=1, pady=(10,0), padx=(10,10), sticky='n')
            self.transaction_desc = CTkLabel(
                master=self.left_scrollable,
                text= self.u.data.iloc[i]['Description'],
                font=('Roboto Mono Bold', font_size),
                text_color=text_color
            )
            self.transaction_desc.grid(row=i, column=2, pady=(10,0), padx=(10,10), sticky='n')

        # Vystar Frame
        for i in range(len(self.v.data)):
            self.transaction_date = CTkLabel(
                master=self.right_scrollable,
                text= self.v.data.iloc[i]['PostingDate'],
                font=('Roboto Mono Bold', font_size),
                text_color=text_color
            )
            self.transaction_date.grid(row=i, column=0, pady=(10,0), padx=(10,10), sticky='n')
            self.transaction_amount = CTkLabel(
                master=self.right_scrollable,
                text= self.v.data.iloc[i]['Amount'],
                font=('Roboto Mono Bold', font_size),
                text_color=text_color
            )
            self.transaction_amount.grid(row=i, column=1, pady=(10,0), padx=(10,10), sticky='n')
            self.transaction_desc = CTkLabel(
                master=self.right_scrollable,
                text= self.v.data.iloc[i]['Description'][:20],
                font=('Roboto Mono Bold', font_size),
                text_color=text_color
            )
            self.transaction_desc.grid(row=i, column=2, pady=(10,0), padx=(10,10), sticky='n')

    def create_scrollable_frames(self):
        bg_color = "#3f3f3f"

        # Scrollable List of transactions
        self.left_scrollable = CTkScrollableFrame(
            master=self.left_frame,
            width=800,
            height=200,
            fg_color = bg_color,
            
        )
        self.right_scrollable = CTkScrollableFrame(
            master=self.right_frame,
            width=800,
            height=200,
            fg_color = bg_color,

        )
        
        self.left_scrollable.rowconfigure(0,weight=1)
        self.left_scrollable.columnconfigure([0,1,2], weight=1)
        self.right_scrollable.rowconfigure(0,weight=1)
        self.right_scrollable.columnconfigure([0,1,2], weight=1)

        self.left_scrollable.grid(row=1, column=0, pady=(40,0), padx=(10,10), sticky='n')
        self.right_scrollable.grid(row=1, column=0, pady=(0,0), padx=(30,30), sticky='n')

    def create_frames(self):
        bg_color = "#282828"
        brdr_color = "#592E83"
        brdr_width = 3
        brdr_radius = 20

        # Two frames 
        self.left_frame = CTkFrame(
            master=self.app,
            border_color=brdr_color, 
            border_width=brdr_width, 
            corner_radius=brdr_radius,
            fg_color=bg_color
        )
        self.right_frame = CTkFrame(
            master=self.app,
            border_color=brdr_color, 
            border_width=brdr_width, 
            corner_radius=brdr_radius,
            fg_color=bg_color
        )
        self.left_frame.rowconfigure([0, 1, 2], weight=1)
        self.left_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure([0, 1, 2], weight=1)
        self.right_frame.columnconfigure(0, weight=1)

        # Place the frames in the grid
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        
    def create_title_labels(self):
        title_font_size = 70
        text_color = '#fff'

        # Title Labels
        self.title_label1 = CTkLabel(
            master=self.left_frame,
            text="USAA Data", 
            font=('Roboto Mono Bold', title_font_size), 
            text_color=text_color
        )
        self.title_label2 = CTkLabel(
            master=self.right_frame,
            text="Vystar Data", 
            font=('Roboto Mono Bold', title_font_size), 
            text_color=text_color
        )
        self.title_label1.grid(row=0, column=0, pady=(10, 0), padx=(20,0), sticky='n')
        self.title_label2.grid(row=0, column=0, pady=(10, 0), padx=(20,0), sticky='n')

        # USAA Labels
        self.total_label1 = CTkLabel(
            master=self.left_frame,
            text=f"Total spending this month: {self.u.expenses}", 
            font=('Roboto Mono', 20), 
            text_color=text_color
        )
        self.total_label1.grid(row=2, column=0, pady=(40,0), padx=(85,0), sticky='nw')

        # Vystar Labels
        self.total_label2 = CTkLabel(
            master=self.right_frame,
            text=f"Total earnings this month: {self.v.income} (Metro)\nCar payment: {self.v.car_payment}\nSubscriptions: {self.v.subscriptions} (VCC, PF, Spotify, Amazon Prime)",
            font=('Roboto Mono', 20), 
            text_color=text_color,
            width=400,
            anchor='w',
            justify='left'
        )
        self.total_label2.grid(row=2, column=0, pady=(0,10), padx=(40,0), sticky='w')

V = Vystar('Transactions-2024-07-23.csv')
U = USAA('bk_download (1).csv')

V.readData()
U.readData()

V.calculateIncome()
U.calculateExpenses()

V.createChart()
U.createExpensePieChart()

gui = GUI(V, U)