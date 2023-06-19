from datetime import datetime, timedelta, timezone
from time import sleep
from orbit import ISS
from picamera import PiCamera
from pathlib import Path
from os import mkdir, remove, fsync
from os.path import exists, getsize
from PIL import Image
from numpy import ceil, abs
from logzero import logger, logfile

# max images it can store, how long it waits between images, how long the experiment will run for and camera resolution
CONST_MAX_SIZE_MB = 3000 - 6
CONST_MAX_IMAGES = 2298
CONST_SLEEP_TIME = 4.8
CONST_EXPERIMENT_TIME_MINUTES = 3 * 60 - 3
CONST_CAMERA_RESOLUTION = (2592, 1944)
CONST_IMAGE_SKIP = 6

def avg_brightness(pil_img):
    """Calculates the highest average pixel brightness of an image. (Note, this is not the perceived brightness, just the average of RGB values)
        Code adapted from https://stackoverflow.com/questions/6442118/python-measuring-pixel-brightness"""
    if not Image.isImageType(pil_img):
        raise TypeError("pil_img image must be a valid PIL.Image")
    avg_bright = 0.0
    for x in range(0, pil_img.width, CONST_IMAGE_SKIP):
        for y in range(0, pil_img.height, CONST_IMAGE_SKIP):
            (R, G, B) = pil_img.getpixel((x, y))
            avg_bright += (R + G + B) / 3.0
    return ceil(avg_bright / ((pil_img.width / CONST_IMAGE_SKIP) * (pil_img.height / CONST_IMAGE_SKIP)))


def is_nighttime(pil_img, thresh=50):
    """Gets the average brightness in an image, then returns true or false based on whether it is smaller than a
    user-given threshold, default threshold value is 128"""
    return avg_brightness(pil_img=pil_img) < thresh


if __name__ == '__main__':
    """Main method, this creates all the needed files, sets up the camera, and loops for 3 hours. Every 4.7 seconds 
    it captures an image from the camera, and checks if the average brightness in the image is less than a certain 
    amount, if so it assumes it is night time and does not save the image. If it saves the image it also saves the 
    coordinates of the ISS and current time, so we can identify where the image was taken. Once the 3 hours are over 
    it will close all the files and the camera, then shutdown. It will also shutdown if the amount of space the 
    images take is more than the maximum allowable space. It also logs what the program does for error handling. A 
    bit of code (taking an image, and stopping the experiment) was adapted from some of the Astro-PI projects, 
    https://projects.raspberrypi.org/en/pathways/life-on-earth"""
    end_time = datetime.now(timezone.utc) + timedelta(minutes=CONST_EXPERIMENT_TIME_MINUTES)
    base_folder = str(Path(__file__).parent.resolve())
    # Init logger
    logfile(filename=f"{base_folder}/logfile.txt")
    logger.info("New log")
    # Creating the file structure, default data folder is (base_folder)/data
    data_folder = f"{base_folder}/data"
    if not exists(path=data_folder):
        mkdir(path=data_folder)
        logger.info("Made data folder")
    # image folder (where saved images are stored) default is (base_folder)/data/images
    image_folder = f"{data_folder}/images"
    if not exists(path=image_folder):
        mkdir(path=image_folder)
        logger.info("Made image folder")
    # location data file where iss coords are stored, default path is (base_folder)/data/location_data.txt
    data_file = open(file=f"{data_folder}/location_data.txt", mode='a')
    logger.info("Opened data file")
    camera = PiCamera()
    camera.resolution = CONST_CAMERA_RESOLUTION
    camera.framerate = 15
    logger.info("Initialized camera")
    sleep(2)
    img_count = 0
    size_mb = 0.0
    data_file.write("Starting new experiment!\n")
    data_file.flush()
    logger.info("Starting experiment!")
    while datetime.now(timezone.utc) < end_time:
        begin = datetime.now(timezone.utc)
        try:
            img_path = f"{image_folder}/Image_{img_count}.jpg"
            camera.capture(img_path)
            logger.info("Took an image")
            if is_nighttime(pil_img=Image.open(img_path), thresh=67):
                remove(path=img_path)
                logger.info("Removed image because it was night time")
            else:
                size_mb += getsize(img_path) / 1000000.0
                if size_mb > CONST_MAX_SIZE_MB:
                    size_mb -= getsize(img_path) / 1000000.0
                    logger.warning("Max sized reached, removing image and exiting.")
                    remove(path=img_path)
                    break
                coords = ISS.coordinates()
                data_file.write(
                    f'Image_{img_count}.jpg,'
                    f'{coords.latitude},'
                    f'{coords.longitude},'
                    f'{datetime.now(timezone.utc).strftime("%m-%d-%H-%M-%S-%f")[:-3]}\n'
                )
                data_file.flush()
                fsync(data_file)
                img_count += 1
                logger.info("Saved image")
                if img_count == CONST_MAX_IMAGES:
                    logger.warning("Max images reached, exiting.")
                    break
        except Exception as e:
            logger.error(f"Error in {e.__class__.__name__}, {e}")
        seconds = (datetime.now(timezone.utc) - begin).total_seconds()
        sleep_time = CONST_SLEEP_TIME - seconds
        if sleep_time > 0:
            sleep(sleep_time)
        else:
            logger.warning(f"Experiment is taking too long! (+{abs(sleep_time)} seconds!)")
    data_file.write(f"Ended experiment ----- {ceil(size_mb)} MB\n")
    data_file.flush()
    fsync(data_file)
    data_file.close()
    camera.close()
    logger.info("Closed everything, End of log.")