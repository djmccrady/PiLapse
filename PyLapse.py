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
        self.fRatio = fRatio
        self.shutterSeconds = shutterSeconds
        self.iso = iso

    def __str__(self):
        return "ISO %s, shutter %s, f/ratio %s" % (self.iso, self.shutterSeconds, self.fRatio)

    def GetExposureValue(self):
        return math.log(math.pow(self.fRatio, 2) / self.shutterSeconds / (self.iso / 100), 2)



class Camera:
    def __init__(self, name, baseISO, maxISO):
        self.name = name
        self.baseISO = baseISO
        self.maxISO = maxISO




def StartExposure(exposureSeconds):
    print("Taking exposure: ", exposureSeconds)
    time.sleep(exposureSeconds)

startTime = time.time()
endTime = startTime + 120  # 2 minutes in the future

exposureSeconds = 15
intervalSeconds = 20

camera = Camera("EOS R5", 100, 6400)
exposure = Exposure(2.8, 20, 4000)

print("EV for ", exposure, " is ", exposure.GetExposureValue())


print('Start time = ', time.ctime(startTime))
print('End time   = ', time.ctime(endTime))

while time.time() < endTime:
    extraWaitAfter = intervalSeconds - exposureSeconds
    StartExposure(exposureSeconds)
    print("Waiting after exposure for ", extraWaitAfter)
    time.sleep(extraWaitAfter)