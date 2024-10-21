## UDE Alpha v1.0 Oct 21st 2024 ##
--------------------------------------
#/HOW TO USE/#
To setup, just download the zip under releases in github. Then, extract the contents into whatever folder you'd like.
For Windows users, download UDEwin.zip. For Mac users, download UDEmac.zip. For Linux users, I will eventually add a zip with my own personal scripts, but they require additional setup and a knowledge of bash to use.

All you really gotta do to use things in this program is set up the config file to your liking. Try not to mess up the formatting since it may cause unexpected errors.

For UDG, you can get a free API key from google's ai studio, and you can change other generation instructions as you please. Google AI Studio has some documentation for it if you are confused or want to add more settings in a fork.

For UDP, you can change the delays to modify the speed at which it simulates typing, so you can either have it run at full speed or change it to be more similar to your own typing speed.

For HOTKEYS, it explains itself. You can change key combos to whatever keys you like, and clicking those will run different things like pasting, killswitches, and calling the gemini api. This is VERY IMPORTANT! Without killswitches, it is very hard to close these programs, especially UDP!

To start up the program, just run the executable file and it will stay open in the background, waiting for you to press any hotkeys. The config file contains all the hotkeys as well, so you can change them if you want.

To update the hotkeys/config, you need to press the default keybind for it which is also in the config folder. You can change it if you wish though. You can also update the config/hotkeys by just closing out the program and opening it again.

I will eventually add visual icons to show what module is running, but for now that won't be the case.

#/HOW TO USE/#
--------------------------------------
#/ABOUT/#
UDE is a windows port for all my personal scripts that I use for nefarious actions (cheating). I will eventually post the bash versions of the scrips for people who use linux.

UDG calls google's gemini api and uses your copied text as the prompt, then sends the result back to you clipboard completely undetected.

UDP types out what is in your clipboard like a human would.

#/ABOUT/#
--------------------------------------
#/DEBUGGING/#
The logs folder will contain most information being sent across the program, so you can easily see the what's going on and what errors are popping up. 

As long as you don't mess up the formatting of the cfg files or context json then you shouldn't ever need to check the logs.

#/DEBUGGING/#
--------------------------------------
