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
    The twilight times chosen for civil and astro should be chosen as follows:
       - For sunsets, beginning of civil twilight and end of astro twilight
       - For sunrises, end of astro twilight, and end of civil twilight ends
    From these times, the direction (whether exposure increases [sunset] or decreases [sunrise]) is
    automatically chosen.
    """
    def __init__(self, startTime, endTime, startExposure, endExposure, civilTwilight, astroTwilight):
        self.startTime = startTime
        self.endTime = endTime
        self.startExposure = startExposure
        self.endExposure = endExposure
        self.civilTwilight = civilTwilight
        self.astroTwilight = astroTwilight

        # interval between shots is the longest exposure time + __INTERVAL_EXTRA to allow camera buffer read
        self.shootingInterval = round(max(startExposure.shutter, endExposure.shutter)) + Timelapse.__INTERVAL_EXTRA
        self._computeAdjustmentInterval()

    def _computeAdjustmentInterval(self):
        twilightDuration = self.astroTwilight - self.civilTwilight

        # If astro twilight comes after civil twilight, then it's a sunset (direction = 1), otherwise
        # it's a sunrise (direction = -1)
        if twilightDuration > 0:
            self.direction = 1
        else:
            self.direction = -1

        exposureDiff = abs(startExposure.GetExposureValue() - endExposure.GetExposureValue())
        twilightDuration = abs(twilightDuration)

        self.adjustmentInterval = (twilightDuration * 24) / (math.ceil(exposureDiff * 3 * 3) / 3) / 1440
        self.adjustmentInterval *= 60  # convert to seconds

    def __str__(self):
        return "Shooting interval %s, adjustment interval %s, direction %s, startExposure %s, endExposure %s" % (self.shootingInterval, self.adjustmentInterval, self.direction, self.startExposure, self.endExposure)

    def Start(self):
        currentTime = time.time()
        if currentTime < startTime:
            duration = startTime - currentTime
            print("Waiting to start at ", time.strftime("%H:%M:%S", time.localtime(startTime)), " (waiting ", round(duration, 1), "s)")
            time.sleep(duration)

        print("Starting timelapse")



class Camera:
    def __init__(self, name, baseISO, maxISO):
        self.name = name
        self.baseISO = baseISO
        self.maxISO = maxISO




def StartExposure(exposureSeconds):
    print("Taking exposure: ", exposureSeconds)
    time.sleep(exposureSeconds)


camera = Camera("EOS R5", 100, 6400)
exposure = Exposure(2.8, 20, 4000)

print("EV for ", exposure, " is ", exposure.GetExposureValue())

exposure.AdjustISO(-3)
print("EV(ISO-3) for ", exposure, " is ", exposure.GetExposureValue())

exposure.AdjustShutter(-3)
print("EV(shutter-3) for ", exposure, " is ", exposure.GetExposureValue())

exposure.AdjustFRatio(-3)
print("EV(fRatio-3) for ", exposure, " is ", exposure.GetExposureValue())

ts = (2021, 3, 24, 20, 0, 0, 2, 83, -1)
startTime = time.mktime(ts)

ts = (2021, 3, 24, 23, 0, 0, 2, 83, -1)
endTime = time.mktime(ts)

ts = (2021, 3, 24, 20, 42, 0, 2, 83, -1)
civilStart = time.mktime(ts)

ts = (2021, 3, 24, 22, 4, 0, 2, 83, -1)
astroEnd = time.mktime(ts)



startExposure = Exposure(2.8, 1.6, 100)
endExposure = Exposure(2.8, 18, 4000)

timelapse = Timelapse(startTime, endTime, startExposure, endExposure, civilStart, astroEnd)
print("Timelapse: ", timelapse)
#timelapse.Start()