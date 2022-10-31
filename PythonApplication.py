import os
import time
from enum import Enum
from pydoc import text
from tkinter import *
import tkinter.font as font
from tkinter import filedialog
from tkinter import ttk
from pygame import mixer
from mutagen.mp3 import MP3

class playerState(Enum):
    STOP = 1
    PLAY = 2
    PAUSE = 3

currentState = playerState.STOP

fullpathTracklist = list()

startTime = 0

# Change volume
def SlideVolume(x):
    mixer.music.set_volume(float(x))

# Change song position
def SlidePos(x):
    curr_song=trackList.curselection()
    if curr_song and currentState!=playerState.STOP:
        mixer.music.play(start=int(float(x)))
        global startTime
        startTime = int(float(x))

# Display current playtime in status bar and update slider position
def Playtime():
    global startTime
    currentTime = mixer.music.get_pos() / 1000
    if int(currentTime) != int(posSlider.get()):
        currentTime = currentTime + startTime
    convertedTime = time.strftime('%M:%S', time.gmtime(currentTime))

    curr_song=trackList.curselection()
    if curr_song:
        curr_song = curr_song[0]
        song = fullpathTracklist[curr_song]

        song_mut = MP3(song)
        global songLength
        songLength = song_mut.info.length
        convertedLength = time.strftime('%M:%S', time.gmtime(songLength))

        statusBar.config(text=f'{convertedTime} of {convertedLength}  ')
        sliderMax = int(songLength)
        posSlider.config(to=sliderMax,value=int(currentTime))
    else:
        statusBar.config(text='  ')

    if currentState == playerState.PLAY:
        if mixer.music.get_busy():
            statusBar.after(1000, Playtime)
        else:
            startTime = 0
            if loopSong.get():
                mixer.music.play(-1)
            else:
                Next()
            Playtime()

# Refresh UI
def RefreshUI():
    print('Refresh UI')
    if currentState==playerState.PLAY:
        playButton.configure(text='Play', state='disabled')
        pauseButton.configure(state='normal')
        stopButton.configure(state='normal')
        songsMenu.entryconfigure(0, state='disabled', label='Play', command=Play)
        songsMenu.entryconfigure(1, state='normal')
        songsMenu.entryconfigure(2, state='normal')
    elif currentState==playerState.PAUSE:
        playButton.configure(text='Resume', state='normal', command=Resume)
        pauseButton.configure(state='disabled')
        stopButton.configure(state='normal')
        songsMenu.entryconfigure(0, state='normal', label='Resume', command=Resume)
        songsMenu.entryconfigure(1, state='disabled')
        songsMenu.entryconfigure(2, state='normal')
    else:
        playButton.configure(text='Play', state='normal', command=Play)
        pauseButton.configure(state='disabled')
        stopButton.configure(state='disabled')
        songsMenu.entryconfigure(0, state='normal', label='Play', command=Play)
        songsMenu.entryconfigure(1, state='disabled')
        songsMenu.entryconfigure(2, state='disabled')

# Add song to the player list
def AddSongs():
    temp=filedialog.askopenfilenames(initialdir="Music/",title="Choose songs to add to the tracklist", filetypes=(("mp3 files","*.mp3"),))
    ##loop through every item in the list to insert in the listbox
    for s in temp:
        global fullpathTracklist
        fullpathTracklist.append(s)
        s=os.path.basename(s)
        trackList.insert(END,s)
    print(fullpathTracklist)
     
# Delete the selected song from the list
def DeleteSong():
    global fullpathTracklist
    curr_song=trackList.curselection()
    if curr_song:
        fullpathTracklist.pop(curr_song[0])
        trackList.delete(curr_song[0])
        print(fullpathTracklist)
    
# Play the song
def Play():
    global currentState
    curr_song=trackList.curselection()
    if curr_song:
        currentState = playerState.PLAY
        index=curr_song[0]
        global currentTrack
        currentTrack.set(trackList.get(index))
        global fullpathTracklist
        song=fullpathTracklist[index]
        mixer.music.load(song)
        mixer.music.play()
        RefreshUI()
        Playtime()

# Pause the song 
def Pause():
    global currentState
    currentState = playerState.PAUSE
    mixer.music.pause()
    RefreshUI()

# Stop the song 
def Stop():
    global currentState
    currentState = playerState.STOP
    global currentTrack
    currentTrack.set('')
    mixer.music.stop()
    trackList.selection_clear(ACTIVE)
    RefreshUI()
    posSlider.config(value=0)

# Resume the song 
def Resume():
    global currentState
    currentState = playerState.PLAY
    mixer.music.unpause()
    RefreshUI()
    Playtime()

# Select the previous song
def Previous():
    prevSong=trackList.curselection()
    prevSong=prevSong[0]-1
    if prevSong < 0:
        prevSong=trackList.size()-1
    global currentTrack
    currentTrack.set(trackList.get(prevSong))
    global fullpathTracklist
    song=fullpathTracklist[prevSong]
    mixer.music.load(song)
    mixer.music.play()
    trackList.selection_clear(0,END)
    trackList.activate(prevSong)
    trackList.selection_set(prevSong)

