# Pi radio

This script is intended to turn a radio into a transmitter for a fox hunts or similar activities.


## Setup

```
pip3 install pygame numpy scipy
```

Audio setup:
```
sudo raspi-config
```
Navigate to: System Options -> Audio, and select your preferred device.

Note: If unable to hear output from the pi, may need to force system volume to max via the following command line:
```
amixer set PCM unmute && amixer set PCM 100%
```

```
crontab crontab_settings.txt
```
