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
# global change_img_callback
global pic_click 
global pic
pic_click = False
# change_img_callback = None
# 

class PreviewCallback(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/Camera$PreviewCallback']
    __javacontext__ = 'app'

    def __init__(self ,kivy_image_callback):
        super().__init__()
        self.kivy_image_callback = kivy_image_callback

    @java_method('([BLandroid/hardware/Camera;)V')
    def onPreviewFrame(self, data, camera):
        global pic_click
        if not pic_click:
            return
        pic_click = False

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
        self.kivy_image_callback()

class AddPreviewRunnable(PythonJavaClass):
    __javainterfaces__ = ['java/lang/Runnable']
    __javacontext__ = 'app'

    def __init__(self, activity ,kivy_image_callback):
        super().__init__()
        self.activity = activity
        self.kivy_image_callback = kivy_image_callback

    @java_method('()V')
    def run(self):
        # Get the PreviewView class you created in Java (must be in your Java side code)
        # PreviewView = autoclass('org.kivy.android.PreviewView')
        # FrameLayout = autoclass('android.widget.FrameLayout')
        # FrameLayoutParams = autoclass('android.widget.FrameLayout$LayoutParams')

        # # Create a preview view
        # preview = PreviewView(self.activity)
        # layout_params = FrameLayoutParams(-1, -1)  # MATCH_PARENT int(self.activity.getResources().getDisplayMetrics().heightPixels * 0.6)

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


class LiveCameraApp(App):
    # def build(self):
    #     request_permissions([Permission.CAMERA])
    #     self.layout = BoxLayout(orientation='vertical')

    #     btn = Button(text='Start Camera Preview')
    #     btn.size_hint = (.4 , .8)
    #     # btn.size = (200, 50)
    #     btn.pos_hint = {'center_x': 0.5, 'center_y': 0.9}
    #     btn.bind(on_press=self.start_preview)

    #     self.layout.add_widget(btn)
    #     return self.layout

    # def start_preview(self, instance):
    #     PythonActivity = autoclass('org.kivy.android.PythonActivity')
    #     activity = PythonActivity.mActivity

    #     # Add preview view using a Runnable
    #     preview_runnable = AddPreviewRunnable(activity)
    #     activity.runOnUiThread(preview_runnable)

    #     # Optional: disable the button to prevent adding multiple previews
    #     # instance.disabled = True
    img = None
    source = StringProperty("https://media.istockphoto.com/id/1307609675/photo/bluebird.jpg?s=612x612&w=0&k=20&c=PdSeFBXLNi2n8vNxDjubRQOsaOw_sJ1w7RhtxjGL5GM=")
    def build(self):
        request_permissions([Permission.CAMERA])
        self.layout = FloatLayout()

        btn = Button(text='Start Camera')
        btn.size_hint = None, None
        btn.size = (dp(200), dp(50))
        # btn.size = (200, 50)
        btn.pos_hint = {'center_x': 0.3, 'top': 0.98}
        # btn.bind(on_press=self.start_preview)
        btn.bind(on_press=self.take_picture)

        self.img = AsyncImage(source=self.source)
        self.img.size_hint = None, None
        self.img.size = (dp(200), dp(70))
        self.img.pos_hint = {'center_x': 0.6, 'top': 0.99}

        self.layout.add_widget(btn)
        self.layout.add_widget(self.img)
        return self.layout
    
    def on_start(self):
        # Check if the camera permission is granted
        if check_permission(Permission.CAMERA):
            ## Necessery for the camera to work | requires a delay to init the classes
            Clock.schedule_once(lambda dt: self.start_preview(None), 2)

    def on_resume(self):
        ## Camera disapprears when the app is paused | relaunch the camera on resume
        self.start_preview(None)
        return True
    
    @mainthread
    def change_img(self):
        Clock.schedule_once(lambda dt: setattr(self.img, "source", pic), .5)
        print("Image changed to: ", pic)

    def take_picture(self , instance):
        global pic_click
        global pic
        pic = str(datetime.datetime.now()) + ".jpg"
        pic_click = True
        #
        print(self.img.source , "\n" ,self.img)

    def start_preview(self, instance):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity

        # Add preview view using a Runnable
        preview_runnable = AddPreviewRunnable(activity, self.change_img)
        activity.runOnUiThread(preview_runnable)


if __name__ == "__main__":
    LiveCameraApp().run()
