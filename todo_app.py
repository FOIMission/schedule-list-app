import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime


class SimpleFloatingTodoApp:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("简易悬浮日程")
        self.root.withdraw()  # 隐藏主窗口，只显示悬浮窗口

        # 数据文件路径
        self.data_file = "todo_data.json"
        self.tasks = []

        # 窗口状态
        self.is_collapsed = False

        # 加载数据
        self.load_data()

        # 创建悬浮窗口
        self.create_floating_window()

    def create_floating_window(self):
        """创建悬浮窗口"""
        self.floating_window = tk.Toplevel(self.root)
        self.floating_window.title("简易悬浮日程")
        self.floating_window.geometry("300x400")
        self.floating_window.attributes('-topmost', True)  # 始终置顶
        self.floating_window.overrideredirect(True)  # 无边框
        self.floating_window.configure(bg='#2c3e50')
        self.floating_window.attributes('-alpha', 0.95)  # 透明度

        # 标题栏
        title_bar = tk.Frame(self.floating_window, bg='#34495e', height=30)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)

        # 标题
        title_label = tk.Label(title_bar, text="📝 简易日程", bg='#34495e', fg='white',
                               font=('Microsoft YaHei', 10, 'bold'))
        title_label.pack(side=tk.LEFT, padx=10)

        # 关闭按钮
        close_btn = tk.Label(title_bar, text="×", bg='#34495e', fg='white',
                             font=('Arial', 16, 'bold'), cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=10)
        close_btn.bind("<Button-1>", lambda e: self.hide_window())

        # 折叠按钮
        self.collapse_btn = tk.Label(title_bar, text="−", bg='#34495e', fg='white',
                                     font=('Arial', 16, 'bold'), cursor="hand2")
        self.collapse_btn.pack(side=tk.RIGHT, padx=10)
        self.collapse_btn.bind("<Button-1>", lambda e: self.toggle_collapse())

        # 拖动功能
        title_bar.bind("<ButtonPress-1>", self.start_move)
        title_bar.bind("<ButtonRelease-1>", self.stop_move)
        title_bar.bind("<B1-Motion>", self.on_motion)

        # 主内容区域
        self.main_frame = tk.Frame(self.floating_window, bg='#ecf0f1')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 输入区域
        input_frame = tk.Frame(self.main_frame, bg='#ecf0f1')
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        self.task_entry = tk.Entry(input_frame, font=('Microsoft YaHei', 10),
                                   bg='white', relief=tk.FLAT, highlightthickness=1,
                                   highlightcolor='#3498db', highlightbackground='#bdc3c7')
        self.task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.task_entry.bind("<Return>", lambda e: self.add_task())

        add_btn = tk.Button(input_frame, text="添加", bg='#27ae60', fg='white',
                            font=('Microsoft YaHei', 9), relief=tk.FLAT,
                            command=self.add_task, cursor="hand2")
        add_btn.pack(side=tk.RIGHT)

        # 任务列表区域
        list_frame = tk.Frame(self.main_frame, bg='#ecf0f1')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # 创建滚动条
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 任务列表
        self.task_listbox = tk.Listbox(list_frame, bg='white', bd=0,
                                       selectmode=tk.SINGLE,
                                       font=('Microsoft YaHei', 9),
                                       yscrollcommand=scrollbar.set)
        self.task_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.task_listbox.yview)

        # 绑定事件
        self.task_listbox.bind("<Double-Button-1>", self.toggle_task_completion)
        self.task_listbox.bind("<Delete>", self.delete_selected_task)

        # 底部按钮区域
        self.button_frame = tk.Frame(self.main_frame, bg='#ecf0f1')
        self.button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # 删除按钮
        delete_btn = tk.Button(self.button_frame, text="删除选中", bg='#e74c3c', fg='white',
                               font=('Microsoft YaHei', 9), relief=tk.FLAT,
                               command=self.delete_selected_task, cursor="hand2")
        delete_btn.pack(side=tk.LEFT)

        # 清空按钮
        clear_btn = tk.Button(self.button_frame, text="清空已完成", bg='#f39c12', fg='white',
                              font=('Microsoft YaHei', 9), relief=tk.FLAT,
                              command=self.clear_completed, cursor="hand2")
        clear_btn.pack(side=tk.RIGHT)

        # 刷新任务列表
        self.refresh_task_list()

        # 初始位置（屏幕右下角）
        self.position_window()

    def toggle_window(self, event=None):
        """切换窗口显示状态"""
        if self.floating_window.winfo_viewable():
            self.hide_window()
        else:
            self.show_window()

    def toggle_collapse(self, event=None):
        """切换折叠状态"""
        if not self.is_collapsed:
            self.collapse_window()
        else:
            self.expand_window()

    def collapse_window(self):
        """折叠窗口"""
        # 获取当前位置
        x = self.floating_window.winfo_x()
        y = self.floating_window.winfo_y()

        # 隐藏主内容区域
        self.main_frame.pack_forget()

        # 更新折叠按钮文本
        self.collapse_btn.config(text="+")

        # 调整窗口大小到只显示标题栏
        self.floating_window.geometry(f"300x30+{x}+{y}")

        self.is_collapsed = True

    def expand_window(self):
        """展开窗口"""
        # 获取当前位置
        x = self.floating_window.winfo_x()
        y = self.floating_window.winfo_y()

        # 恢复主内容区域
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # 更新折叠按钮文本
        self.collapse_btn.config(text="−")

        # 恢复窗口大小
        self.floating_window.geometry(f"300x400+{x}+{y}")

        self.is_collapsed = False

    def position_window(self):
        """将窗口定位到屏幕右下角"""
        screen_width = self.floating_window.winfo_screenwidth()
        screen_height = self.floating_window.winfo_screenheight()

        if self.is_collapsed:
            window_width = 150
            window_height = 30
        else:
            window_width = 300
            window_height = 400

        x = screen_width - window_width - 20
        y = screen_height - window_height - 50

        self.floating_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def start_move(self, event):
        """开始拖动窗口"""
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        """停止拖动"""
        self.x = None
        self.y = None

    def on_motion(self, event):
        """拖动窗口"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.floating_window.winfo_x() + deltax
        y = self.floating_window.winfo_y() + deltay
        self.floating_window.geometry(f"+{x}+{y}")

    def show_window(self):
        """显示窗口"""
        self.floating_window.deiconify()
        if self.is_collapsed:
            # 折叠状态下自动展开
            self.expand_window()
        self.task_entry.focus()

    def hide_window(self):
        """隐藏窗口"""
        self.floating_window.withdraw()

    def load_data(self):
        """加载任务数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []
        else:
            self.tasks = []

    def save_data(self):
        """保存任务数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")

    def refresh_task_list(self):
        """刷新任务列表"""
        self.task_listbox.delete(0, tk.END)

        for task in self.tasks:
            status = "✅ " if task.get("completed", False) else "⏳ "

            # 安全地获取时间信息
            time_str = task.get("time", "")
            if time_str:
                try:
                    time_display = time_str.split()[0] if " " in time_str else time_str
                except:
                    time_display = time_str
            else:
                time_display = "未知时间"

            task_text = f"{status}{task['text']} ({time_display})"
            self.task_listbox.insert(tk.END, task_text)

            # 设置已完成任务的样式
            if task.get("completed", False):
                self.task_listbox.itemconfig(tk.END, {'fg': '#7f8c8d'})

    def add_task(self, event=None):
        """添加新任务"""
        task_text = self.task_entry.get().strip()
        if not task_text:
            messagebox.showwarning("提示", "请输入任务内容")
            return

        new_task = {
            "text": task_text,
            "completed": False,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.tasks.append(new_task)
        self.save_data()
        self.refresh_task_list()

        # 清空输入框并重新聚焦
        self.task_entry.delete(0, tk.END)
        self.task_entry.focus()

    def toggle_task_completion(self, event):
        """切换任务完成状态"""
        selection = self.task_listbox.curselection()
        if selection:
            index = selection[0]
            self.tasks[index]["completed"] = not self.tasks[index].get("completed", False)
            self.save_data()
            self.refresh_task_list()

    def delete_selected_task(self, event=None):
        """删除选中的任务"""
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个任务")
            return

        index = selection[0]
        del self.tasks[index]
        self.save_data()
        self.refresh_task_list()

    def clear_completed(self):
        """清空所有已完成的任务"""
        completed_count = sum(1 for task in self.tasks if task.get("completed", False))
        if completed_count == 0:
            messagebox.showinfo("提示", "没有已完成的任务")
            return

        if messagebox.askyesno("确认", f"确定要删除{completed_count}个已完成的任务吗？"):
            self.tasks = [task for task in self.tasks if not task.get("completed", False)]
            self.save_data()
            self.refresh_task_list()

    def quit_app(self):
        """退出应用程序"""
        self.root.quit()

    def run(self):
        """运行应用程序"""
        # 显示使用提示
        print("=" * 50)
        print("简易悬浮待办事项")
        print("=" * 50)
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.quit_app()


def main():
    # 运行应用
    app = SimpleFloatingTodoApp()
    app.run()


if __name__ == "__main__":
    main()