import pyautogui
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import smtplib
import subprocess
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import psutil
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import requests
import tkinter as tk
import math
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import apikey

i = 0
# Initialize the speech engine
engine = pyttsx3.init('sapi5')

# Retrieve the list of available voices
voices = engine.getProperty('voices')

# Set the first voice from the available voices list
engine.setProperty('voice', voices[0].id)

# Adjust the rate of speech for the selected voice (you can experiment with different values)
engine.setProperty('rate', 185)  # Adjust the rate as per your preference

# Function to speak out the audio
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# Function is Notepad Open
def open_notepad():
    # Open Notepad using subprocess
    subprocess.Popen(["notepad.exe"])

# In Notepad Type
def type_in_notepad(text):
    # Type text into Notepad
    pyautogui.typewrite(text)

def calculate_expression(expression):
    try:
        result = eval(expression)
        return result
    except Exception as e:
        print("Error:", e)
        return "Sorry, I couldn't calculate that."

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
creds = None

def authenticate():
    global creds
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

def change_volume(percent):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        current_volume = volume.GetMasterVolume()
        new_volume = max(0.0, min(1.0, current_volume + percent / 100.0))
        volume.SetMasterVolume(new_volume, None)

        # Convert percentage to string
        percent_str = str(percent) if percent >= 0 else "minus " + str(abs(percent))
        speak(f"Volume changed by {percent_str} percent")

# Replace 'YOUR_API_KEY' with your actual API key from Alpha Vantage
API_KEY = 'O2ALJBYH0QWH0MP3'

# Example API request to get stock data
def get_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data

if __name__ == "__main__":
    symbol = 'AAPL'  # Example stock symbol (Apple Inc.)
    stock_data = get_stock_data(symbol)
    print(stock_data)  # This will print the stock data returned by the API


def stop_music():
    # Iterate through all running processes
    for proc in psutil.process_iter(['pid', 'name']):
        # Check if the process name is 'wmplayer.exe' (Windows Media Player)
        if proc.info['name'] == 'wmplayer.exe':
            # Terminate the process
            os.kill(proc.info['pid'], 9)
            speak("Music stopped")
            return
    speak("No music is currently playing")
def add_event(summary, start_time, end_time):
    service = build('calendar', 'v3', credentials=creds)
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Your_Time_Zone_Here',  # e.g., 'America/New_York'
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Your_Time_Zone_Here',
        },
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

# Function to sleep the computer
def sleep_computer():
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")  # Command to put the computer to sleep
    speak("Computer is going to sleep")

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")

    elif hour>=12 and hour<18:
        speak("Good Afternoon!")

    else:
        speak("Good Evening!")

    speak("I am Jarvis Sir. Please tell me how may I help you")

def takeCommand():
    #It takes microphone input from the user and returns string output

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        # print(e)
        print("Say that again please...")
        return "None"
    return query

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('youremail@gmail.com', 'your-password')
    server.sendmail('youremail@gmail.com', to, content)
    server.close()


if __name__ == "__main__":
    wishMe()
    while True:
    # if 1:
        query = takeCommand().lower()

        # Logic for executing tasks based on query
        if 'who is' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'open youtube' in query:
            webbrowser.open("youtube.com")

        elif 'open google' in query:
            webbrowser.open("google.com")

        elif 'open stackoverflow' in query:
            webbrowser.open("stackoverflow.com")

        elif 'play music' in query:
            music_dir = 'C:\\Users\\Mr.Robot\\Music'  # Corrected path format
            songs = os.listdir(music_dir)
            print(songs)
            os.startfile(os.path.join(music_dir, songs[0]))
            speak("Song Is Played Sir")

        elif 'next song' in query:
            i = (i + 1) % len(songs)
            os.startfile(os.path.join(music_dir, songs[i]))
            speak("Sir, Song Is Change")

        elif 'previous song' in query:
            i = (i - 1) % len(songs)
            os.startfile(os.path.join(music_dir, songs[i]))
            speak("Sir, Previous Song is played")

        elif 'stop music' in query:
            stop_music()

        elif 'change volume ' in query:
                # Extracting the percentage from the query
                try:
                    percent = int(query.split("volume change")[1].strip().split()[0])
                    change_volume(percent)
                except ValueError:
                    speak("Sorry, I couldn't understand the percentage.")
                    continue

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")

        elif 'open pycharm' in query:
            codePath = "C:\Program Files\JetBrains\PyCharm Community Edition 2023.3.5\bin\\pycharm64.exe"
            os.startfile(codePath)

        elif 'close pycharm' in query:
            os.system("taskkill /f /im pycharm64.exe")

        elif 'open code' in query:
            codePath = "C:\\Users\\Mr.Robot\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            os.startfile(codePath)

        elif 'sleep computer' in query:
            sleep_computer()

        elif 'open whatsapp' in query:
            pass

        elif 'clear screen' in query:
            pyautogui.hotkey('win', 'd')
            speak("Sir, Screen is Cleared")

        elif 'change window' in query:
            pyautogui.hotkey('alt','tab')
            speak("Sir, Window is change")

        elif 'show all window' in query:
            pyautogui.hotkey('win','tab')
            speak("All window is there ,sir")

        elif 'next window' in query:
            pyautogui.hotkey('rightarrow')

        elif 'select the window' in query:
            pyautogui.hotkey('enter')

        elif 'close code' in query:
            os.system("taskkill /f /im Code.exe")
            speak("Visual Studio Code is closed, Sir!")

        elif 'thanks' in query:
            speak("It's my pleasure, sir.")

        elif 'email to harry' in query:
            try:
                speak("What should I say?")
                content = takeCommand()
                to = "makarandjadhavhalda@gmail.com"
                sendEmail(to, content)
                speak("Email has been sent!")
            except Exception as e:
                print(e)
                speak("Sorry my friend harry bhai. I am not able to send this email")

        elif "schedule meeting" in query:
                speak("Please provide meeting details.")
                speak("What is the meeting title?")
                meeting_title = takeCommand().lower()
                speak("When should the meeting start? Please provide date and time.")
                start_time = takeCommand().lower()

                speak("When should the meeting end? Please provide date and time.")
                end_time = takeCommand().lower()

                # Add the event to Google Calendar
                add_event(meeting_title, start_time, end_time)

        elif "search news" in query:
            # Add news search functionality here
            pass

        elif "how r u" in query:
            speak("Thank you for asking! I'm just a program, so I don't have feelings like humans do, but I'm functioning perfectly fine.")

        elif "send text message" in query:
            # Add text message sending functionality here
            pass

        elif "take notes" in query:
            open_notepad()
            speak("What Would you like to write in the notes?")

        elif "calculate" in query:
            expression = query.replace("calculate", "").strip()
            result = calculate_expression(expression)
            speak(f"The result of {expression} is {result}")

        elif "define" in query:
            # Add definition lookup functionality here
            pass

        elif "schedule meeting" in query:
            # Add meeting scheduling functionality here
            pass

        elif "check calendar" in query:
            # Add calendar checking functionality here
            pass

        elif "translate" in query:
            # Add translation functionality here
            pass

        elif "set timer" in query:
            # Add timer setting functionality here
            pass

        elif "find restaurant" in query:
            # Add restaurant search functionality here
            pass

        elif "stocks" in query:
            speak(f"The Stock Data is{get_stock_data}")

        elif "play podcast" in query:
            # Add podcast playing functionality here
            pass

        elif "control smart home" in query:
            # Add smart home control functionality here
            pass

        else:
            print("Chatting...")