import os
import glob
import pandas as pd
import msvcrt

tgt_dir = "C:\\Users\\R123828878\\Downloads\\20250107"

if not os.path.isdir(tgt_dir):
    print(f"directory {tgt_dir} not found, exit")

excel_files = glob.glob(f"{tgt_dir}\\{tgt_dir.split("\\")[-1]}\\*")

checked_dir = tgt_dir + "\\checked"
os.makedirs(checked_dir, exist_ok=True)

def getkey(s=''):
    assert type(s) is str
    if len(s):
        print(s)

    while True:
        if msvcrt.kbhit():
            return msvcrt.getch().decode()

for fp in sorted(excel_files):
    print("="*30)
    print(f"id from {fp.split('\\')[-1]}")
    data = pd.read_excel(fp, header=None)
    for i, row in data.iterrows():
        print("%2d / %2d" % (i+1, len(data)) , row.to_list())

        ch = getkey()
        if ch == "q": # exit
            exit()
        if ch == "s": # skip
            break

    print(f"end of file {fp}")
    ch = getkey("move to checked?[y]") #input()
    if ch == 'y':
        new_fp = f"{checked_dir}\\{fp.split('\\')[-1]}"
        os.rename(fp, new_fp)
        print(f"saved to {new_fp}")
    print("="*30)