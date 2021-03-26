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

    - Initial exposure settings (f-stop, shutter speed, ISO) for the **start** of civil twilight
    - Final exposure values (f-stop, shutter speed, ISO) for **end** of astronomical twilight.
    - Times for **start** of civil and **end** of astronomical twilights (TODO: compute)
        - For sunrise, use the **start** of astronomical twilight and the **end** of civil twilight

At the start of the sequence, the initial exposure values are used to take the first
picture.  At intervals computed by PyLapse, the exposure values are changed in 1/3-stop
increments.  For sunsets, first the shutter speed will be gradually lengthened until
we reach the shutter speed limit for sharp stars.  After that, the ISO will be gradually
increased until we reach our target night-time exposure value.  Note that the f-stop is
never adjusted; it remains constant throughout the exposure.

EXAMPLE

On March 26, 2021, civil twilight starts at 7:31pm, astronomical twilight ends at 9:17pm.  Let's
say we want our timelapse to start at 7:00pm, and end at 11:30pm.  For the Canon 6D, the
maximum exposure time for spot stars is about 20 seconds (with a 16mm lens), and the maximum
ISO is 6400.

Here are our variables:

    - Start time:  7:00pm
    - End time:  11:30pm
    - Initial exposure (for civil twilight about EV+13, i.e ISO 100, f/2.4, 1/1000s)
    - Final exposure (after astro twilight about EV-6.67, i.e. ISO 4000, f/2.4, 20s)
    - Twilight start/end times
    - Extra 2 seconds between shots (one shot every 22 seconds)

The duration of the timelapse is 4h30m, and with an exposure every 20s that's 736 exposures.
The duration between the start of civil twilight and the end of astro twilight is 1h46m, so
we compute that we'll need to adjust the exposure by 1/3 stop every 1m48s.

At 7:00pm we start the timelapse with our initial exposure settings of ISO 100, f/2.4, 1/1000s.
We keep shooting at this exposure until civil twilight begins, about 84 shots.  At 1m48s past
the start of civil twilight, the exposure will be adjusted down by 1/3 stop, to ISO 100, f/2.4, 
1/800s.  After another 1m48s, the exposure will be adjusted to ISO 100, f/2.4, 1/640s.  After
42 adjustments have been made to the shutter speed, we will have reached our maximum shuttter
speed of 20s (ISO 100, f/2.4, 20s).  Since we still haven't reached the end of astro twilight,
we therefore start adjusting the ISO instead.  After the next 1m48s interval, we'll adjust the
exposure to ISO 125, f/2.4, 20s.  Then ISO 160, f/2.4, 20s, etc.  By the time astro twilight
ends we will have done a total of 58 exposure adjustments and will have reached our final
exposure of ISO 4000, f/2.4, 20s.  We will keep using this exposure until 11:30pm when the
timelapse ends.
