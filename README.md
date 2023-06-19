# AstroPICode
This is the main file that goes on the Astro-PI for the Astro-PI experiment.
It was made by me following a bit of docs from the Astro-PI website to capture images from the camera.
# How does the Astro-PI work?
It is basically a rasberry-pi with addons, things like a camera, inbuilt libraries to get images from the camera, and capture sensor data like: yaw, pitch, infra-red images, normal images, acceleration, etc...
You can use what you capture from the data in different ways, there are 2 experiments you can do,
Life in Space, or Life on Earth, if you are doing Life in Space, you have to come up with and do an experiment related to on-board the ISS.
If you choose Life on Earth, then you design and execute an experiment related to Earth.
This experiment is Life on Earth.
# What does this file do?
This file will periodically capture images from the Astro-PI, and check if they are night time (by averaging the color of the pixels), if the brightness level is higher than a threshhold (indicating it is probably day-time), it will check if it has enough space to save the image, and if it does, it will save the image.
then it sleeps for a period of time determined beforehand, the time it sleeps for does take into account how long it takes to save the image from the camera. (if it has to)
Feel free to look at the files code and comments to understand it further, and to see how it accomplishes this.
# What will the experiment do?
The goal of this experiment is to use the captured images from the ISS to create a Minecraft world that, based on height maps and the color of each pixel from our image,
will look like the Earth. (atleast in the parts of the world we captured from the ISS)
# Will this be maintained?
No
