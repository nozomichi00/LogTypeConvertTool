import customtkinter as ctk
import os, re, random, base64, textwrap
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def select_input_file():
    selected_files = filedialog.askopenfilenames()
    if selected_files:
        input_path.set("\n".join(selected_files))

def select_output_folder():
    selected_folder = filedialog.askdirectory()
    if selected_folder:
        output_folder.set(selected_folder)

def generate_time_options():
    now = datetime.now()
    options = []
    for day_offset in range(-3, 1):
        current_day = now + timedelta(days=day_offset)
        for hour in range(0, 24, 3):
            time_option = current_day.replace(hour=hour, minute=0).strftime('%Y/%m/%d %H:00')
            options.append(time_option)
    return options

def convert_file():
    result_label.configure(text="Converting file, please wait...")
    root.update_idletasks()

    selected_files = input_path.get().split(",")
    if len(selected_files) > 1:
        messagebox.showerror("Error", "Please select only one file for conversion.")
        return
    
    if not input_path.get():
        messagebox.showerror("Error", "Please select a compressed file.")
        return

    if not output_folder.get():
        messagebox.showerror("Error", "Please select an output folder.")
        return

    start_time = datetime.strptime(start_time_combobox.get(), '%Y/%m/%d %H:%M')
    end_time = datetime.strptime(end_time_combobox.get(), '%Y/%m/%d %H:%M')
    if start_time >= end_time:
        messagebox.showerror("Error", "Start time must be earlier than end time.")
        return

    try:
        with open(input_path.get(), "rb") as f:
            data = f.read()
    except Exception as e:
        messagebox.showerror("Error", f"Error reading file: {str(e)}")
        return

    conversion_type = conversion_combobox.get()

    if conversion_type == "Binary":
        converted_data = ' '.join(format(byte, '08b') for byte in data)
    elif conversion_type == "Decimal":
        converted_data = ' '.join(str(byte) for byte in data)
    elif conversion_type == "Hexadecimal":
        converted_data = ' '.join(format(byte, '02x') for byte in data)
    elif conversion_type == "Base64":
        converted_data = base64.b64encode(data).decode()

    wrapped_converted_data = textwrap.fill(converted_data, width=int(max_line_length.get()))
    
    output_lines = []
    wrapped_lines = wrapped_converted_data.split('\n')
    total_lines = len(wrapped_lines)
    
    time_delta = (end_time - start_time) / total_lines if total_lines > 0 else timedelta(0)
    previous_milliseconds = 0

    for i, line in enumerate(wrapped_lines):
        random_milliseconds = random.randint(previous_milliseconds + 1, 999) if previous_milliseconds < 999 else 999
        current_time = start_time + time_delta * i + timedelta(milliseconds=random_milliseconds)
        previous_milliseconds = random_milliseconds
        timestamp = current_time.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
        output_lines.append(f"{timestamp} {line.strip()}")

    output_text = "\n".join(output_lines)
    file_data = []
    current_file_size = 0
    max_file_size_kb = int(max_file_size.get()) * 1024
    num_files = 1

    for line in output_text.splitlines():
        file_data.append(line + "\n")
        current_file_size += len(line.encode('utf-8'))
        
        if current_file_size >= max_file_size_kb:
            output_file_path = os.path.join(output_folder.get(), f"{output_file_name.get()}_{num_files}.txt")
            with open(output_file_path, "w") as f:
                f.writelines(file_data)
            num_files += 1
            file_data = []
            current_file_size = 0

    if file_data:
        output_file_path = os.path.join(output_folder.get(), f"{output_file_name.get()}_{num_files}.txt")
        with open(output_file_path, "w") as f:
            f.writelines(file_data)

    result_label.configure(text=f"Conversion successful, saved as {num_files} file(s)")

