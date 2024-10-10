import customtkinter as ctk
import os, re, random, base64, textwrap
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def select_input_file():
    input_path.set(filedialog.askopenfilename())

def select_output_folder():
    output_folder.set(filedialog.askdirectory())

def generate_time_options():
    now = datetime.now()
    options = []
    for day_offset in range(-3, 1):  # 前後日期
        current_day = now + timedelta(days=day_offset)
        for hour in range(0, 24, 3):  # 時間間隔
            time_option = current_day.replace(hour=hour, minute=0).strftime('%Y/%m/%d %H:00')
            options.append(time_option)
    return options

def convert_file():
    # 檢查輸入檔案是否選擇
    if not input_path.get():
        messagebox.showerror("Error", "Please select an compressed file.")
        return

    # 檢查輸出資料夾是否選擇
    if not output_folder.get():
        messagebox.showerror("Error", "Please select an output folder.")
        return

    # 檢查時間區間
    start_time = datetime.strptime(start_time_combobox.get(), '%Y/%m/%d %H:%M')
    end_time = datetime.strptime(end_time_combobox.get(), '%Y/%m/%d %H:%M')
    if start_time >= end_time:
        messagebox.showerror("Error", "Start time must be earlier than end time.")
        return
    
    with open(input_path.get(), "rb") as f:
        data = f.read()

    # 根據選擇的轉換類型進行轉換
    # 取代 or 正規替換掉空白都會導致長時間的延遲，所以放棄刪除空白
    if conversion_type.get() == "Binary":
        converted_data = ' '.join(format(byte, '08b') for byte in data)
    elif conversion_type.get() == "Decimal":
        converted_data = ' '.join(str(byte) for byte in data)
    elif conversion_type.get() == "Hexadecimal":
        converted_data = ' '.join(format(byte, '02x') for byte in data)
    elif conversion_type.get() == "Base64":
        converted_data = base64.b64encode(data).decode()

    # Test Code
    # RawData_Before_path = os.path.join(output_folder.get(), "RawData_Before.txt")
    # with open(RawData_Before_path, "w") as f:
    #     f.write(converted_data)

    # 將轉換後的數據依照100字元每行進行切割
    max_line_length = 100
    wrapped_converted_data = textwrap.fill(converted_data, width=max_line_length)
    
    # 將每一行與時間戳結合
    output_lines = []
    wrapped_lines = wrapped_converted_data.split('\n')
    total_lines = len(wrapped_lines)
    
    # 計算每行的時間間隔
    time_delta = (end_time - start_time) / total_lines if total_lines > 0 else timedelta(0)

    # 設置初始毫秒數
    previous_milliseconds = 0

    for i, line in enumerate(wrapped_lines):
        # 每行毫秒都需要隨機增加，但保證是遞增的
        random_milliseconds = random.randint(previous_milliseconds + 1, 999) if previous_milliseconds < 999 else 999
        current_time = start_time + time_delta * i + timedelta(milliseconds=random_milliseconds)
        
        # 更新上一行的毫秒值
        previous_milliseconds = random_milliseconds
        
        timestamp = current_time.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
        output_lines.append(f"{timestamp} {line.strip()}")

    # 寫入輸出文件
    output_path = os.path.join(output_folder.get(), "output.txt")
    with open(output_path, "w") as f:
        f.write("\n".join(output_lines))

    result_label.configure(text="Conversion successful, saved as output.txt")

