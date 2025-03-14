import bz2
import os
import pathlib

def processStatusDump(FOLDER_NAME):

if not os.path.exists(f"{FOLDER_NAME}/stats/dumps/{pg_id}.log"):
    print(f"File {FOLDER_NAME}/stats/dumps/{pg_id}.log does not exit")
    return False

desktop = pathlib.Path("Desktop")
for item in desktop.iterdir():
...     print(f"{item} - {'dir' if item.is_dir() else 'file'}")


myfile =  'c:\\my_dir\\random.txt.bz2'
newfile = 'c:\\my_dir\\random_10000.txt'

stream = bz2.BZ2File(myfile)
with open(newfile, 'w') as f:
  for i in range(1,10000):
    f.write(stream.readline())