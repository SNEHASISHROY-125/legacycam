# LBarCam

LBarCam is a QR and barcode scanner app for Android, built with [Kivy](https://kivy.org/) and using the legacy Android Camera API. It provides a simple interface to scan QR codes and barcodes using your device's camera, leveraging Python and Java integration via Pyjnius.

![6167837306849969573](https://github.com/user-attachments/assets/2f47c720-326f-4cda-9d39-e07aff7cfe77)

## Features

- **Live Camera Preview:** Uses the legacy Android Camera API for compatibility with a wide range of devices.
- **QR & Barcode Scanning:** Decodes QR codes and barcodes in real time using [pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar) and [Pillow](https://python-pillow.org/).
- **Kivy UI:** Modern, touch-friendly interface built with Kivy.
- **Android Integration:** Uses Pyjnius to access Java APIs and display camera preview directly in the app.

## Requirements

- Python 3.10+
- [Kivy](https://kivy.org/) (2.3.1 recommended)
- [Buildozer](https://github.com/kivy/buildozer) for packaging the app for Android
- [pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar)
- [Pillow](https://python-pillow.org/)
- Android SDK/NDK (handled by Buildozer)
- Java JDK

### System Dependencies

Before running or building the app, install the following system dependency (see [issue #54](https://github.com/kivy-garden/zbarcam/issues/54)):

```sh
!sudo apt-get install gettext
```

## Setup

1. **Install Buildozer:**

   ```sh
   !pip install buildozer
   !sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
   !pip install cython==0.29.33
   !sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    python3 \
    python3-dev \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev
   !sudo apt-get install -y \
    libgstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good
   !sudo apt-get install build-essential libsqlite3-dev sqlite3 bzip2 libbz2-dev zlib1g-dev libssl-dev openssl libgdbm-dev libgdbm-compat-dev liblzma-dev libreadline-dev libncursesw5-dev libffi-dev uuid-dev libffi7
   !sudo apt-get install libffi-dev
   !sudo apt-get install gettext
   ```


2. **Build for Android:**

   Edit `buildozer.spec` as needed (see included [buildozer.spec](buildozer.spec) and [qrscanner/buildozer.spec](qrscanner/buildozer.spec)).

   ```sh
   buildozer -v android debug
   ```

5. **Run on Android device:**

   Connect your device via USB and run:

   ```sh
   buildozer android deploy run
   ```

## How to Use

1. **Import LegacyScanner:**

```sh
from lbarcam.LbarCam import LegacyScanner
```

2. **Construct the Scanner:**

```sh
self.scanner = LegacyScanner(self.change_img, recycle_frames=True)
```

3. **Relaunch camera preview ``on_pause`` as it disapprears when the app is paused**

```sh
self.scanner.start_preview()
```

4. **Start Camera Preview and ``scheduled`` Scanning**

```sh
if not self.schedule_scan:
   self.scanner.start_preview()
   self.schedule_scan = Clock.schedule_interval(lambda dt: self.scanner.scan(), 0.7)
```

5. **Stop Camera Preview and ``Unschedule`` Scanning**
```sh
if self.schedule_scan:
   Clock.unschedule(self.schedule_scan)
   self.schedule_scan = None

self.scanner.stop_preview()
```

## Notes

- The app uses the legacy Android Camera API for maximum compatibility, but this API is deprecated on newer Android versions. For modern devices, consider migrating to Camera2 API.
- Make sure to grant camera permissions on your device.
- If you encounter issues with QR decoding, ensure `pyzbar` and `Pillow` are installed and available in your environment.

## License

MIT License. See [LICENSE](LICENSE) for details.

---

**Author:** Snehasish Roy  
**Project:** LBarCam – QR & Barcode Scanner for Kivy/Android
