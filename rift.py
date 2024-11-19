#!/usr/bin/python3

#############################################################
#                                                           #
# File created by 0hStormy                                  #
#                                                           #
#############################################################

# Imports
from colorama import Fore, Style
import requests
import os
import platform
import sys
import time
import termios
import tty
from datetime import datetime

# Color printing
def cprint(text, color):
    print(f"{color}{text}{colors.reset}")

# Determine clear command
def clear():
    if platform.system() == 'Windows':
        clearCMD = 'cls'
    else:
        clearCMD = 'clear'
    os.system(clearCMD)


def errorHandle(message, code):
    print(f'{colors.red}Error {str(code)}:{colors.reset} {message}')
    log(message, 2)
    time.sleep(2)

def welcomeScreen():
    clear()
    try:
        if sys.argv[2] != "":
            global cliMode
            cliMode = True
            loadRepo(sys.argv[1])
    except IndexError:
        pass
    try:
        if sys.argv[1] != "": # Check if there was URL in the command
            if sys.argv[1] == "local":
                loadRepo("local")
            else:
                loadRepo(sys.argv[1])
    except IndexError:
        cprint("Welcome to Rift Rewrite", colors.purple)
        url = input("URL: ")
        loadRepo(url)

def loadRepo(url):
    if cliMode is False:
        clear()
        cprint(f"Loading {url}", colors.purple)
    if not url == "local":
        try:
            r = requests.get((f"https://{url}/repo.rift"), allow_redirects=True)
            open(f"{riftFolder}repo.rift", 'wb').write(r.content)
        except FileNotFoundError:
            errorHandle("Could not find a repository file!", 3)
            exit(1)
    else:
        log("Using local Repository, beware there may be issues!", 1)
        cprint("Using local Repository, beware there may be issues!", colors.yellow)
        if os.path.isfile(f"{riftFolder}repo.rift") is False:
            errorHandle("Could not find a repository file!", 3)
            exit(1)
            

def drawUI():
    clear()
    index = 0
    with open(f"{riftFolder}repo.rift", "r") as f:
        lines = f.readlines()
        cprint(f"{len(lines)} files available", colors.purple)
        drawLine()
        for i in lines:
            i = i.removesuffix("\n")
            entry = i.split(";")
            if index == entryIndex:
                if cliMode is False:
                    cprint(f"{index + 1}: {entry[0]}", colors.green)
                else:
                    print(f"{index + 1}: {entry[0]}")
                global selectedFile
                description = entry[2]
                selectedFile = entry[1]
            else:
                print(f"{index + 1}: {entry[0]}")
            index = index + 1
        drawLine()
        if cliMode is False:
            print(f"Description: {description}")
        drawLine()
    log("Drew UI")

def drawLine():
    if cliMode is False:
        terminalX = os.get_terminal_size().columns
        print("─" * terminalX)

def commandPrompt():
    global cmdInput
    print(f"{colors.purple}> {colors.reset}{cmdInput}")
    orig_settings = termios.tcgetattr(sys.stdin)

    tty.setcbreak(sys.stdin)
    x = 0
    while x != chr(27):
        x = sys.stdin.read(1)[0]
        cmdInput = cmdInput + x
        if x == "\n":
            commandList(cmdInput.removesuffix("\n").split(" "))
            drawUI()
            cmdInput = ""
            return
        elif x in ("\x08", "\x7f"):
            cmdInput = cmdInput[:-2]
            drawUI()
            return
        else:
            drawUI()
            return
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)

def commandList(command):
    if command[0] == "i":
        try:
            global entryIndex
            entryIndex = int(command[1]) - 1
        except IndexError:
            errorHandle("Invalid index, try i 2", 2)
        except ValueError:
            errorHandle("Invalid index, try i 2", 2)
    elif command[0] == "dl":
        downloadFile(selectedFile)
    elif command[0] == "exit":
        clear()
        endLogging()
        sys.exit(0)
    else:
        errorHandle(f"Invalid command: {command[0]}", 1)

def downloadFile(url):
    fileName = os.path.basename(url)
    r = requests.get(url, stream=True)

    with open(f"{homeFolder}/Downloads/{fileName}", "wb") as f:
        chunkSize = 8184
        totalChunks = 0
        for chunk in r.iter_content(chunk_size=chunkSize):
            if chunk:
                totalChunks = totalChunks + chunkSize
                cprint(f"{str(round((totalChunks / 1048576), 2)).removesuffix(".0")}mb downloaded...", colors.green)
                try:
                    f.write(chunk)
                    log(f"{str(round((totalChunks / 1048576), 2)).removesuffix(".0")}mb downloaded...")
                except IOError:
                    errorHandle("Chunk failed to write", 3)
                    log("File Chunk failed to write!", 2)
        cprint("Done!", colors.green)
        log(f"Finished downloading {fileName}")

def checkForLogFolder():
    if os.path.exists(f"{riftFolder}/logs/") is False:
        os.mkdir(f"{riftFolder}/logs/")

def log(message, severity=0):
    checkForLogFolder()
    if severity == 0:
        svString = "Info"
    elif severity == 1:
        svString = "Warn"
    elif severity == 2:
        svString = "Error"
    else:
        svString == "Unknown"
    with open(f"{riftFolder}/logs/latest.log", "a") as f:
        f.write(f"[{svString}] {message}\n")

def cliParse():
    if sys.argv[2] == "list":
        drawUI()
    if sys.argv[2] == "dl":
        print("Downloading...")
        try:
            global entryIndex
            with open(f"{riftFolder}repo.rift", "r") as f:
                lines = f.readlines()
                entry = lines[int(sys.argv[3]) - 1].split(";")
            selectedFile = entry[1]
            downloadFile(selectedFile)
        except TypeError:
            errorHandle("No index specified, find index with rift [URL] list", 1)

def endLogging():
    log("Finished Logging!")
    os.rename(f"{riftFolder}/logs/latest.log", f"{riftFolder}/logs/{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}.log")

# Init Vars
class colors:
    red = Fore.LIGHTRED_EX
    green = Fore.LIGHTGREEN_EX
    blue = Fore.LIGHTBLUE_EX
    purple = Fore.MAGENTA
    yellow = Fore.LIGHTYELLOW_EX
    reset = Style.RESET_ALL
riftFolder = f"{os.path.expanduser('~')}/.rift/"
entryIndex = 0
homeFolder = os.path.expanduser('~')
lastTermX = 0
lastTermY = 1
terminalX = 0
terminalY = 1

# Init Logging
checkForLogFolder()

welcomeScreen()
if cliMode is False:
    cmdInput = ""
    drawUI()
    while True:
        if terminalX != lastTermX:
            drawUI()
        if terminalY != lastTermY:
            drawUI()
        terminalY = int(os.get_terminal_size().lines)
        terminalX = int(os.get_terminal_size().columns)
        commandPrompt()
else:
    cliParse()