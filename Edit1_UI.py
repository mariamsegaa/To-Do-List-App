import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QHBoxLayout,QInputDialog
from PyQt6.QtCore import Qt  # Add this for checkbox states
from PyQt6.QtGui import QIcon


class ToDoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("To_Do_List") # Title
        self.setGeometry(100, 100, 500, 400) # x,y,width,height
        self.setWindowIcon(QIcon("D:/Python Project(To-Do List)/ToDoIcon2.png"))  # set window icon

        # Database setup
        self.conn = sqlite3.connect("D:/PYTHON/To_Do_List.db")
        self.cursor = self.conn.cursor() # To execute commands
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         task TEXT NOT NULL,
                         Completed INTEGER DEFAULT 0,
                         Due_Date TEXT,
                         Priority TEXT)''')
        self.conn.commit()
      
        # UI Elements
        self.layout = QVBoxLayout() # arranging layout of widgets

        # Task input
        self.task_input = QLineEdit(self) # text input field 
        self.task_input.setPlaceholderText("Enter new task...") # hint text
        self.task_input.returnPressed.connect(self.add_task)
        self.layout.addWidget(self.task_input) # add input field
        

        # Buttons Layout
        self.buttons_layout = QHBoxLayout()

        # Add Task 
        self.add_button = QPushButton("Add Task", self) # create button,label it
        self.add_button.clicked.connect(self.add_task) # connect the button whth function
        self.buttons_layout.addWidget(self.add_button) # add to layout

        # Edit Task 
        self.edit_button = QPushButton("Edit Task", self)
        self.edit_button.clicked.connect(self.edit_task)
        self.buttons_layout.addWidget(self.edit_button)

        # Delete Task 
        self.delete_button = QPushButton("Delete Task", self)
        self.delete_button.clicked.connect(self.delete_task)
        self.buttons_layout.addWidget(self.delete_button)

        # Mark as Completed 
        self.complete_button = QPushButton("Mark as Completed", self)
        self.complete_button.clicked.connect(self.mark_task_completed)
        self.buttons_layout.addWidget(self.complete_button)
        
        # Clear All Tasks
        self.clear_button = QPushButton("Clear All Tasks", self)
        self.clear_button.clicked.connect(self.clear_all_tasks)
        self.layout.addWidget(self.clear_button)

        self.layout.addLayout(self.buttons_layout)
        

        # Task list
        self.task_list = QListWidget(self) # displaying tasks as list
        self.task_list.itemChanged.connect(self.toggle_task_completed)# Listen for checkbox change
        self.layout.addWidget(self.task_list) # add to layout

        # Delete Completed Task
        self.delete_completed_button = QPushButton("Delete Completed Tasks", self)
        self.delete_completed_button.clicked.connect(self.delete_completed_tasks)
        self.layout.addWidget(self.delete_completed_button)

        # Sorting Buttons Layout
        self.sort_buttons_layout = QHBoxLayout()

        # Sort by Unfinished Tasks
        self.sort_unfinished_button = QPushButton("Sort by Unfinished", self)
        self.sort_unfinished_button.clicked.connect(lambda: self.show_tasks(sort_by="unfinished"))
        self.sort_buttons_layout.addWidget(self.sort_unfinished_button)

        # Sort by Due Date
        self.sort_due_button = QPushButton("Sort by Due Date", self)
        self.sort_due_button.clicked.connect(lambda: self.show_tasks(sort_by="due_date"))
        self.sort_buttons_layout.addWidget(self.sort_due_button)

        # Sort by Priority
        self.sort_priority_button = QPushButton("Sort by Priority", self)
        self.sort_priority_button.clicked.connect(lambda: self.show_tasks(sort_by="priority"))
        self.sort_buttons_layout.addWidget(self.sort_priority_button)

        # Add sorting layout to the main layout
        self.layout.addLayout(self.sort_buttons_layout)

        self.setLayout(self.layout) # assign the layout to main window
        self.show_tasks() # fetch saved tasks from database
        
        
    def add_task(self):
        task_text = self.task_input.text().strip()
        if task_text:
            # Get Due Date
            due_date, ok = QInputDialog.getText(self, "Due Date", "Enter due date (DD-MM-YYYY) or Leave Empty:")
            if not ok:
                return
        
            # Get Priority
            priority, ok = QInputDialog.getItem(self, "Priority", "Select priority:", ["Urgent", "Normal", "Low Effort"], 0, False)
            if not ok:
                return

            self.cursor.execute("INSERT INTO tasks (task, completed, Due_Date, Priority) VALUES (?, 0, ?, ?)", (task_text, due_date if due_date else None, priority))
            self.conn.commit()
            self.show_tasks()
            self.task_input.clear()
        else:
            QMessageBox.warning(self, "Warning", "Field Cannot Be Empty!")


    def show_tasks(self, sort_by=None):
        self.task_list.clear()
    
        query = "SELECT id, task, Completed, Due_Date, Priority FROM tasks"
    
        # Sorting Logic
        if sort_by == "unfinished":
            query += " ORDER BY Completed ASC, id DESC"  # Unfinished tasks first
        elif sort_by == "due_date":
            query += " ORDER BY Due_Date IS NULL, Due_Date ASC"  # Earliest due date first
        elif sort_by == "priority":
            query += " ORDER BY CASE Priority WHEN 'Urgent' THEN 1 WHEN 'Normal' THEN 2 WHEN 'Low Effort' THEN 3 ELSE 4 END"  # High priority first
    
        self.cursor.execute(query)
        tasks = self.cursor.fetchall()
    
        for task in tasks:
            item = QListWidgetItem(f"{task[1]} | Due: {task[3] if task[3] else 'No Date'} | Priority: {task[4] if task[4] else 'None'}")
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if task[2] else Qt.CheckState.Unchecked)
            item.setData(32, task[0]) #store Id
            self.task_list.addItem(item)
       # tasks = self.cursor.fetchall()
        # print("Retrieved tasks:", tasks)


           
    def toggle_task_completed(self, item):
        task_id = item.data(32)
        completed = 1 if item.checkState() == 2 else 0
        self.cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id))
        self.conn.commit()
        
    def delete_completed_tasks(self):
        self.cursor.execute("DELETE FROM tasks WHERE completed = 1")
        self.conn.commit()
        self.show_tasks()  # Refresh task list

    def edit_task(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            new_task, ok = QInputDialog().getText(self, "Edit Task", "Modify your task:", text=selected_item.text())
            if ok and new_task.strip():
                self.cursor.execute("UPDATE tasks SET task = ? WHERE task = ?", (new_task, selected_item.text()))
                self.conn.commit()
                self.show_tasks()
        else:
            QMessageBox.warning(self, "Warning", "Please select a task to edit!")

    def delete_task(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            task_id = selected_item.data(32)  # Get task ID
            reply = QMessageBox.question(self, "Delete Task", "Are you sure you want to delete this task?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                self.conn.commit()
                self.show_tasks()
        else:
            QMessageBox.warning(self, "Warning", "Please select a task to delete!")


    def mark_task_completed(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            task_id = selected_item.data(32)  # Get task ID
            self.cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
            self.conn.commit()
            self.show_tasks()
        else:
            QMessageBox.warning(self, "Warning", "Please select a task to mark as completed!")


    def closeEvent(self, event):
        self.conn.close() #close connection
        event.accept()

    def clear_all_tasks(self):
        reply = QMessageBox.question(self, "Clear All Tasks", "Are you sure you want to clear all tasks?",
                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.cursor.execute("DELETE FROM tasks")
            self.conn.commit()

        # clear from UI
        self.task_list.clear()
        
        self.show_tasks()
        
        


if __name__ == "__main__": #runs only when executed directly not when imported
    app = QApplication(sys.argv) # creates an instance app ,pass system arguments
    UI = ToDoApp() #creates main window
    UI.show() # display it
    sys.exit(app.exec())# keep app running,ensure proper exit
