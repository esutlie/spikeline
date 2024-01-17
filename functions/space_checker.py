import os
import tkinter as tk
from tkinter import ttk
import time
import psutil

redundant = []
num_redundant = 0


def build_cache(dir_path, cache):
    total_size = 0
    try:
        with os.scandir(dir_path) as entries:
            for entry in entries:
                if entry.name[0] == '$':
                    continue
                if entry.is_file():
                    size = entry.stat().st_size
                elif entry.is_dir():
                    size, cache = build_cache(entry.path, cache)
                cache[entry.path] = size
                total_size += size
    except Exception as e:
        # print(f"Error accessing {dir_path}: {e}")
        pass
    return total_size, cache


def get_folder_size(folder_path, cache):
    # if folder_path in cache:
    #     return cache[folder_path]
    #
    total_size = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)

            if file_path in cache:
                total_size += cache[file_path]
            else:
                size = os.path.getsize(file_path)
                total_size += size
                cache[file_path] = size

    # total_size = sum(
    #     os.path.getsize(os.path.join(root, file)) for root, dirs, files in os.walk(folder_path) for file in files)
    # cache[folder_path] = total_size
    return total_size


def populate_tree(tree, parent, path, cache):
    try:
        for p in os.listdir(path):
            p_full = os.path.join(path, p)
            # size = get_folder_size(p_full, cache) if os.path.isdir(p_full) else os.path.getsize(p_full)
            if p_full not in cache:
                continue
            item = tree.insert(parent, 'end', text=p, values=(f"{cache[p_full] / (1024 ** 3):.2f} GB",))
            if os.path.isdir(p_full):
                populate_tree(tree, item, p_full, cache)
    except Exception as e:
        # print(f"Error accessing {path}: {e}")
        pass


def main(dir_path):
    root = tk.Tk()
    root.title("Directory Sizes Viewer")

    tree = ttk.Treeview(root)
    tree["columns"] = ("size",)
    tree.column("#0", width=300)  # Set width for the first column
    tree.column("size", anchor="e")  # Set anchor for the second column
    tree.heading("#0", text="Directory")
    tree.heading("size", text="Size")
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tic = time.time()
    cache = {}
    size, cache = build_cache(dir_path, cache)
    populate_tree(tree, '', dir_path, cache)  # Change this to the desired directory path
    print(f'{time.time() - tic:.0f} seconds to calculate')

    style = ttk.Style()
    # print(style.theme_names())
    style.theme_use('clam')
    style.configure("Treeview", font=("Helvetica", 12))  # Adjust font size for Treeview widget
    style.configure("Treeview.Heading", font=("Helvetica", 14))  # Adjust font size for column headings

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    disk = os.path.split(dir_path)[0]
    disk_usage = psutil.disk_usage(disk)
    free = disk_usage.free / (1024 ** 3)
    used = disk_usage.used / (1024 ** 3)
    total = disk_usage.total / (1024 ** 3)
    print(f"Space scanned: {size / (1024 ** 3):.0f} GB")
    if dir_path == disk:
        print(f"Space used by hidden folders: {used - (size / (1024 ** 3)):.0f} GB")
    print(f'Space remaining on {disk[0]} drive: {free:.0f}/{total:.0f} GB   ({free / total * 100:.0f}%)')
    root.mainloop()


if __name__ == "__main__":
    main_path = os.path.join('C:\\')
    main(main_path)