# Select the next song
def Next():
    nextSong=trackList.curselection()
    nextSong=nextSong[0]+1
    if nextSong >= trackList.size():
        nextSong=0
    global currentTrack
    currentTrack.set(trackList.get(nextSong))
    global fullpathTracklist
    song=fullpathTracklist[nextSong]
    mixer.music.load(song)
    mixer.music.play()
    trackList.selection_clear(0,END)
    trackList.activate(nextSong)
    trackList.selection_set(nextSong)

# Create window
root=Tk()
root.title('Music Player App ')
root.resizable(False, False)
# Initialize mixer
mixer.init()

# Current Track String
currentTrack = StringVar()
currentTrack.set('')

# Global Frame
frame = Frame(root)
frame.grid(column=0, row=0)

# Tracklist Frame
tlFrame = Frame(frame)
tlFrame.grid(column=0, row=0, padx=5, pady=5)
# Tracklist Listbox
trackList=Listbox(tlFrame,height=10,selectmode=SINGLE,bg="black",fg="white",width=100,font=('Arial'),selectbackground="gray",selectforeground="black")
trackList.grid(column=0, row=0)
# Tracklist Scrollbar
tlScroll=Scrollbar(tlFrame, orient=VERTICAL, command=trackList.yview)
tlScroll.grid(column=1, row=0, sticky=(N,S))
trackList['yscrollcommand'] = tlScroll.set

# Volume Frame
volumeFrame = LabelFrame(frame,text='Volume',width=100)
volumeFrame.grid(column=1, row=0, padx=10)
# Volume Slider
volumeSlider = ttk.Scale(volumeFrame,from_=1,to=0,orient=VERTICAL,value=1,command=SlideVolume, length=150)
volumeSlider.pack(pady=5)

# Current Track Frame
songFrame = Frame(frame)
songFrame.grid(row=1, pady=5)
# Current Track Label
songLabel = Label(songFrame,textvariable=currentTrack,relief='raised',anchor='w',width=100,font=('Arial'),bg="black",fg="white")
songLabel.grid(column=0, row=0)

# Define button font
defined_font = font.Font(family='Arial')
# Button Frame
buttonFrame = Frame(frame)
buttonFrame.grid(row=3, pady=5)
# Play Button
playButton=Button(buttonFrame,text="Play",width=7,command=Play)
playButton['font']=defined_font
playButton.grid(row=0, column=0)
# Pause Button 
pauseButton=Button(buttonFrame,text="Pause",width=7,command=Pause,state='disabled')
pauseButton['font']=defined_font
pauseButton.grid(row=0, column=1)
# Stop Button
stopButton=Button(buttonFrame,text="Stop",width=7,command=Stop,state='disabled')
stopButton['font']=defined_font
stopButton.grid(row=0, column=2)
# Previous Button
previousButton=Button(buttonFrame,text="Prev",width=7,command=Previous)
previousButton['font']=defined_font
previousButton.grid(row=0, column=3)
# Next Button
nextButton=Button(buttonFrame,text="Next",width=7,command=Next)
nextButton['font']=defined_font
nextButton.grid(row=0, column=4)
# Repeat Checkbutton
loopSong = BooleanVar(value=False)
checkRepeat = ttk.Checkbutton(buttonFrame,text='Repeat',variable=loopSong,onvalue=True,offvalue=False)
checkRepeat.grid(row=0, column=5)

# Position Slider
posSlider = ttk.Scale(frame,from_=0,to=100,orient=HORIZONTAL,value=0,command=SlidePos, length=360)
posSlider.grid(row=4, pady=5)

# Status Bar
statusBar = Label(frame, text='', bd=1, relief=GROOVE, anchor=E)
statusBar.grid(row=5, column=0, columnspan=2, sticky="nsew")


# Menu
menuBar=Menu(root)
root.config(menu=menuBar)
# File Tab
fileMenu=Menu(menuBar, tearoff=False)
menuBar.add_cascade(label="File",menu=fileMenu)
fileMenu.add_command(label="Add songs",command=AddSongs)
fileMenu.add_command(label="Delete song",command=DeleteSong)
fileMenu.add_separator()
fileMenu.add_command(label="Exit",command=root.destroy)
# Songs Tab
songsMenu=Menu(menuBar, tearoff=False)
menuBar.add_cascade(label="Songs",menu=songsMenu)
songsMenu.add_command(label="Play",command=Play)
songsMenu.add_command(label="Pause",command=Pause, state='disabled')
songsMenu.add_command(label="Stop",command=Stop, state='disabled')
songsMenu.add_separator()
songsMenu.add_command(label="Previous",command=Previous)
songsMenu.add_command(label="Next",command=Next)

mainloop()