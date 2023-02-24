import os

def restart_program():
    print("test")

file_size_stored = os.stat('application.ini').st_size

while True:
  try:
    file_size_current = os.stat('application.ini').st_size
    if file_size_stored != file_size_current:
      print("changed")
      file_size_stored = file_size_current
  except: 
    print("fail")


