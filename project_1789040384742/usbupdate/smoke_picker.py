"""Choose original ATS smoke files once before starting stress hardware actions."""
import copy
from smoke_runner import discover


def select_smoke_files(cfg):
    import tkinter as tk
    from tkinter import ttk, messagebox
    listing = copy.deepcopy(cfg)
    listing.setdefault('smoke', {}).pop('case_files', None)
    root, files = discover(listing)
    window = tk.Tk()
    window.title('选择本次压测的 ATS 冒烟用例')
    window.geometry('900x620')
    ttk.Label(window, text='选择一个或多个用例，或选模块后点击“选择该模块”；每轮复用本次选择。').pack(padx=12, pady=10)
    modules = sorted({p.parent.relative_to(root).as_posix() for p in files})
    toolbar = ttk.Frame(window)
    toolbar.pack(fill='x', padx=12)
    module = ttk.Combobox(toolbar, values=modules, state='readonly', width=65)
    module.pack(side='left')
    if modules:
        module.current(0)
    frame = ttk.Frame(window)
    frame.pack(fill='both', expand=True, padx=12, pady=10)
    items = tk.Listbox(frame, selectmode=tk.EXTENDED, exportselection=False)
    scroll = ttk.Scrollbar(frame, orient='vertical', command=items.yview)
    items.configure(yscrollcommand=scroll.set)
    scroll.pack(side='right', fill='y')
    items.pack(side='left', fill='both', expand=True)
    for path in files:
        items.insert(tk.END, path.relative_to(root).as_posix())
    previous = set(cfg.get('smoke', {}).get('case_files', []))
    for index, path in enumerate(files):
        if path.relative_to(root).as_posix() in previous:
            items.selection_set(index)
    def choose_module():
        prefix = module.get()
        for index, path in enumerate(files):
            if path.parent.relative_to(root).as_posix() == prefix:
                items.selection_set(index)
    ttk.Button(toolbar, text='选择该模块（追加）', command=choose_module).pack(side='left', padx=8)
    result = []
    def confirm():
        indexes = items.curselection()
        if not indexes:
            messagebox.showwarning('未选择用例', '至少选择一条用例，或取消本次压测。', parent=window)
            return
        result.extend(files[index].relative_to(root).as_posix() for index in indexes)
        window.destroy()
    buttons = ttk.Frame(window)
    buttons.pack(fill='x', padx=12, pady=10)
    ttk.Button(buttons, text='全选', command=lambda: items.selection_set(0, tk.END)).pack(side='left')
    ttk.Button(buttons, text='清空', command=lambda: items.selection_clear(0, tk.END)).pack(side='left', padx=8)
    ttk.Button(buttons, text='取消压测', command=window.destroy).pack(side='right')
    ttk.Button(buttons, text='确认用例并开始压测', command=confirm).pack(side='right', padx=8)
    window.mainloop()
    if not result:
        raise RuntimeError('用户取消用例选择，未启动压测')
    return result
