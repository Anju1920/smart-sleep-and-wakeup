# Smart Sleep and Wake-Up System 😴⏰


## Basic Details
### Team Name: Team Useless


### Team Members
- Team Lead: Amurtha Kaimal - College of Engineering Alappuzha
- Member 2: Anju M B - College of Engineering Alappuzha

### Project Description
The **Smart Sleep and Wake-Up System** is a computer-vision-based project designed to make sleeping and waking up more interactive.

The system plays a relaxing song to help the user sleep and uses a webcam to monitor the user's eyes. At wake-up time, a wake-up voice is played repeatedly until the user opens their eyes.

### The Problem (that doesn't exist)
Sometimes people don't wake up even after hearing their alarm.

So we decided to solve the extremely serious problem:

**"What if my alarm is shouting at me, but my eyes are still closed?"** 😴😂

### The Solution (that nobody asked for)
We created a smart alarm that doesn't simply make noise and give up.

The system uses a webcam to detect the user's eye state. When it is time to wake up, the wake-up voice continues while the user's eyes remain closed.

Once the user opens their eyes, the system detects the change and stops the wake-up sound.

Because apparently, the alarm needs proof that you are actually awake. 👀😂

## Technical Details
### Technologies/Components Used

For Software:
- **Language:** Python
- **Computer Vision:** OpenCV
- **Face/Eye Detection:** MediaPipe
- **Numerical Processing:** NumPy
- **Audio Playback:** Pygame
- **Development Tool:** Visual Studio Code


### Implementation
For Software:

# Installation

Install the required Python packages:

```bash
pip install opencv-python
pip install mediapipe
pip install numpy
pip install pygame

#Run
.venv\Scripts\python.exe activity_alert.py

###Project Documentation

# Screenshots

![The webcam detects that the user's eyes are open, indicating that the user is awake. The system recognizes the change in eye condition and stops the wake-up voice.](open eyes.jpeg)

![The webcam detects that the user's eyes are closed. The system continues playing the wake-up voice until the user opens their eyes.](closeeye.jpeg)
 
# Diagram

### complete flow is:

**Webcam → Eye Detection → Eyes Open → Voice 1 once**

**Webcam → Eye Detection → Eyes Closed → 10 seconds → Voice 2 repeats → Eyes Open → Voice 2 stops → Voice 1 once**


