# Mashaaer Feelings App - Deployment Checklist

## Pre-Deployment Preparation

- [ ] Verify all features work as expected in the latest build
- [ ] Complete all items in the `TESTING_CHECKLIST.md` document
- [ ] Update the `DEFAULT_SERVER_URL` in `android/src/kivy_app.py` to point to the production server
- [ ] Generate both debug and release APK files
- [ ] Test both APK files on at least two different Android devices
- [ ] Verify that offline functionality works when the server is unreachable

## APK Building Process

- [ ] Make sure all dependencies are installed:
  ```
  pip install buildozer
  sudo apt-get install -y python3-pip build-essential git python3 python3-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev libgstreamer1.0-dev gstreamer1.0-plugins-{bad,base,good,ugly} gstreamer1.0-{tools,alsa} libgstreamer-plugins-base1.0-dev
  ```

- [ ] Run the build script:
  ```
  cd android
  chmod +x build_apk.sh
  ./build_apk.sh
  ```

- [ ] Verify the APK was created in the `bin/` directory
- [ ] For release version, run:
  ```
  buildozer android release
  ```

## Documentation Package

- [ ] Finalize the following documentation:
  - [ ] `USER_GUIDE.md`
  - [ ] `KNOWN_ISSUES.md`
  - [ ] `RELEASE_NOTES.md`
  - [ ] `FEEDBACK_FORM.md`

- [ ] Create a simple README for the package that explains what each file is

- [ ] Bundle the documents with the APK in a zip file named `Mashaaer_Feelings_v1.0.zip`

## Google Drive Upload

- [ ] Create a new folder in Google Drive titled "Mashaaer Feelings App"
- [ ] Upload the following files:
  - [ ] Debug APK
  - [ ] Release APK
  - [ ] Documentation package zip file
  - [ ] Individual documentation files

- [ ] Set appropriate sharing permissions:
  - [ ] Create a shareable link for the APK file
  - [ ] Set permissions to "Anyone with the link can view"

## QR Code Generation

- [ ] Go to a QR code generator website (e.g., https://www.qrcode-monkey.com/)
- [ ] Enter the Google Drive shareable link for the APK
- [ ] Generate a QR code and download it
- [ ] Include the QR code in the documentation package

## Final Verification

- [ ] Test downloading the APK using the QR code
- [ ] Install the APK from the download
- [ ] Verify app launches correctly
- [ ] Test a few basic features to ensure the deployed version works
- [ ] Verify server connection is working with the production server URL

## Communication

- [ ] Prepare an email template for sending to testers/users that includes:
  - [ ] Brief description of the app
  - [ ] QR code for easy download
  - [ ] Link to the Google Drive folder
  - [ ] Instructions for providing feedback
  - [ ] Known issues summary
  - [ ] Contact information for support

- [ ] Create a simple landing page or web view for users scanning the QR code

## Post-Deployment Monitoring

- [ ] Set up a system to collect and organize user feedback
- [ ] Create a spreadsheet to track reported issues
- [ ] Establish a plan for addressing critical bugs
- [ ] Schedule follow-up meetings to discuss user feedback and plan updates

## Initial Response Plan

- [ ] Designate team members responsible for:
  - [ ] Technical support inquiries
  - [ ] Bug fixes
  - [ ] Feature requests evaluation
  - [ ] User feedback collection

- [ ] Set response time expectations for different types of issues:
  - [ ] Critical bugs: ____ hours
  - [ ] Major issues: ____ days
  - [ ] Feature requests: ____ weeks

## App Maintenance Plan

- [ ] Establish a regular update schedule based on feedback
- [ ] Create a prioritized list of improvements for the next version
- [ ] Set up a version tracking system for future releases