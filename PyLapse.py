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
    def __init__(self, fRatio, shutterSeconds, iso):
        self.fRatio = fRatio
        self.shutterSeconds = shutterSeconds
        self.iso = iso

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

print("EV for f/2.8, 20s, ISO 4000 = ", exposure.GetExposureValue())


print('Start time = ', time.ctime(startTime))
print('End time   = ', time.ctime(endTime))

while time.time() < endTime:
    extraWaitAfter = intervalSeconds - exposureSeconds
    StartExposure(exposureSeconds)
    print("Waiting after exposure for ", extraWaitAfter)
    time.sleep(extraWaitAfter)