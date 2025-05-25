package org.kivy.android;

import android.content.Context;
import android.hardware.Camera;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import java.util.List;

public class PreviewView extends SurfaceView implements SurfaceHolder.Callback {
    private SurfaceHolder mHolder;
    private Camera mCamera;

    public PreviewView(Context context) {
        super(context);

        mCamera = Camera.open();
        mCamera.setDisplayOrientation(90);  // Rotate preview

        mHolder = getHolder();
        mHolder.addCallback(this);
    }
    // capture callback
    public void setPreviewCallback(Camera.PreviewCallback callback) {
    if (mCamera != null) {
        mCamera.setPreviewCallback(callback);
        }
    }

    @Override
    public void surfaceCreated(SurfaceHolder holder) {
        try {
            Camera.Parameters params = mCamera.getParameters();

            // Set high resolution if available
            List<Camera.Size> sizes = params.getSupportedPreviewSizes();
            for (Camera.Size size : sizes) {
                if (size.width == 1280 && size.height == 720) {
                    params.setPreviewSize(size.width, size.height);
                    break;
                }
            }
            // ✅ Set autofocus mode to continuous picture
            List<String> focusModes = params.getSupportedFocusModes();
            if (focusModes != null && focusModes.contains(Camera.Parameters.FOCUS_MODE_CONTINUOUS_PICTURE)) {
                params.setFocusMode(Camera.Parameters.FOCUS_MODE_CONTINUOUS_PICTURE);
            } else if (focusModes.contains(Camera.Parameters.FOCUS_MODE_AUTO)) {
                params.setFocusMode(Camera.Parameters.FOCUS_MODE_AUTO);
            }

            mCamera.setParameters(params);
            mCamera.setPreviewDisplay(holder);
            mCamera.startPreview();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    public void surfaceChanged(SurfaceHolder holder, int format, int width, int height) {}

    @Override
    public void surfaceDestroyed(SurfaceHolder holder) {
        if (mCamera != null) {
          mCamera.setPreviewCallback(null);  // VERY IMPORTANT
          mCamera.stopPreview();
          mCamera.release();
          mCamera = null;
      }
    }
}
