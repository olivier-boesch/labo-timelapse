#!/usr/bin/env python3
"""
PyLapse : A python/kivy application to create Timelapses
Olivier Boesch (c) 2020
"""

# version -------
__version__ = '0.9'

# imports -------

# kivy stuff
from kivy.app import App
from kivy.logger import Logger
from kivy.clock import Clock, mainthread
from kivy.factory import Factory

# system related
from os import system, listdir
from os.path import isfile, join
import pyudev
import shutil

# video related
import ffmpeg

# time related
from datetime import timedelta
from time import sleep

# rpi camera
import picamera


# main app ------
class PylapseApp(App):
    """PylapseApp : Kivy Application to create Timelapse videos on the Raspberry pi"""
    cam = picamera.PiCamera()  # camera object
    preview_on = False  # is preview running
    rotation_angle = 0  # rotation angle for the camera (0, 90 180 270°)
    h_flip = False  # horizontal mirroring (boolean)
    v_flip = False  # vertical mirroring (boolean)
    resolution = '1080p'  # default resolution for timelapse and preview
    timelapse_event = None  # Timelapse event to take picture
    interval_time = 10  # s - interval between two pictures
    total_time = 60  # s - total time of timelapse
    frame_counter = 0  # frame counter for filenames
    timelapse_started = False  # flag set to True when timelapse is started
    confirm_popup = None  # popup to confirm timelapse stop
    progress_popup = None
    device_observer = None
    pyudev_context = None
    usb_drive_device = None
    usb_drive_path = '/media/pi/usb'
    transfer_popup = None

    def on_start(self):
        """when app starts"""
        # pyudev context
        self.pyudev_context = pyudev.Context()
        # start preview
        self.toggle_preview(on=True)
        # listening for usb drive plugged
        self.start_listening_usb()

    def start_listening_usb(self):
        monitor = pyudev.Monitor.from_netlink(self.pyudev_context)
        monitor.filter_by('block')
        self.device_observer = pyudev.MonitorObserver(monitor, self.new_usb_drive)
        self.device_observer.start()

    def stop_listening_usb(self):
        if self.device_observer is not None:
            self.device_observer.stop()
            self.device_observer = None

    @mainthread
    def new_usb_drive(self, action, device):
        """triggered when a usb drive is plugged"""
        if action == 'add' and device.device_type == 'partition':
            self.usb_drive_device = device.device_node
            drive_label = device.get('ID_FS_LABEL')
            Logger.info('{0} usb key \"{1}\" ({2})'.format(action, drive_label, self.usb_drive_device))
            self.root.ids['usb'].opacity = 1.0
            self.root.ids['usb_drive'].text = drive_label
            system('sudo mount -o gid=1000,uid=1000 {0} {1}'.format(self.usb_drive_device, self.usb_drive_path))
            self.toggle_preview(on=False)
            Logger.info('{0} usb key \"{1}\" ({2} - > {3})'.format(action, drive_label,
                                                                   self.usb_drive_device, self.usb_drive_path))
            self.transfer_popup = Factory.DialogTransfer()
            self.transfer_popup.open()
        elif action == 'remove' and device.device_type == 'partition':
            self.usb_drive_device = None
            self.root.ids['usb'].opacity = 0.1
            self.root.ids['usb_drive'].text = ''
            Logger.info('{0} usb key \"{1}\" ({2})'.format(action, device.get('ID_FS_LABEL'), device.device_node))
            if self.transfer_popup is not None:
                self.transfer_popup.dismiss()
                self.transfer_popup = None

    def eject_usb_drive(self):
        if self.usb_drive_device is not None:
            system('sudo eject {0}'.format(self.usb_drive_device))
            Logger.info('eject usb key {0}'.format(self.usb_drive_device))

    def transfer_files(self, transfer_images=True, transfer_video=False):
        try:
            if transfer_images or transfer_video:
                system("rm -rvf {0}/timelapse && mkdir {0}/timelapse".format(self.usb_drive_path))
            if transfer_images:
                files = [f for f in listdir('../images') if isfile(join('../images', f))]
                for f in files:
                    shutil.copy2(join('../images', f), join(self.usb_drive_path, 'timelapse'))
            if transfer_video:
                shutil.copy2(join('../video', 'timelapse.mp4'), join(self.usb_drive_path, 'timelapse'))
            self.eject_usb_drive()
            self.show_message('Transfer Success', 'Files are copied on USB drive')
        except:
            self.show_message('Transfer Error', 'Can\'t copy files on USB drive')

    def show_message(self, title, message):
        p = Factory.DialogMessage()
        p.open()
        p.ids['message_lbl'].text = message
        p.title = title

    def close_message_soon(self, message_popup, when):
        Clock.schedule_once(lambda dt: message_popup.dismiss(), when)

    def set_preview_dims(self, pos, size):
        """set preview overlay coordinates : pos and size"""
        x, y = pos
        w, h = size
        x = int(x)
        # axle is reversed
        y = int(self.root_window.size[1] - h - y)
        w = int(w)
        h = int(h)
        self.cam.preview_window = (x, y, w, h)

    def on_stop(self):
        """when app stops"""
        self.toggle_preview(on=False)
        self.stop_listening_usb()

    def toggle_preview(self, on):
        """preview : Toggle display of the preview"""
        # show preview if the button is down
        if on:
            self.preview_on = True
            # display preview
            self.cam.start_preview(fullscreen=False,
                                   rotation=self.rotation_angle,
                                   hflip=self.h_flip,
                                   vflip=self.v_flip)
            self.set_preview_dims(self.root.ids['preview'].pos, self.root.ids['preview'].size)
            self.cam.resolution = self.resolution
            # a bit of log
            Logger.info("Camera: preview enabled")
        else:
            # stop preview
            self.preview_on = False
            self.cam.stop_preview()
            # bit of log
            Logger.info("Camera: preview disabled")

    def camera_angle_change(self, text):
        """camera_angle_change : change rotation angle"""
        # 0°
        if text == 'No rotation':
            self.rotation_angle = 0
        # 90°
        elif text == 'rotate 90°':
            self.rotation_angle = 90
        # 180°
        elif text == 'rotate 180°':
            self.rotation_angle = 180
        # 270°
        elif text == 'rotate 270°':
            self.rotation_angle = 270
        # in case of wrong value : set to 0°
        else:
            self.rotation_angle = 0
        self.cam.rotation = self.rotation_angle

    def add_time_toggle(self, state_active):
        if state_active:
            self.cam.annotate_background = picamera.Color('black')
            self.cam.annotate_foreground = picamera.Color('white')
            self.cam.annotate_text = 'Elapsed Time'
        else:
            self.cam.annotate_background = None
            self.cam.annotate_foreground = picamera.Color('white')
            self.cam.annotate_text = ''

    def consistent_image_toggle(self, state_active):
        """consistent_image_toggle : set or unset 50Hz flickering filter and consistent image settings across time"""
        if state_active:
            # Set ISO to the desired value
            # self.cam.iso = 10
            self.cam.exposure_mode = 'off'
            sleep(0.5)
            # Now fix the values
            # adjust speed as a multiple of 10ms to prevent 50Hz flickering (multiple of 100Hz -> 10000µs)
            # with a min of 10ms
            Logger.info("Camera: Shutter speed is {:3.0f}µts".format(self.cam.exposure_speed))
            speed = max(int(round(self.cam.exposure_speed / 10000)) * 10000, 10000)
            self.cam.shutter_speed = speed
            Logger.info("Camera: Shutter speed set to {:3.0f}µs".format(speed))
            g = self.cam.awb_gains
            self.cam.awb_mode = 'off'
            self.cam.awb_gains = g
        else:
            self.cam.shutter_speed = 0
            self.cam.exposure_mode = 'auto'
            self.cam.awb_mode = 'auto'

    def resolution_change(self, text):
        """resolution_change : change resolution of the timelapse"""
        if text == '640x480':
            self.resolution = text
        elif text == '800x600':
            self.resolution = text
        elif text == 'HD 1280x720p':
            self.resolution = '720p'
        elif text == 'FHD 1920x1080p':
            self.resolution = '1080p'
        elif text == 'Max 2592x1944':
            self.resolution = '2592x1944'  # max value for 2.0 pi camera
        # in case of wrong value: set to FHD
        else:
            self.resolution = '1080p'
        self.update_ui_time_info()
        self.cam.resolution = self.resolution

    def hflip_change(self, active):
        """hflip_change: set or unset horizontal flip"""
        self.h_flip = active
        self.cam.hflip = self.h_flip

    def vflip_change(self, active):
        """vflip_change: set or unset vertical flip"""
        self.v_flip = active
        self.cam.vflip = self.v_flip

    def interval_time_change(self):
        """"interval_time_change: change interval time and reflect on ui"""
        val = int(self.root.ids['interval_value'].text)
        unit = self.root.ids['interval_unit'].text
        self.interval_time = self.compute_time(val, unit)
        self.adapt_ui_to_interval_time()
        self.update_ui_time_info()

    def adapt_ui_to_interval_time(self):
        """adapt_ui: change ui widgets availability with interval_time"""
        # frame period < 2s : disable image display
        if self.interval_time <= 2:
            self.root.ids['show_images'].active = False
            self.root.ids['show_images'].disabled = True
        else:
            self.root.ids['show_images'].disabled = False

    def total_time_change(self):
        """"total_time_change: change total time and reflect on ui"""
        val = int(self.root.ids['total_value'].text)
        unit = self.root.ids['total_unit'].text
        self.total_time = self.compute_time(val, unit)
        self.update_ui_time_info()

    def update_ui_time_info(self):
        """update_ui_time_info: update time and size info according to settings"""
        every = self.interval_time
        total = self.total_time
        # compute number of frames
        number_of_frames = int(total / every)
        # update infos label
        s = "Ready to take {:d} frames : 1 frame every {:d}s; total time {:d}s"
        self.root.ids['infos'].text = s.format(number_of_frames, every, total)

    @staticmethod
    def compute_time(value, unit):
        """compute_time : compute internal times in seconds according to units"""
        if unit == 's':
            return value
        if unit == 'min':
            return value * 60
        if unit == 'h':
            return value * 3600
        if unit == 'd':
            return value * 3600 * 24

    def timelapse_toggle(self):
        """timelapse_toggle : start or stop timelapse"""
        # start timelapse if not started
        if not self.timelapse_started:
            self.confirm_popup = Factory.DialogConfirmDelete()
            self.confirm_popup.open()
        # or stop if it was running
        else:
            # check first if the user really wants to stop...
            self.confirm_popup = Factory.DialogConfirmStop()
            self.confirm_popup.open()

    def start_timelapse(self):
        """start_timelapse: starts the timelapse"""
        self.change_ui_for_timelapse(start_timelapse=True)
        if self.confirm_popup is not None:
            self.confirm_popup.dismiss()
            self.confirm_popup = None
        self.delete_images()
        self.timelapse_event = Clock.schedule_interval(lambda dt: self.perform_capture(), self.interval_time)
        self.frame_counter = 0
        self.perform_capture()
        self.timelapse_started = True
        Logger.info("Timelapse: Started every: {:d} s / total: {:d} s".format(self.interval_time, self.total_time))

    def stop_timelapse(self):
        """stop_timelapse: stops the timelapse"""
        if self.confirm_popup is not None:
            self.confirm_popup.dismiss()
            self.confirm_popup = None
        self.cam.annotate_text = "Elapsed time"
        self.timelapse_event.cancel()
        self.timelapse_event = None
        Logger.info("Timelapse: Stopped ({:d} frames captured)".format(self.frame_counter))
        self.frame_counter = 0
        self.timelapse_started = False
        self.change_ui_for_timelapse(start_timelapse=False)

    def change_ui_for_timelapse(self, start_timelapse=True):
        """change_ui_for_timelapse: disable/enable everything possible for/after timelapse"""
        if start_timelapse:
            self.stop_listening_usb()
            self.toggle_preview(on=False)
            self.root.ids['timelapse_toggle'].text = 'Stop Timelapse'
            self.root.ids['resolution_timelapse'].disabled = True
            self.root.ids['rotation'].disabled = True
            self.root.ids['hflip'].disabled = True
            self.root.ids['vflip'].disabled = True
            self.root.ids['interval_value'].disabled = True
            self.root.ids['interval_unit'].disabled = True
            self.root.ids['total_value'].disabled = True
            self.root.ids['total_unit'].disabled = True
            self.root.ids['show_images'].disabled = True
            self.root.ids['add_time'].disabled = True
            self.root.ids['consistent_images'].disabled = True
            # self.root.ids['create_video'].disabled = True
            self.root.ids['quit'].disabled = True
        else:  # False -> stop timelapse
            self.start_listening_usb()
            self.toggle_preview(on=True)
            self.root.ids['timelapse_toggle'].text = 'Start Timelapse'
            self.root.ids['preview'].source = "1blackpixel.png"
            self.update_ui_time_info()
            self.root.ids['resolution_timelapse'].disabled = False
            self.root.ids['rotation'].disabled = False
            self.root.ids['hflip'].disabled = False
            self.root.ids['vflip'].disabled = False
            self.root.ids['interval_value'].disabled = False
            self.root.ids['interval_unit'].disabled = False
            self.root.ids['total_value'].disabled = False
            self.root.ids['total_unit'].disabled = False
            self.root.ids['show_images'].disabled = False
            self.root.ids['add_time'].disabled = False
            self.root.ids['consistent_images'].disabled = False
            # self.root.ids['create_video'].disabled = False
            self.root.ids['quit'].disabled = False

    def perform_capture(self):
        """perform_capture : get one frame and record it as jpg"""
        filename = "../images/img_{:05d}.jpg".format(self.frame_counter)
        if self.root.ids['add_time'].active:
            elapsed_time = timedelta(seconds=self.interval_time * self.frame_counter)
            self.cam.annotate_text = str(elapsed_time).replace("day", "jour")
        self.cam.capture(filename)
        if self.root.ids['show_images'].active:
            self.root.ids['preview'].source = filename
        self.frame_counter += 1
        if self.interval_time * self.frame_counter > self.total_time:
            self.stop_timelapse()
        Logger.info("Timelapse: captured frame num {:d} : {:s}".format(self.frame_counter, filename))
        self.root.ids['infos'].text = "Timelapse Running (Captured frame n°{:d}.)".format(self.frame_counter)

    def create_video(self):
        """create_video: create a video by calling ffmpeg"""
        # TODO: find a way to get ffmpeg stats and run asynchronously
        self.toggle_preview(on=False)
        self.progress_popup = Factory.VideoProgress()
        self.progress_popup.open()

    def launch_video_thread(self):
        pass

    def on_quit_button_released(self):
        self.toggle_preview(on=False)
        p = Factory.DialogConfirmQuit()
        p.open()

    @staticmethod
    def poweroff():
        """poweroff the pi"""
        Logger.info("App: Stopping the pi")
        system("sudo poweroff")
        self.stop()

    @staticmethod
    def delete_images():
        """delete_images : empty the images dir"""
        Logger.info("Timelapse: deleting images in the \"images\" dir")
        # delete the directory and recreate it
        system("rm -rvf ../images && mkdir ../images")


# Run the app -------
app = PylapseApp()
app.run()