def restore_file():
    # 檢查輸入是否是 .txt 檔案
    if not input_path.get().endswith(".txt"):
        result_label.configure(text="Please select a valid .txt file for restoration.")
        return

    with open(input_path.get(), "r") as f:
        data = f.readlines()  # 讀取所有行以便逐行處理

    # 去除每行的時間戳
    clean_data = []
    for line in data:
        # 使用正則表達式刪除時間戳
        clean_line = re.sub(r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\s+', '', line)
        clean_data.append(clean_line.strip())  # 去除行首尾空白

    # 將清理後的數據合併成一個字串
    clean_data = ' '.join(clean_data)

    # Test Code
    # RawData_After_path = os.path.join(output_folder.get(), "RawData_After.txt")
    # with open(RawData_After_path, "w") as f:
    #     f.write(clean_data)

    # 根據轉換類型來還原資料
    # if conversion_type.get() == "Binary":
    #     byte_data = bytearray([int(b, 2) for b in clean_data.split()])
    # elif conversion_type.get() == "Decimal":
    #     byte_data = bytearray([int(b) for b in clean_data.split()])
    # elif conversion_type.get() == "Hexadecimal":
    #     byte_data = bytearray([int(b, 16) for b in clean_data.split()])
    # elif conversion_type.get() == "Base64":
    #     byte_data = base64.b64decode(clean_data)
    # else:
    #     messagebox.showerror("Error", "Invalid conversion type.")
    #     return

    # 自動判斷數據類型
    if all(len(b) == 8 for b in clean_data.split()):
        byte_data = bytearray([int(b, 2) for b in clean_data.split()])
    elif all(b.isdigit() for b in clean_data.split()):
        byte_data = bytearray([int(b) for b in clean_data.split()])
    elif all(all(c in '0123456789abcdefABCDEF' for c in b) and len(b) % 2 == 0 for b in clean_data.split()):
        byte_data = bytearray([int(b, 16) for b in clean_data.split()])
    else:
        try:
            byte_data = base64.b64decode(clean_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decode data: {str(e)}")
            return

    # 將還原的檔案存為 .zip 檔案
    output_path = os.path.join(output_folder.get(), "restored.zip")
    with open(output_path, "wb") as f:
        f.write(byte_data)

    result_label.configure(text=f"Restoration successful, saved as {output_path}")

def show_about():
    messagebox.showinfo("About", 
                        "This is a file conversion tool.\n\n"
                        "Instructions:\n"
                        "1. Select a compressed file (zip/7z).\n"
                        "2. Choose an output folder.\n"
                        "3. Choose the conversion type (Binary, Decimal, Hexadecimal, Base64).\n"
                        "4. Convert the file and save the result as a .txt file.\n"
                        "5. You can also restore the file to its original compressed format.\n\n"
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

# 建立主視窗
root = ctk.CTk()
root.title("File Conversion Tool")
root.geometry("700x400")

# 建立 StringVar 來儲存檔案路徑與轉換選項
input_path = ctk.StringVar()
output_folder = ctk.StringVar()
conversion_type = ctk.StringVar(value="Binary")

# 標籤及按鈕設計
title_label = ctk.CTkLabel(root, text="File Conversion Tool Ver. 1", font=ctk.CTkFont(size=24, weight="bold"))
title_label.pack(pady=20)

# 選擇檔案部分
input_frame = ctk.CTkFrame(root)
input_frame.pack(pady=10, padx=20, fill="x")

input_frame.grid_columnconfigure(1, weight=1)

input_label = ctk.CTkLabel(input_frame, text="Select Compressed File:", width=150)
input_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

input_entry = ctk.CTkEntry(input_frame, textvariable=input_path, width=300)
input_entry.grid(row=0, column=1, padx=10, pady=5)

input_button = ctk.CTkButton(input_frame, text="Browse", command=select_input_file)
input_button.grid(row=0, column=2, padx=10, pady=5, sticky="e")

# 選擇資料夾部分
output_frame = ctk.CTkFrame(root)
output_frame.pack(pady=10, padx=20, fill="x")

output_frame.grid_columnconfigure(1, weight=1)

output_label = ctk.CTkLabel(output_frame, text="Select Output Folder:", width=150)
output_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

output_entry = ctk.CTkEntry(output_frame, textvariable=output_folder, width=300)
output_entry.grid(row=0, column=1, padx=10, pady=5)

output_button = ctk.CTkButton(output_frame, text="Browse", command=select_output_folder)
output_button.grid(row=0, column=2, padx=10, pady=5, sticky="e")

# 選擇轉換類型部分
conversion_frame = ctk.CTkFrame(root)
conversion_frame.pack(pady=10, padx=20, fill="x")

conversion_frame.grid_columnconfigure(1, weight=1)

conversion_label = ctk.CTkLabel(conversion_frame, text="Select Conversion Type:", width=150)
conversion_label.pack(side="left", padx=10)

conversion_menu = ctk.CTkOptionMenu(conversion_frame, variable=conversion_type, values=["Binary", "Decimal", "Hexadecimal", "Base64"])
conversion_menu.pack(side="left", padx=10)

# Log 轉換格式調整部分 (設定開始和結束時間)
obfuscation_frame = ctk.CTkFrame(root)
obfuscation_frame.pack(pady=10, padx=20, fill="x")

obfuscation_label = ctk.CTkLabel(obfuscation_frame, text="Log Obfuscation Time:", width=150)
obfuscation_label.pack(side="left", padx=10)

time_options = generate_time_options()

start_time_combobox = ctk.CTkComboBox(obfuscation_frame, values=time_options, width=150)
start_time_combobox.set(time_options[0])
start_time_combobox.pack(side="left", padx=10)

end_time_label = ctk.CTkLabel(obfuscation_frame, text="~")
end_time_label.pack(side="left", padx=10)

end_time_combobox = ctk.CTkComboBox(obfuscation_frame, values=time_options, width=150)
end_time_combobox.set(time_options[-1])
end_time_combobox.pack(side="left", padx=10)

# 按鈕區域
button_frame = ctk.CTkFrame(root)
button_frame.pack(pady=10, padx=20, fill="x")

button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)
button_frame.grid_columnconfigure(2, weight=1)

convert_button = ctk.CTkButton(button_frame, text="Convert", command=convert_file, width=150)
convert_button.grid(row=0, column=0, padx=20, pady=10)

restore_button = ctk.CTkButton(button_frame, text="Restore", command=restore_file, width=150)
restore_button.grid(row=0, column=1, padx=20, pady=10)

about_button = ctk.CTkButton(button_frame, text="About", command=show_about, width=150)
about_button.grid(row=0, column=2, padx=20, pady=10)

# 顯示結果的標籤
result_label = ctk.CTkLabel(root, text="")
result_label.pack(pady=20)

# 啟動主循環
root.mainloop()
