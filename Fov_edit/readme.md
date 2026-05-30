I took a swing through the exe and and got my python minion to write something that seems to change the drivers fov/pov using the field of view slider in game and it works (sorta) as you have to have the game resolution at 640x480 800x600 1024x768 or 1280x1024. I have tried messing with the rend dlls as well as a aspect ratio in the exe and not really getting anywhere.

The other reason is that it looks more like you are moving the driver position back and forth. At 97 back you can see three quarters of the steering wheel and the a pillar in the passenger side at 30 you just see the top of the curve on the steering wheel (but then the tach reads 0 at idle) but everything still works and drives

I would like someone who knows more then I do on the car files and how the driver is positioned(I'm still breaking models).

But I have discovered some things. The minimum of 65 is linked to the rpm on the tach and when you go over about 97.10 the mirror turns black.

Run patch_nr2003_fov.py --help for options

TL:DR
Copy nr2003.exe to the folder and run

python3 patch_nr2003_fov.py --output nr2003p.exe --fov-min 50 --fov-max 100 --no-dll

copy exe to your game folder and go.

This is very much a use at own risk. I know that the game starts/runs at the track for me. I have not did much testing. This is a proof of concept. You have the script so change it and make it better.

Then you can tell me what a awesome change you made. :)
