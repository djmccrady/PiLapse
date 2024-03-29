"""   
   Copyright 2021 Don J. McCrady

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import time
import math

class Exposure:
    # Standard ISO, fstop, and shutter values in 1/3 increments, in order of increasing exposure value
    __ISO_values = [ 100, 125, 160, 200, 250, 320, 400, 500, 640, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6400, 8000, 10000, 12800, 16000, 20000, 25600 ]
    __fstop_values = [ 22.0, 20.0, 18.0, 16.0, 14.0, 13.0, 11.0, 10.0, 9.0, 8.0, 7.1, 6.3, 5.6, 5.0, 4.5, 4.0, 3.5, 3.2, 2.8, 2.5, 2.0, 1.8, 1.4, 1.2 ]
    __shutter_values = [ 1.0/8000.0, 1.0/6400.0, 1.0/5000.0, 1.0/4000.0, 1.0/3200.0, 1.0/2500.0, 1.0/2000.0, 1.0/1600.0, 1.0/1250.0, 1.0/1000.0, 1.0/800.0, 1.0/640.0, 1.0/500.0, 1.0/400.0, 1.0/320.0, 1.0/250.0, 1.0/200.0, 1.0/160.0, 1.0/125.0, 1.0/100.0, 1.0/80.0, 1.0/60.0, 1.0/50.0, 1.0/40.0, 1.0/30.0, 1.0/25.0, 1.0/20.0, 1.0/15.0, 1.0/13.0, 1.0/10.0, 1.0/8.0, 1.0/6.0, 1.0/5.0, 1.0/4.0, 1.0/3.0, 1.0/2.5, 1.0/2.0, 1.0/1.6, 1.0/1.3, 1.0, 1.3, 1.6, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 13.0, 15.0, 20.0, 25.0, 30.0 ]

    def __init__(self, fRatio, shutterSeconds, iso):
        self._ix_fRatio = Exposure._closest_index(Exposure.__fstop_values, fRatio)
        self._ix_shutter = Exposure._closest_index(Exposure.__shutter_values, shutterSeconds)
        self._ix_iso = Exposure._closest_index(Exposure.__ISO_values, iso)

    def _closest_index(lst, K):
        return min(range(len(lst)), key = lambda i: abs(lst[i]-K))

    @property
    def ISO(self):
        return self.__ISO_values[self._ix_iso]

    @property
    def shutter(self):
        return self.__shutter_values[self._ix_shutter]

    @property
    def fRatio(self):
        return self.__fstop_values[self._ix_fRatio]

    def __str__(self):
        return "ISO %s, %ss, f/%s" % (self.ISO, self.shutter, self.fRatio)

    def GetExposureValue(self):
        return math.log(math.pow(self.fRatio, 2) / self.shutter / (self.ISO / 100), 2)

    def _adjust(ix, list, direction):
        new_ix = ix + direction
        if new_ix >= 0 and new_ix < len(list):
            return new_ix
        return None

    def AdjustISO(self, direction):
        ix = Exposure._adjust(self._ix_iso, Exposure.__ISO_values, direction)
        if ix != None:
            self._ix_iso = ix
            return self.ISO
        return None

    def AdjustShutter(self, direction):
        ix = Exposure._adjust(self._ix_shutter, Exposure.__shutter_values, direction)
        if ix != None:
            self._ix_shutter = ix
            return self.shutter
        return None

    def AdjustFRatio(self, direction):
        ix = Exposure._adjust(self._ix_fRatio, Exposure.__fstop_values, direction)
        if ix != None:
            self._ix_fRatio = ix
            return self.fRatio
        return None

class Timelapse:
    __INTERVAL_EXTRA = 2  # 2 seconds extra to allow the camera buffer read

    """
    The twilight times chosen for beginTwilight and endTwilight should be as follows:
       - For sunsets, beginning of civil twilight and end of astro twilight
       - For sunrises, beginning of astro twilight, and end of civil twilight
    """
    def __init__(self, startTime, endTime, startExposure, endExposure, beginTwilight, endTwilight, direction):
        self.startTime = startTime
        self.endTime = endTime
        self.startExposure = startExposure
        self.endExposure = endExposure
        self.beginTwilight = beginTwilight
        self.endTwilight = endTwilight
        self.direction = direction

        if startTime > beginTwilight:
            print("Start time begins after twilight start... adjusting twilight start.")
            self.beginTwilight = startTime

        # interval between shots is the longest exposure time + __INTERVAL_EXTRA to allow camera buffer read
        self.shootingInterval = round(max(startExposure.shutter, endExposure.shutter)) + Timelapse.__INTERVAL_EXTRA
        self._computeAdjustmentInterval()

    def _computeAdjustmentInterval(self):
        twilightDuration = self.endTwilight - self.beginTwilight

        exposureDiff = abs(self.startExposure.GetExposureValue() - self.endExposure.GetExposureValue())
        twilightDuration = abs(twilightDuration)

        self.adjustmentInterval = (twilightDuration * 24) / (math.ceil(exposureDiff * 3 * 3) / 3) / 1440
        self.adjustmentInterval *= 60  # convert to seconds

    def __str__(self):
        return "Shooting interval %s, adjustment interval %s, direction %s, startExposure %s, endExposure %s" % (self.shootingInterval, self.adjustmentInterval, self.direction, self.startExposure, self.endExposure)

    """
    Start the timelapse.
        - If the start time is in the future, wait until it's time to start.
        - Set the next adjustment time to be the first twilight begin plus the adjustment interval
        - Start shooting at the starting exposure
            - Wait the extra interval after each shot.
        - If the current time is greater-or-equal-to the next adjustment time, adjust the exposure in the appropriate direction
            - Set the next adjustment time to be the previous adjustment time plust the adjustment interval
    """
    def Start(self):
        currentTime = time.time()
        if currentTime < startTime:
            duration = startTime - currentTime
            print("Waiting to start at ", time.strftime("%H:%M:%S", time.localtime(startTime)), " (waiting ", round(duration, 1), "s)")
            time.sleep(duration)

        nextAdjustmentTime = self.beginTwilight + self.adjustmentInterval
        print("Starting timelapse... first adjustment at ", time.strftime("%H:%M:%S", time.localtime(nextAdjustmentTime)))

        currentExposure = startExposure

    """
    Adjust the exposure in the designated direction.

    If direction is positive (a sunset, so we are increasing our exposure value):
        - If the shutter speed is less than the max shutter speed, increase that.  Otherwise,
        - If the ISO is less than the max ISO, increase that.  Otherwise,
        - Keep the previous exposure.

    If direction is negative (a sunrise, so we are decreasing our exposure value):
        - If the ISO is greater than the min ISO, decrease that.  Otherwise,
        - If the shutter speed is greater than the min shutter speed, decrease that.  Otherwise,
        - Keep the previous exposure.
    """
    def _AdjustExposure(self, exposure):
        if self.direction > 0:   # sunset, exposures increase
            if exposure.shutter < max(self.startExposure.shutter, self.endExposure.shutter):
                exposure.AdjustShutter(self.direction)
            elif exposure.ISO < max(self.startExposure.ISO, self.endExposure.ISO):
                exposure.AdjustISO(self.direction)
        else:                    # sunrise, exposures decrease 
            if exposure.ISO > min(self.startExposure.ISO, self.endExposure.ISO):
                exposure.AdjustISO(self.direction)
            elif exposure.shutter > min(self.startExposure.shutter, self.endExposure.shutter):
                exposure.AdjustShutter(self.direction)
            


# TODO: not sure we need this
class Camera:
    def __init__(self, name, baseISO, maxISO):
        self.name = name
        self.baseISO = baseISO
        self.maxISO = maxISO



# TODO: Get rid of this
def StartExposure(exposureSeconds):
    print("Taking exposure: ", exposureSeconds)
    time.sleep(exposureSeconds)


def TestExposureAdjustments():
    camera = Camera("EOS R5", 100, 6400)
    exposure = Exposure(2.8, 20, 4000)

    print("EV for ", exposure, " is ", exposure.GetExposureValue())

    exposure.AdjustISO(-3)
    print("EV(ISO-3) for ", exposure, " is ", exposure.GetExposureValue())

    exposure.AdjustShutter(-3)
    print("EV(shutter-3) for ", exposure, " is ", exposure.GetExposureValue())

    exposure.AdjustFRatio(-3)
    print("EV(fRatio-3) for ", exposure, " is ", exposure.GetExposureValue())


def TestSunsetTimelapseComputations():
    ts = (2021, 3, 26, 19, 30, 0, 4, 85, -1)
    startTime = time.mktime(ts)

    ts = (2021, 3, 26, 23, 30, 0, 4, 85, -1)
    endTime = time.mktime(ts)

    ts = (2021, 3, 26, 19, 31, 0, 4, 85, -1)
    civilStart = time.mktime(ts)

    ts = (2021, 3, 26, 21, 17, 0, 4, 85, -1)
    astroEnd = time.mktime(ts)


    startExposure = Exposure(2.4, 1/1000, 100)
    endExposure = Exposure(2.4, 20, 4000)

    timelapse = Timelapse(startTime, endTime, startExposure, endExposure, civilStart, astroEnd, 1)
    print("Timelapse: ", timelapse)

    for i in range(70):
        timelapse._AdjustExposure(startExposure)
        print("Adjusted exposure: ", startExposure, "step", i)
    #timelapse.Start()

def TestSunriseTimelapseComputations():
    ts = (2021, 3, 26, 19, 30, 0, 4, 85, -1)
    startTime = time.mktime(ts)

    ts = (2021, 3, 26, 23, 30, 0, 4, 85, -1)
    endTime = time.mktime(ts)

    ts = (2021, 3, 26, 5, 13, 0, 4, 85, -1)
    astroStart = time.mktime(ts)

    ts = (2021, 3, 26, 6, 59, 0, 4, 85, -1)
    civilEnd = time.mktime(ts)


    startExposure = Exposure(2.4, 20, 4000)
    endExposure = Exposure(2.4, 1/1000, 100)

    timelapse = Timelapse(startTime, endTime, startExposure, endExposure, astroStart, civilEnd, -1)
    print("Timelapse: ", timelapse)

    for i in range(70):
        timelapse._AdjustExposure(startExposure)
        print("Adjusted exposure: ", startExposure, "step", i)
    #timelapse.Start()

TestSunriseTimelapseComputations()