import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from ttkbootstrap import Style
import threading
from datetime import datetime, timedelta
from PIL import Image, ImageTk


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List")
        
        window_width = 600
        window_height = 700

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        position_x = int((screen_width / 2) - (window_width / 2))
        position_y = int((screen_height / 2) - (window_height / 2))
  
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

        self.style = Style(theme="cosmo")

        self.tasks = []
        self.completed_tasks = []
        self.heading_text = tk.StringVar(value="My Tasks")

        self.selected_font = tk.StringVar(value="Georgia")

        logo_image = Image.open("todo_logo.png")
        logo_photo = ImageTk.PhotoImage(logo_image)
        self.root.iconphoto(False, logo_photo)  

        self.background_image = None
        self.setup_ui()

    def setup_ui(self):
        self.main_frame = ttk.Frame(self.root, style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        header_frame = ttk.Frame(self.main_frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(10, 5))

        self.heading_label = ttk.Label(header_frame, textvariable=self.heading_text, font=("Georgia", 24, "bold"), foreground="#0078D7")
        self.heading_label.pack(side=tk.LEFT, padx=10)
        self.heading_label.bind("<Button-1>", self.change_heading)

        add_list_btn = ttk.Button(header_frame, text="+", command=self.save_to_file, style="Accent.TButton", width=3)
        add_list_btn.pack(side=tk.RIGHT, padx=10)

        entry_frame = ttk.Frame(self.main_frame, style='TFrame')
        entry_frame.pack(fill=tk.X, pady=5, padx=10)

        self.task_var = tk.StringVar()
        self.task_entry = ttk.Entry(entry_frame, textvariable=self.task_var, font=("Segoe UI", 12), style='TEntry')
        self.task_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.task_entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.task_entry.bind("<FocusOut>", self.on_entry_focus_out)
        self.task_entry.bind("<Return>", self.add_task)


        self.emoji_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.emoji_frame.pack(fill=tk.X, pady=5, padx=10)
        self.setup_emoji_picker()

       
        self.task_var.set("Add a task...")
        self.task_entry.config(foreground="gray")

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        self.tasks_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.tasks_frame, text="Tasks")

        self.task_listbox = tk.Listbox(self.tasks_frame, font=("Segoe UI", 11), selectmode=tk.SINGLE, activestyle='none', 
                                       bg='#F0F0F0', fg='#333333', selectbackground='#0078D7', selectforeground='white')
        self.task_listbox.pack(fill=tk.BOTH, expand=True)
        self.task_listbox.bind('<Button-3>', self.show_context_menu)  
        
        self.completed_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.completed_frame, text="Completed")

        self.completed_listbox = tk.Listbox(self.completed_frame, font=("Segoe UI", 11), selectmode=tk.SINGLE, activestyle='none',
                                            bg='#F0F0F0', fg='#333333', selectbackground='#0078D7', selectforeground='white')
        self.completed_listbox.pack(fill=tk.BOTH, expand=True)

        # Hover menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Set Reminder", command=self.set_reminder_context)
        self.context_menu.add_command(label="Complete", command=self.complete_task_context)
        self.context_menu.add_command(label="Delete", command=self.delete_task_context)

        toolbar_frame = ttk.Frame(self.main_frame, style='TFrame')
        toolbar_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        themes = ["flatly", "darkly", "cosmo", "litera", "minty"]
        theme_combo = ttk.Combobox(toolbar_frame, values=themes, state="readonly", width=10)
        theme_combo.set("flatly")
        theme_combo.pack(side=tk.RIGHT, padx=10)
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)

        fonts = ["Segoe UI", "Arial", "Verdana", "Courier New", "Comic Sans MS", "Georgia", "Helvetica", "Times New Roman", "Trebuchet MS", "Calibri"]
        font_combo = ttk.Combobox(toolbar_frame, values=fonts, textvariable=self.selected_font, state="readonly", width=15)
        font_combo.set(self.selected_font.get())  # Default font
        font_combo.pack(side=tk.LEFT, padx=10)
        font_combo.bind("<<ComboboxSelected>>", self.change_font)

    def setup_emoji_picker(self):
        emojis = ["😍", "😊", "😂", "😀", "❤️", "👍", "🎉", "🔥", "🙏", "👏",
          "😎", "😉", "💪", "😜", "🤔", "🎶", "🤩", "💥", "🌟", "🙌",
          "🥳", "💯", "😇", "😅", "🥰", "🎂", "😋", "🙈", "😱", "🤗"]
        row, col = 0, 0
        for emoji in emojis:
            btn = ttk.Button(self.emoji_frame, text=emoji, width=3, command=lambda e=emoji: self.insert_emoji(e))
            btn.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 10:
                col = 0
                row += 1
    def show_context_menu(self, event):
        try:
            index = self.task_listbox.nearest(event.y)
            if 0 <= index < len(self.tasks):
                self.task_listbox.selection_clear(0, tk.END)
                self.task_listbox.selection_set(index)
                self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def set_reminder_context(self):
        if self.task_listbox.curselection():
            index = self.task_listbox.curselection()[0]
            self.set_reminder(index)

    def complete_task_context(self):
        if self.task_listbox.curselection():
            index = self.task_listbox.curselection()[0]
            task_info = self.tasks.pop(index)
            self.completed_tasks.append(task_info)
            self.update_listbox()

    def delete_task_context(self):
        if self.task_listbox.curselection():
            index = self.task_listbox.curselection()[0]
            self.tasks.pop(index)
            self.update_listbox()

    def on_entry_focus_in(self, event):
        if self.task_var.get() == "Add a task...":
            self.task_var.set("")
            self.task_entry.config(foreground="black")

    def on_entry_focus_out(self, event):
        if not self.task_var.get():
            self.task_var.set("Add a task...")
            self.task_entry.config(foreground="gray")

    def add_task(self, event=None):
        task = self.task_var.get().strip()
        if task:
            task_info = {"task": task, "remind_time": None}
            self.tasks.append(task_info)
            self.task_var.set("")
            self.update_listbox()
        else:
            messagebox.showwarning("Input Error", "Please enter a new task before adding.")

    def update_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for i, task_info in enumerate(self.tasks, 1):
            task_text = f"{i}. {task_info['task']}"
            if task_info['remind_time']:
                task_text += f" (Reminder: {task_info['remind_time']})"
            self.task_listbox.insert(tk.END, task_text)
        
        self.completed_listbox.delete(0, tk.END)
        for i, task_info in enumerate(self.completed_tasks, 1):
            task_text = f"{i}. {task_info['task']}"
            self.completed_listbox.insert(tk.END, task_text)

    def on_hover(self, event):
        index = self.task_listbox.nearest(event.y)
        if 0 <= index < len(self.tasks):
            self.task_listbox.selection_clear(0, tk.END)
            self.task_listbox.selection_set(index)
            self.hover_menu.post(event.x_root, event.y_root)

    def on_leave(self, event):
        self.hover_menu.unpost()

    def set_reminder_hover(self):
        index = self.task_listbox.curselection()[0]
        self.set_reminder(index)

    def complete_task_hover(self):
        index = self.task_listbox.curselection()[0]
        task_info = self.tasks.pop(index)
        self.completed_tasks.append(task_info)
        self.update_listbox()
        self.hover_menu.unpost()

    def delete_task_hover(self):
        index = self.task_listbox.curselection()[0]
        self.tasks.pop(index)
        self.update_listbox()
        self.hover_menu.unpost()

    def set_reminder(self, index):
        reminder_window = tk.Toplevel(self.root)
        reminder_window.title("Set Reminder")
        reminder_window.geometry("350x250")

        # Date selection
        date_frame = ttk.Frame(reminder_window)
        date_frame.pack(pady=10)

        ttk.Label(date_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5)
        date_entry = ttk.Entry(date_frame, width=12)
        date_entry.grid(row=0, column=1, padx=5)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Time selection
        time_frame = ttk.Frame(reminder_window)
        time_frame.pack(pady=10)

        ttk.Label(time_frame, text="Time (HH:MM):").grid(row=0, column=0, padx=5)
        time_entry = ttk.Entry(time_frame, width=8)
        time_entry.grid(row=0, column=1, padx=5)
        time_entry.insert(0, datetime.now().strftime("%H:%M"))

        def save_reminder():
            date = date_entry.get()
            time = time_entry.get()
            try:
                remind_datetime = f"{date} {time}"
                datetime.strptime(remind_datetime, "%Y-%m-%d %H:%M")  
                self.tasks[index]['remind_time'] = remind_datetime
                self.update_listbox()
                self.schedule_reminder(self.tasks[index]['task'], remind_datetime)
                reminder_window.destroy()
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid date and time.")

        ttk.Button(reminder_window, text="Save", command=save_reminder).pack(pady=10)

    def schedule_reminder(self, task, remind_datetime):
        def show_reminder():
            messagebox.showinfo("Reminder", f"It's time for your new task: {task}")

        now = datetime.now()
        remind_time = datetime.strptime(remind_datetime, "%Y-%m-%d %H:%M")
        
        if remind_time > now:
            delay = (remind_time - now).total_seconds()
            threading.Timer(delay, show_reminder).start()

    def save_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write("Tasks:\n")
                for task_info in self.tasks:
                    file.write(f"- {task_info['task']}")
                    if task_info['remind_time']:
                        file.write(f" (Remind: {task_info['remind_time']})")
                    file.write("\n")
                file.write("\nCompleted Tasks:\n")
                for task_info in self.completed_tasks:
                    file.write(f"- {task_info['task']}\n")
            messagebox.showinfo("File Saved", "Your to-do list has been saved.")

   
    def insert_emoji(self, emoji_char):
        current_text = self.task_var.get()
        if current_text == "Add a task...":
            current_text = ""
        self.task_var.set(current_text + emoji_char)
        self.task_entry.icursor(tk.END)
        self.task_entry.config(foreground="black")   

    def change_theme(self, event):
        selected_theme = event.widget.get()
        self.style.theme_use(selected_theme)

    def change_heading(self, event):
        new_heading = simpledialog.askstring("Change Heading", "Enter new heading:", parent=self.root)
        if new_heading:
            self.heading_text.set(new_heading)

    def change_font(self, event=None):
        font_name = self.selected_font.get()
        self.task_listbox.config(font=(font_name, 12))
        self.completed_listbox.config(font=(font_name, 12))

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
