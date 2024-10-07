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

# Init Vars
class colors:
    red = Fore.LIGHTRED_EX
    green = Fore.LIGHTGREEN_EX
    blue = Fore.LIGHTBLUE_EX
    purple = Fore.MAGENTA
    reset = Style.RESET_ALL
riftFolder = f"{os.path.expanduser('~')}/.rift/"
entryIndex = 0
homeFolder = os.path.expanduser('~')

# Color printing
def cprint(text, color=colors.reset):
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
    time.sleep(2)

def welcomeScreen():
    clear()
    try:
        if sys.argv[1] != "": # Check if there was URL in the command
            loadRepo(f"https://{sys.argv[1]}/repo.rift")
    except IndexError:
        cprint("Welcome to Rift Rewrite", colors.purple)
        url = input("URL: ")
        loadRepo(f"https://{url}/repo.rift")

def loadRepo(url):
    clear()
    cprint(f"Loading {url}", colors.purple)
    try:
        r = requests.get((url), allow_redirects=True)
        open(f"{riftFolder}repo.rift", 'wb').write(r.content)
    except FileNotFoundError:
        exit(1)

def drawUI():
    index = 0
    with open(f"{riftFolder}repo.rift", "r") as f:
        lines = f.readlines()
        for i in lines:
            i = i.removesuffix("\n")
            entry = i.split(";")
            if index == entryIndex:
                cprint(entry[0], colors.green)
                global selectedFile
                selectedFile = entry[1]
            else:
                print(entry[0])
            index = index + 1

def commandPrompt():
    command = (input(f"{colors.purple}> {colors.reset}")).split(" ")
    if command[0] == "i":
        try:
            global entryIndex
            entryIndex = int(command[1]) - 1
        except IndexError:
            errorHandle("Invalid index, try i 2", 2)
    elif command[0] == "dl":
        downloadFile(selectedFile)
    elif command[0] == "exit":
        clear()
        sys.exit(0)
    else:
        errorHandle("Invalid command", 1)

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
                except IOError:
                    errorHandle("Chunk failed to write", 3)
        cprint("Done!", colors.green)

welcomeScreen()
while True:
    clear()
    drawUI()
    commandPrompt()