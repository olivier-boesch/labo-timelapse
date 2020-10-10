#!/usr/bin/env python3
"""
PyLapse : A python/kivy application to create Timelapses
Olivier Boesch (c) 2020
"""
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.factory import Factory
from datetime import timedelta
from time import sleep


class PylapseApp(App):
    """PylapseApp : Kivy Application to create Timelapse videos on the Raspberry pi"""
    cam = picamera.PiCamera()  # camera object
    rotation_angle = 0  # rotation angle for the camera (0, 90 180 270°)
    h_flip = False  # horizontal mirroring (boolean)
    v_flip = False  # vertical mirroring (boolean)
    resolution_preview = '720p'  # default resolution for preview
    resolution = '1080p'  # default resolution for timelapse (pictures)
    timelapse_event = None  # Timelapse event to take picture
    interval_time = 10  # s - interval between two pictures
    total_time = 60  # s - total time of timelapse
    frame_counter = 0  # frame counter for filenames
    timelapse_started = False  # flag set to True when timelapse is started
    confirm_popup = None  # popup to confirm timelapse stop

    def preview(self, state):
        """preview : Toggle display of the preview"""
        # show preview if the button is down
        if state == 'down':
            # make preview overlay fit the preview image widget (it's drawn on top of the app)
            x, y = self.root.ids['preview'].pos
            w, h = self.root.ids['preview'].size
            x = int(x)
            y = int(Window.size[1] - h - y)
            w = int(w)
            h = int(h)
            # set chosen resolution
            self.cam.resolution = self.resolution_preview
            # display preview
            self.cam.start_preview(fullscreen=False,
                                   window=(x, y, w, h),
                                   rotation=self.rotation_angle,
                                   hflip=self.h_flip,
                                   vflip=self.v_flip)
            # a bit of log
            Logger.info("Camera: preview enabled")
        # button is normal
        else:
            # stop preview
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
        # if the preview is on : update instantly
        if self.root.ids['toggle_preview'].state == 'down':
            self.cam.rotation = self.rotation_angle

    def preview_resolution_change(self, text):
        """preview_resolution_change: change resolution of preview only"""
        if text == '640x480':
            self.resolution_preview = text
        elif text == '800x600':
            self.resolution_preview = text
        elif text == 'HD 1280x720p':
            self.resolution_preview = '720p'
        elif text == 'FHD 1920x1080p':
            self.resolution_preview = '1080p'
        # in case of wrong value: set to HD
        else:
            self.resolution_preview = '720p'
        # if the preview is on : update instantly
        if self.root.ids['toggle_preview'].state == 'down':
            self.cam.resolution = self.resolution_preview

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

    def hflip_change(self, active):
        """hflip_change: set or unset horizontal flip"""
        self.h_flip = active
        if self.root.ids['toggle_preview'].state == 'down':
            self.cam.hflip = self.h_flip

    def vflip_change(self, active):
        """vflip_change: set or unset vertical flip"""
        self.v_flip = active
        if self.root.ids['toggle_preview'].state == 'down':
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
        # compute size of files (in kb or Mb)
        if self.resolution == '640x480':
            one_file_size = 10
        elif self.resolution == '800x600':
            one_file_size = 20
        elif self.resolution == '720p':
            one_file_size = 400
        elif self.resolution == '1080p':
            one_file_size = 1000
        elif self.resolution == '2592x1944':
            one_file_size = 2400
        total_size = int(one_file_size * number_of_frames / 1024)  # compute in Mb (approx)
        # update infos label
        s = "Ready to take {:d} frames : 1 frame every {:d}s; total time {:d}s; frame size {:d}ko; total size {:d}Mb"
        self.root.ids['infos'].text = s.format(number_of_frames, every, total, one_file_size, total_size)

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
            # stop preview to properly display the dialog
            if self.root.ids['toggle_preview'].state == 'down':
                self.cam.stop_preview()
                self.root.ids['toggle_preview'].state = 'normal'
            self.confirm_popup = Factory.DialogConfirmDelete()
            self.confirm_popup.open()
        # or stop if it was running
        else:
            # check first if the user really wants to stop...
            self.confirm_popup = Factory.DialogConfirmStop()
            self.confirm_popup.open()

    def start_timelapse(self):
        """start_timelapse: starts the timelapse"""
        if self.confirm_popup is not None:
            self.confirm_popup.dismiss()
            self.confirm_popup = None
        self.delete_images()
        self.timelapse_event = Clock.schedule_interval(lambda dt: self.perform_capture(), self.interval_time)
        self.frame_counter = 0
        self.cam.resolution = self.resolution
        self.cam.rotation = self.rotation_angle
        self.cam.hflip = self.h_flip
        self.cam.vflip = self.v_flip
        # enable annotations on images
        if self.root.ids['add_time'].active:
            self.cam.annotate_background = picamera.Color('black')
            self.cam.annotate_foreground = picamera.Color('white')
        # make image consistent across time and avoid 50Hz flickering
        if self.root.ids['consistent_images'].active:
            # Set ISO to the desired value
            camera.iso = 100
            # Wait for the automatic gain control to settle
            sleep(2)
            # Now fix the values
            # adjust speed as a multiple of 10ms to prevent 50Hz flickering
            # with a min of 10ms
            speed = min(camera.exposure_speed // 10000 * 10000, 10000)
            camera.shutter_speed = speed
            Logger.info("Camera: Shutter speed set to {:3.0f}ms".format(speed))
            camera.exposure_mode = 'off'
            g = camera.awb_gains
            camera.awb_mode = 'off'
            camera.awb_gains = g
        self.change_ui_for_timelapse(start_timelapse=True)
        self.perform_capture()
        self.timelapse_started = True
        Logger.info("Timelapse: Started every: {:d} s / total: {:d} s".format(self.interval_time, self.total_time))

    def stop_timelapse(self):
        """stop_timelapse: stops the timelapse"""
        if self.confirm_popup is not None:
            self.confirm_popup.dismiss()
            self.confirm_popup = None
        self.timelapse_event.cancel()
        self.timelapse_event = None
        Logger.info("Timelapse: Stopped ({:d} frames captured)\nReady".format(self.frame_counter))
        self.frame_counter = 0
        self.timelapse_started = False
        self.change_ui_for_timelapse(start_timelapse=True)

    def change_ui_for_timelapse(self, start_timelapse=True):
        """change_ui_for_timelapse: disable/enable everything possible for/after timelapse"""
        if start_timelapse:
            self.root.ids['timelapse_toggle'].text = 'Stop Timelapse'
            if self.root.ids['toggle_preview'].state == 'down':
                self.cam.stop_preview()
                self.root.ids['toggle_preview'].state = 'normal'
            self.root.ids['toggle_preview'].disabled = True
            self.root.ids['resolution_preview'].disabled = True
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
            self.root.ids['create_video'].disabled = True
            self.root.ids['delete_images'].disabled = True
            self.root.ids['quit'].disabled = True
        else:  # False -> stop timelapse
            self.root.ids['timelapse_toggle'].text = 'Start Timelapse'
            self.root.ids['preview'].source = "1blackpixel.png"
            self.root.ids['infos'].text = "Ready"
            self.root.ids['toggle_preview'].disabled = False
            self.root.ids['resolution_preview'].disabled = False
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
            self.root.ids['create_video'].disabled = False
            self.root.ids['delete_images'].disabled = False
            self.root.ids['quit'].disabled = False

    def perform_capture(self):
        """perform_capture : get one frame and record it as jpg"""
        filename = "images/img_{:05d}.jpg".format(self.frame_counter)
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
        # TODO: find a way to get ffmpeg stats...
        pass

    @staticmethod
    def delete_images():
        """delete_images : empty the images dir"""
        Logger.info("Timelapse: deleting images in the \"images\" dir")
        import os
        os.system('rm images/*')


# Run the app
app = PylapseApp()
app.run()