def restore_file():
    result_label.configure(text="Restoring file, please wait...")
    root.update_idletasks()

    selected_files = input_path.get().split("\n")
    if not all(file.endswith(".txt") for file in selected_files):
        result_label.configure(text="Please select valid .txt files for restoration.")
        return

    combined_data = []
    for file in selected_files:
        try:
            with open(file, "r") as f:
                combined_data.extend(f.readlines())
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file: {str(e)}")
            return

    clean_data = []
    for line in combined_data:
        clean_line = re.sub(r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\s+', '', line)
        clean_data.append(clean_line.strip())

    clean_data = ' '.join(clean_data)

    try:
        if all(len(b) == 8 for b in clean_data.split()):  # 二進制
            byte_data = bytearray([int(b, 2) for b in clean_data.split()])
        elif all(b.isdigit() for b in clean_data.split()):  # 十進制
            byte_data = bytearray([int(b) for b in clean_data.split()])
        elif all(all(c in '0123456789abcdefABCDEF' for c in b) and len(b) % 2 == 0 for b in clean_data.split()):  # 十六進制
            byte_data = bytearray([int(b, 16) for b in clean_data.split()])
        else:
            byte_data = base64.b64decode(clean_data)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to decode data: {str(e)}")
        return

    output_path = os.path.join(output_folder.get(), f"{output_file_name.get()}.zip")
    with open(output_path, "wb") as f:
        f.write(byte_data)

    result_label.configure(text=f"Restoration successful, saved as {output_path}")

def show_about():
    messagebox.showinfo("About", 
                        "This tool converts compressed files into strings. Please send the string via email,\n"
                        "and then convert it back to the compressed file.\n"
                        "It is recommended to use the Hexadecimal mode.\n\n"
                        "Example of file compression ratio:\n"
                        "1. Original Log: 174 MB\n"
                        "2. Compressed Size: 9.24 MB\n"
                        "3. Compressed String Sizes for Different Types:\n"
                        "   Binary_output.txt: 104 MB\n"
                        "   Decimal_output.txt: 41.0 MB\n"
                        "   Hexadecimal_output.txt: 34.7 MB\n"
                        "   Base64_output.txt: 15.5 MB\n"
                        "4. Restored Size: 9.24 MB; Uncompressed Size: 174 MB\n\n"
                        "===============================================\n\n"
                        "此工具使用方式是將壓縮檔案轉換成字串，請客戶信件寄出後，\n"
                        "再將字串轉換回壓縮檔。\n"
                        "建議使用: Hexadecimal 模式\n\n"
                        "以下是檔案壓縮率的範例：\n"
                        "1. 原始Log共 174 MB\n"
                        "2. 壓縮後共 9.24 MB\n"
                        "3. 轉換字串後不同類型的壓縮：\n"
                        "   Binary_output.txt: 104 MB\n"
                        "   Decimal_output.txt: 41.0 MB\n"
                        "   Hexadecimal_output.txt: 34.7 MB\n"
                        "   Base64_output.txt: 15.5 MB\n"
                        "4. 還原後共 9.24 MB，解壓縮後共 174 MB")

root = ctk.CTk()
root.title("File Conversion Tool Ver.2")
root.geometry("570x550")

scrollable_frame = ctk.CTkScrollableFrame(root)
scrollable_frame.grid(row=0, column=0, sticky="nsew")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

input_path = ctk.StringVar()
output_folder = ctk.StringVar()
max_line_length = ctk.StringVar(value="100")
max_file_size = ctk.StringVar(value="3000")
output_file_name = ctk.StringVar(value="OutputFileName")

ctk.CTkLabel(scrollable_frame, text="Select input file (zip/txt):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
ctk.CTkEntry(scrollable_frame, textvariable=input_path, width=200).grid(row=0, column=1, padx=10, pady=10, sticky="w")
ctk.CTkButton(scrollable_frame, text="Browse", command=select_input_file).grid(row=0, column=2, padx=10, pady=10)

ctk.CTkLabel(scrollable_frame, text="Select output folder:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
ctk.CTkEntry(scrollable_frame, textvariable=output_folder, width=200).grid(row=1, column=1, padx=10, pady=10, sticky="w")
ctk.CTkButton(scrollable_frame, text="Browse", command=select_output_folder).grid(row=1, column=2, padx=10, pady=10)

ctk.CTkLabel(scrollable_frame, text="Select start time:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
start_time_combobox = ctk.CTkComboBox(scrollable_frame, values=generate_time_options(), width=200)
start_time_combobox.set(generate_time_options()[0])
start_time_combobox.grid(row=2, column=1, padx=10, pady=10, sticky="w")

ctk.CTkLabel(scrollable_frame, text="Select end time:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
end_time_combobox = ctk.CTkComboBox(scrollable_frame, values=generate_time_options(), width=200)
end_time_combobox.set(generate_time_options()[-1])
end_time_combobox.grid(row=3, column=1, padx=10, pady=10, sticky="w")

ctk.CTkLabel(scrollable_frame, text="Max line length:").grid(row=4, column=0, padx=10, pady=10, sticky="e")
ctk.CTkEntry(scrollable_frame, textvariable=max_line_length, width=200).grid(row=4, column=1, padx=10, pady=10, sticky="w")

ctk.CTkLabel(scrollable_frame, text="Max file size (KB):").grid(row=5, column=0, padx=10, pady=10, sticky="e")
ctk.CTkEntry(scrollable_frame, textvariable=max_file_size, width=200).grid(row=5, column=1, padx=10, pady=10, sticky="w")

ctk.CTkLabel(scrollable_frame, text="Conversion type:").grid(row=6, column=0, padx=10, pady=10, sticky="e")
conversion_combobox = ctk.CTkComboBox(scrollable_frame, values=["Binary", "Decimal", "Hexadecimal", "Base64"], width=200)
conversion_combobox.set("Hexadecimal")
conversion_combobox.grid(row=6, column=1, padx=10, pady=10, sticky="w")

ctk.CTkLabel(scrollable_frame, text="Output file name:").grid(row=7, column=0, padx=10, pady=10, sticky="e")
ctk.CTkEntry(scrollable_frame, textvariable=output_file_name, width=200).grid(row=7, column=1, padx=10, pady=10, sticky="w")

ctk.CTkButton(scrollable_frame, text="Convert", command=convert_file).grid(row=8, column=0, padx=10, pady=10)
ctk.CTkButton(scrollable_frame, text="Restore", command=restore_file).grid(row=8, column=1, padx=10, pady=10)

ctk.CTkButton(scrollable_frame, text="About", command=show_about).grid(row=8, column=2, padx=10, pady=10)

result_label = ctk.CTkLabel(scrollable_frame, text="", text_color="cyan")
result_label.grid(row=9, column=0, columnspan=3)

ctk.CTkLabel(scrollable_frame, text="Selected files:").grid(row=10, column=0, padx=10, pady=(10, 0), sticky="W")
selected_files_label = ctk.CTkLabel(scrollable_frame, textvariable=input_path)
selected_files_label.grid(row=11, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="w")

root.mainloop()
