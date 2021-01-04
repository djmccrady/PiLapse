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