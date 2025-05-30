# legacy camera

from jnius import autoclass, PythonJavaClass, java_method
from android.permissions import request_permissions, Permission , check_permission
from android.runnable import run_on_ui_thread
import os , datetime


from kivy import platform

if platform != "android":
    raise TypeError(
        f"{platform.capitalize()} platform does not support Android Toast"
    )

__all__ = ("toast",)
activity = autoclass("org.kivy.android.PythonActivity").mActivity
Toast = autoclass("android.widget.Toast")
String = autoclass("java.lang.String")

@run_on_ui_thread
def toast(text, length_long=False, gravity=0, y=0, x=0):
    """
    Displays a toast.

    :param length_long: the amount of time (in seconds) that the toast is
           visible on the screen;
    :param text: text to be displayed in the toast;
    :param short_duration:  duration of the toast, if `True` the toast
           will last 2.3s but if it is `False` the toast will last 3.9s;
    :param gravity: refers to the toast position, if it is 80 the toast will
           be shown below, if it is 40 the toast will be displayed above;
    :param y: refers to the vertical position of the toast;
    :param x: refers to the horizontal position of the toast;

    Important: if only the text value is specified and the value of
    the `gravity`, `y`, `x` parameters is not specified, their values will
    be 0 which means that the toast will be shown in the center.
    """

    duration = Toast.LENGTH_SHORT if length_long else Toast.LENGTH_LONG
    t = Toast.makeText(activity, String(text), duration)
    t.setGravity(gravity, x, y)
    t.show()



class PreviewCallback(PythonJavaClass):
    """
    Callback class to handle camera preview frames and save them as images.
    This class implements the `android.hardware.Camera.PreviewCallback` interface.
    *kivy_image_callback*

    *returns*
    - ``saved image path``
    """
    __javainterfaces__ = ['android/hardware/Camera$PreviewCallback']
    __javacontext__ = 'app'
    take_picture = False

    def __init__(self ,kivy_image_callback):
        super().__init__()
        self.kivy_image_callback = kivy_image_callback

    @java_method('([BLandroid/hardware/Camera;)V')
    def onPreviewFrame(self, data, camera):
        # global pic_click
        if not self.take_picture:
            return
        self.take_picture = False

        print("take picture" , self.take_picture)

        # check for cache/ exists
        if not os.path.exists("cache"): os.makedirs("cache", exist_ok=True)
        pic = os.path.join("cache", str(datetime.datetime.now()) + ".jpg")

        # Convert YUV to JPEG and save image
        YuvImage = autoclass('android.graphics.YuvImage')
        Rect = autoclass('android.graphics.Rect')
        ByteArrayOutputStream = autoclass('java.io.ByteArrayOutputStream')
        FileOutputStream = autoclass('java.io.FileOutputStream')
        Environment = autoclass('android.os.Environment')
        File = autoclass('java.io.File')

        params = camera.getParameters()
        size = params.getPreviewSize()
        width = size.width
        height = size.height

        yuv = YuvImage(data, params.getPreviewFormat(), width, height, None)
        stream = ByteArrayOutputStream()
        rect = Rect(0, 0, width, height)
        yuv.compressToJpeg(rect, 90, stream)

        ## Save to Pictures directory
        # pictures_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES)
        # image_file = File(pictures_dir, "captured_image.jpg")
        ##
        fos = FileOutputStream(pic)
        fos.write(stream.toByteArray())
        fos.close()
        print("captured frame")
        # change kivy image
        self.kivy_image_callback(pic)

