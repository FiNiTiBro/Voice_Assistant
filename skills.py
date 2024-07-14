import os, webbrowser, sys, requests, subprocess, winreg, pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 180)

async def speaker(text):
    engine.say(text)
    engine.runAndWait()

def get_default_browser_path():
    with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"http\shell\open\command") as key:
        browser_path, _ = winreg.QueryValueEx(key, None)
        return browser_path.split('"')[1]

def browser():
    default_browser_path = get_default_browser_path()
    subprocess.Popen(default_browser_path)
    print("Браузер запущен!")

def open_vk():
    webbrowser.open('https://vk.com/al_feed.php')
def open_youtube():
    webbrowser.open('https://www.youtube.com/')
def open_yandex():
    webbrowser.open('https://dzen.ru/')

def offBot():
    sys.exit()

def offPc():
    os.system('shutdown /s /t 10 /c "Пятница желает Вам сладких снов"')
    print("Пк выключен")

def sonpc():
    os.system('shutdown /s')
    print("Пк в сонном режиме")