from kivy.app import App
from kivy.uix.button import Button
from jnius import autoclass, PythonJavaClass, java_method
from android.permissions import request_permissions, Permission , check_permission
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
from kivy.clock import Clock , mainthread
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.metrics import dp
import os , datetime

# 
try: 
    from pyzbar.pyzbar import decode
    from PIL import Image
except ImportError:
    print("pyzbar or PIL not installed. QR code decoding will not work.")
    decode = None
    Image = None
# 


__all__ = ("toast",)

from kivy import platform

if platform != "android":
    raise TypeError(
        f"{platform.capitalize()} platform does not support Android Toast"
    )

from android.runnable import run_on_ui_thread
from jnius import autoclass

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

        # Save to Pictures directory
        # pictures_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES)
        # image_file = File(pictures_dir, "captured_image.jpg")
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
        # try: self.preview.stopAndRemove()
        # except Exception as e: print(e)
        # finally: setattr(self , "preview" , None)
        ##
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
        print(Window.size)

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
    def __init__(self):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def take_picture(self):
        pass


class LiveCameraApp(App):
    img = None
    source = StringProperty("https://media.istockphoto.com/id/1307609675/photo/bluebird.jpg?s=612x612&w=0&k=20&c=PdSeFBXLNi2n8vNxDjubRQOsaOw_sJ1w7RhtxjGL5GM=")
    ## PreviewClass
    preview_runnable = None
    flash_ = False
    recycle_items = []


    def build(self):
        request_permissions([Permission.CAMERA])
        self.layout = FloatLayout()

        btn = Button(text='Start QR Scanner')
        btn.size_hint = None, None
        btn.size = (dp(200), dp(50))
        # btn.size = (200, 50)
        btn.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        # btn.bind(on_press=self.start_preview)
        btn.bind(on_press=self.launch_camera)

        ## close preview
        bt = Button(text='Close QR Scanner')
        bt.size_hint = None, None
        bt.size = (dp(150), dp(50))
        # btn.size = (200, 50)
        bt.pos_hint = {'center_x': 0.2, 'top': 0.98}
        # btn.bind(on_press=self.start_preview)
        bt.bind(on_press=self.close_camera)

        ## flash preview
        bf = Button(text='Flashlight')
        bf.size_hint = None, None
        bf.size = (dp(150), dp(50))
        # btn.size = (200, 50)
        bf.pos_hint = {'center_x': 0.8, 'top': 0.98}
        # btn.bind(on_press=self.start_preview)
        bf.bind(on_press=self.flashlight)

        self.img = AsyncImage(source=self.source)
        self.img.size_hint = None, None
        self.img.size = (dp(200), dp(70))
        self.img.pos_hint = {'center_x': 0.5, 'top': 0.99}

        self.layout.add_widget(btn)
        self.layout.add_widget(bt)
        self.layout.add_widget(bf)
        self.layout.add_widget(self.img)
        return self.layout
    
    def on_start(self): ...

    def on_resume(self):
        ## Camera disapprears when the app is paused | relaunch the camera on resume
        self.start_preview(None)
        return True
    
    @mainthread
    def change_img(self , path):
        Clock.schedule_once(lambda dt: setattr(self.img, "source", path), .5)
        print("Image changed to: ", path)

        [os.remove(image) for image in self.recycle_items if os.path.exists(image)]
        self.recycle_items.clear()

        try:
            with Image.open(path) as img:
                # Convert the image to grayscale
                img = img.convert("L")

            # Decode the QR code using pyzbar
            decoded_objects = decode(img)

            # Print the results
            for obj in decoded_objects:
                print(f"Decoded QR code: {obj.data.decode('utf-8')}")
                toast(obj.data.decode('utf-8'))

        except Exception as e:
            print("Error decoding QR code:", e)
        finally:
            self.recycle_items.append(path)
    
    def scan(self,instance): 
      try:
        if self.preview_runnable : setattr(self.preview_runnable.preview_callback , "take_picture", True)
        else: print("self.preview_runnable is " , self.preview_runnable)
      except Exception as e: print(e)

    def launch_camera(self , instance):
        # This method is called to start the camera preview
        if self.preview_runnable is None and check_permission(Permission.CAMERA):
            print("Starting camera preview...")
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            self.preview_runnable = AddPreviewRunnable(activity, self.change_img)
            activity.runOnUiThread(self.preview_runnable)
            # start qr scan
            Clock.schedule_interval(lambda dt: self.scan(None), 0.7)
        else:
            print("Camera permission not granted or preview already running.")
            request_permissions([Permission.CAMERA])
    
    def close_camera(self , instance): 
      if self.preview_runnable: 
        try: self.preview_runnable.close()
        except Exception as e : print(e)

    def flashlight(self, instance):
      if self.preview_runnable: 
        self.flash_ = not self.flash_
        try: self.preview_runnable.flash(self.flash_)
        except Exception as e : print(e)

    def start_preview(self, instance):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity

        # Add preview view using a Runnable
        self.preview_runnable = AddPreviewRunnable(activity, self.change_img)
        activity.runOnUiThread(self.preview_runnable)



if __name__ == "__main__":
    LiveCameraApp().run()
