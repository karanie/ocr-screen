import sys
import multiprocessing
import core
import core.settings_win
import core.systray
import core.context

def run_win32():
    ctx = core.context.MainContext()

    main_p = multiprocessing.Process(target=core.main, args=(ctx,))
    settings_p = multiprocessing.Process(target=core.settings_win.main, args=(ctx,))
    systray_p = multiprocessing.Process(target=core.systray.main, args=(ctx,))

    main_p.start()
    settings_p.start()
    systray_p.start()

    main_p.join()
    settings_p.join()
    systray_p.join()

def main():
    if sys.platform == "win32":
        print("Windows Operating System Detected")
        run_win32()
    elif sys.platform == "linux":
        print("This program only supported in Windows")

if __name__ == "__main__":
    main()
