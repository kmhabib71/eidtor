import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from silence_cutter import SilenceCutterApp

def main():
    """Run the silence cutter application with a test video"""
    app = QApplication(sys.argv)
    window = SilenceCutterApp()
    
    # Test video file - update this path to a video file on your system
    test_video = r"C:/Users/WALTON/Videos/Captures/13.mp4"
    
    if os.path.exists(test_video):
        print(f"Loading test video: {test_video}")
        # Load the video after the app is initialized
        QTimer.singleShot(500, lambda: load_and_detect(window, test_video))
    else:
        print(f"Test video not found: {test_video}")
    
    window.show()
    sys.exit(app.exec_())

def load_and_detect(window, video_path):
    """Load the video file and start silence detection"""
    # Set the video path
    window.video_path = video_path
    file_name = os.path.basename(video_path)
    window.file_label.setText(file_name)
    window.detect_btn.setEnabled(True)
    
    # Clear previous results
    window.silence_list.clear()
    window.silent_parts = []
    window.process_btn.setEnabled(False)
    
    # Set more sensitive detection settings
    window.threshold_slider.setValue(-60)  # More sensitive threshold
    window.duration_slider.setValue(300)   # Shorter minimum duration
    
    # Start silence detection automatically
    print("Starting automatic silence detection...")
    window.detect_silence()

if __name__ == "__main__":
    main() 