class AddPreviewRunnable(PythonJavaClass):
    __javainterfaces__ = ['java/lang/Runnable']
    __javacontext__ = 'app'
    preview = None
    preview_callback = None

    def __init__(self, activity ,kivy_image_callback):
        super().__init__()
        self.activity = activity
        self.kivy_image_callback = kivy_image_callback

    def flash(self, enable):
      try: self.preview.setFlashlight(enable)
      except Exception as e: print("Failed to toggle flashlight:", e)

    def close(self):
      if self.preview: 
        ## Remove the preview view from the layout | runonui_thread else throws error
        from jnius import PythonJavaClass, java_method
        class RemovePreviewRunnable(PythonJavaClass):
            __javainterfaces__ = ['java/lang/Runnable']
            __javacontext__ = 'app'

            def __init__(self, preview):
                super().__init__()
                self.preview = preview

            @java_method('()V')
            def run(self):
                try:
                    self.preview.stopAndRemove()
                except Exception as e:
                    print("Error during preview removal:", e)
        # Dispatch on UI thread
        try:
          runnable = RemovePreviewRunnable(self.preview)
          self.activity.runOnUiThread(runnable)
        except Exception as e: print(e)

    @java_method('()V')
    def run(self):
        # Get the PreviewView class you created in Java (must be in your Java side code)
        # PreviewView = autoclass('org.kivy.android.PreviewView')
        # FrameLayout = autoclass('android.widget.FrameLayout')
        # FrameLayoutParams = autoclass('android.widget.FrameLayout$LayoutParams')

        # # Create a preview view
        # preview = PreviewView(self.activity)
        # layout_params = FrameLayoutParams(-1, -1)  # MATCH_PARENT int(self.activity.getResources().getDisplayMetrics().heightPixels * 0.6) ## 60% height and top top

        # # Add to root layout
        # self.activity.addContentView(preview, layout_params)
        ## Cam Preview + space at the top
        PreviewView = autoclass('org.kivy.android.PreviewView')
        LinearLayout = autoclass('android.widget.LinearLayout')
        LinearLayoutParams = autoclass('android.widget.LinearLayout$LayoutParams')
        FrameLayout = autoclass('android.widget.FrameLayout')
        FrameLayoutParams = autoclass('android.widget.FrameLayout$LayoutParams')
        View = autoclass('android.view.View')

        # Get screen height and calculate desired preview height (e.g., 40% of screen)
        display_metrics = self.activity.getResources().getDisplayMetrics()
        screen_height = display_metrics.heightPixels
        preview_height = int(screen_height * 0.9)
        # Debugging output
        print("Screen height: ", screen_height )
        print("Preview height: ", preview_height)
        print("Preview height in dp: ", int(preview_height / display_metrics.density))
        # print(Window.size)

        # Create a spacer view to push preview to the bottom
        spacer_height = screen_height - preview_height
        spacer = View(self.activity)
        spacer_params = LinearLayoutParams(LinearLayoutParams.MATCH_PARENT, spacer_height)

        # Create the PreviewView
        preview = PreviewView(self.activity)
        preview_params = LinearLayoutParams(LinearLayoutParams.MATCH_PARENT, LinearLayoutParams.MATCH_PARENT)
        # add the callback
        self.preview_callback = PreviewCallback(self.kivy_image_callback)
        preview.setPreviewCallback(self.preview_callback)

        # Create vertical LinearLayout and add spacer + preview
        linear_layout = LinearLayout(self.activity)
        linear_layout.setOrientation(LinearLayout.VERTICAL)
        linear_layout.addView(spacer, spacer_params)
        linear_layout.addView(preview, preview_params)

        # Add LinearLayout to the root view
        frame_params = FrameLayoutParams(FrameLayoutParams.MATCH_PARENT, FrameLayoutParams.MATCH_PARENT)
        self.activity.addContentView(linear_layout, frame_params)

        ###
        self.preview = preview


class LegacyCamera:
    """
    Legacy camera class implements legacy android camera API eg. android.hardware.Camera
    """

    from jnius import autoclass
    from android.permissions import request_permissions, Permission, check_permission
    
    preview_runnable = None
    flash_ = False

    def __init__(self,image_callback):
        """ callback when a pic is taken """
        self.image_callback = image_callback

    def start(self):
        # This method is called to start the camera preview
        if self.preview_runnable is None and check_permission(Permission.CAMERA):
            print("Starting camera preview...")
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            self.preview_runnable = AddPreviewRunnable(activity, self.image_callback)
            activity.runOnUiThread(self.preview_runnable)
            return True

        else:
            print("Camera permission not granted or preview already running.")
            toast("Camera permission not granted")
            request_permissions([Permission.CAMERA])
            return False

    def stop(self):
        if self.preview_runnable: 
            try: self.preview_runnable.close()
            except Exception as e : print(e)
            # clear the preview 
            self.preview_runnable = None

    def flash(self):
        """
        Toggle the flashlight on or off.
        """
        if self.preview_runnable: 
            self.flash_ = not self.flash_
            try: self.preview_runnable.flash(self.flash_)
            except Exception as e : print(e)
            finally: return self.flash_

    def take_picture(self):
        try:
            if self.preview_runnable: setattr(self.preview_runnable.preview_callback, "take_picture", True)
            else: print("self.preview_runnable is ", self.preview_runnable)
        except Exception as e: print(e)
        finally: return self.preview_runnable is not None
