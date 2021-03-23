# PyLapse

PyLapse is a gphoto2-based DLSR camera contoller that automatically takes timelapse
images for a given interval.  It also supports automatic ramping of exposure settings
to adjust for changing light conditions during a sunset or sunrise.

At its most basic level, PyLapse will behave like a smart remote (e.g. Canon TCN-80),
taking an image at preset fixed intervals.

Adding automatic exposure adjustments, PyLapse can be used to automatically control
a Holy Grail timelapse starting with a fast, low-ISO daylight exposure, gradually ramping
down to a slow, high-ISO nighttime exposure.

TIMELAPSE

A timelapse requires the following inputs:

    - Interval (time between each exposure)
        - Note: longest exposure time should be one or two seconds shorter than the interval
    - Start time
    - End time

RAMPING

Ramping requires the following inputs:

    - Initial exposure settings (f-stop, shutter speed, ISO) for the **end** of civil twilight
    - Final exposure values (f-stop, shutter speed, ISO) for **end** of astronomical twilight.
    - Times for **end** of civil and astronomical twilights (TODO: compute)
    - Maximum ISO and maximum exposure time

At the start of the sequence, the initial exposure values are used to take the first
picture.  At intervals computed by PyLapse, the exposure values are changed in 1/3-stop
increments.  For sunsets, first the shutter speed will be gradually lengthened until
we reach the shutter speed limit for sharp stars.  After that, the ISO will be gradually
increased until we reach our target night-time exposure value.  Note that the f-stop is
never adjusted; it remains constant throughout the exposure.

EXAMPLE

On Dec 21, 2020, civil twilight ends at 4:56pm, astronomical twilight ends at 5:35.  Let's
say we want our timelapse to start at 4:30pm, and end at 7:00pm.  For the Canon R5, the
maximum exposure time for spot stars is about 15 seconds (with a 14mm lens), and the maximum
ISO is 6400.

Here are our variables:

    - Interval chosen:  20s
    - Start time:  4:30pm
    - End time:  7:00pm
    - Initial exposure (for civil twilight about EV+10, i.e ISO 100, f/2.4, 1/160s)
    - Final exposure (after astro twilight about EV-7, i.e. ISO 6400, f/2.4, 15s)
    - Max ISO: 6400 (get this from the final exposure above)
    - Max exposure time: 15s (get this from the final exposure above)

The duration of the timelapse is 2h30m, and with an exposure every 20s that's 450 exposures.

At 4:30pm the timelapse begins with the initial exposure settings of ISO 100, f/2.4, 1/160s).
At 4:56pm after 78 exposures have been taken, the exposure ramping begins with computed changes
happening every 45s (computed by PyLapse), and the next exposure will be 1/125s.  Approximately
45s after that the shutter speed will increase to 1/100s. After 32 more exposures, the shutter 
speed will have reached 15s, the maximum we've specified to keep the stars sharp.  PiLapse will
then start ramping up the ISO from 100, until at 5:35pm (astronomical twilight) we will have
fully ramped up to ISO 6400.  The remaining exposures will use the final exposure values (ISO 6400,
f/2.4, 15s).

TEST
