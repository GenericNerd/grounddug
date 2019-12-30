import os
while True:
    exit_code = os.system("python pxb2.py")
    if exit_code == 100:
        print("\nRestarting...")
    if exit_code == 0:
        break
