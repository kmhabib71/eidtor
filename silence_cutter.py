import os
import sys
import time
import tempfile
import atexit
import subprocess
import numpy as np
import io  # Add missing io module
import matplotlib.pyplot as plt
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import moviepy.editor as mp
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QLabel, QPushButton, QSlider, QProgressBar, QFileDialog, QListWidget,
                             QListWidgetItem, QMessageBox, QCheckBox, 
                             QSplitter, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QRectF
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPainterPath, QImage, QPixmap
import cv2

class SilenceDetectionThread(QThread):
    progress_updated = pyqtSignal(int)
    detection_complete = pyqtSignal(list)
    
    def __init__(self, video_path, min_silence_duration=500, silence_threshold=-40):
        super().__init__()
        self.video_path = video_path
        self.min_silence_duration = min_silence_duration
        self.silence_threshold = silence_threshold
        # Get FFmpeg path
        self.ffmpeg_path = self.get_ffmpeg_path()
    
    def get_ffmpeg_path(self):
        """Try to find FFmpeg executable path"""
        # First try directly if it's in PATH
        try:
            # Use subprocess to check if ffmpeg is available
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                return "ffmpeg"  # ffmpeg is in PATH and working
        except Exception:
            pass  # ffmpeg not in PATH or not working
        
        # Check known locations
        known_locations = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Users\\WALTON\\ffmpeg-2025-05-07-git-1b643e3f65-full_build\\ffmpeg-2025-05-07-git-1b643e3f65-full_build\\bin\\ffmpeg.exe",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")
        ]
        
        for location in known_locations:
            if os.path.exists(location):
                return location
                
        # Could not find FFmpeg, will use just the command and hope it works
        return "ffmpeg"
        
    def run(self):
        try:
            print(f"\n---------- SILENCE DETECTION START ----------")
            print(f"Detecting silence with threshold: {self.silence_threshold} dB, min duration: {self.min_silence_duration} ms")
            
            # Modify moviepy's FFMPEG_BINARY setting to use our detected FFmpeg path
            from moviepy.config import change_settings
            change_settings({"FFMPEG_BINARY": self.ffmpeg_path})
            
            # Extract audio from video
            print(f"Loading video from: {self.video_path}")
            video = mp.VideoFileClip(self.video_path)
            audio_duration_ms = int(video.audio.duration * 1000)
            print(f"Video loaded, audio duration: {audio_duration_ms} ms")
            
            # Create temporary audio file with unique name to avoid conflicts
            temp_audio = tempfile.NamedTemporaryFile(suffix=f'_sid_{os.getpid()}_{int(time.time())}.wav', delete=False)
            temp_audio_path = temp_audio.name
            temp_audio.close()
            print(f"Extracting audio to: {temp_audio_path}")
            
            video.audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
            print(f"Audio extracted successfully")
            
            # Load audio and detect non-silent parts
            print(f"Loading audio for silence detection")
            audio = AudioSegment.from_file(temp_audio_path)
            print(f"Audio loaded: duration={len(audio)}ms, channels={audio.channels}, sample_width={audio.sample_width}, frame_rate={audio.frame_rate}")
            
            # Detect non-silent parts (we'll invert this to get silent parts)
            print(f"Detecting non-silent parts with silence threshold={self.silence_threshold}dB, min_silence_len={self.min_silence_duration}ms")
            non_silent_ranges = detect_nonsilent(
                audio,
                min_silence_len=self.min_silence_duration,
                silence_thresh=self.silence_threshold
            )
            print(f"Number of non-silent ranges detected: {len(non_silent_ranges)}")
            if non_silent_ranges:
                for i, (start, end) in enumerate(non_silent_ranges[:5]):  # Show first 5
                    print(f"  Non-silent range {i+1}: {start}ms - {end}ms (duration: {end-start}ms)")
                if len(non_silent_ranges) > 5:
                    print(f"  ... and {len(non_silent_ranges) - 5} more ranges")
            
            # Convert non-silent ranges to silent ranges
            silent_ranges = []
            
            if len(non_silent_ranges) == 0:
                # If no non-silent parts detected, the whole audio is silence
                silent_ranges = [(0, audio_duration_ms)]
                print(f"No non-silent parts detected, treating the entire audio as silence")
            else:
                # Add silent range at the beginning if the first non-silent part doesn't start at 0
                if non_silent_ranges[0][0] > 0:
                    silent_ranges.append((0, non_silent_ranges[0][0]))
                
                # Add silent ranges between non-silent parts
                for i in range(len(non_silent_ranges) - 1):
                    silent_ranges.append((non_silent_ranges[i][1], non_silent_ranges[i+1][0]))
                
                # Add silent range at the end if the last non-silent part doesn't end at the audio duration
                if non_silent_ranges[-1][1] < audio_duration_ms:
                    silent_ranges.append((non_silent_ranges[-1][1], audio_duration_ms))
            
            print(f"Number of initial silent ranges: {len(silent_ranges)}")
            if silent_ranges:
                for i, (start, end) in enumerate(silent_ranges[:5]):  # Show first 5
                    print(f"  Silent range {i+1}: {start}ms - {end}ms (duration: {end-start}ms)")
                if len(silent_ranges) > 5:
                    print(f"  ... and {len(silent_ranges) - 5} more ranges")
            
            # Filter out silent ranges shorter than the minimum duration
            filtered_silent_ranges = [(start, end) for start, end in silent_ranges if end - start >= self.min_silence_duration]
            print(f"After filtering by minimum duration ({self.min_silence_duration}ms): {len(filtered_silent_ranges)} silent ranges")
            
            # Calculate duration of each silent part and create result list
            silent_parts = []
            for i, (start, end) in enumerate(filtered_silent_ranges):
                duration_ms = end - start
                start_sec = start / 1000
                end_sec = end / 1000
                
                # Create a thumbnail from the video at the start of the silence
                silent_parts.append({
                    'id': i,
                    'start': start_sec,
                    'end': end_sec,
                    'duration_ms': duration_ms,
                    'selected': True  # Default to cutting this silence
                })
                
                # Update progress
                progress = int((i + 1) / len(filtered_silent_ranges) * 100)
                self.progress_updated.emit(progress)
            
            # Clean up temp file
            try:
                os.unlink(temp_audio_path)
            except:
                pass
                
            # Emit results
            print(f"Final silent parts count: {len(silent_parts)}")
            print(f"---------- SILENCE DETECTION END ----------\n")
            self.detection_complete.emit(silent_parts)
            
        except Exception as e:
            print(f"Error in silence detection: {str(e)}")
            import traceback
            traceback.print_exc()
            self.detection_complete.emit([])

class ProcessingThread(QThread):
    progress_updated = pyqtSignal(int)
    processing_complete = pyqtSignal(str)
    
    def __init__(self, video_path, silent_parts, output_path):
        super().__init__()
        self.video_path = video_path
        self.silent_parts = silent_parts
        self.output_path = output_path
        # Get FFmpeg path
        self.ffmpeg_path = self.get_ffmpeg_path()
    
    def get_ffmpeg_path(self):
        """Try to find FFmpeg executable path"""
        # First try directly if it's in PATH
        try:
            # Use subprocess to check if ffmpeg is available
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                return "ffmpeg"  # ffmpeg is in PATH and working
        except Exception:
            pass  # ffmpeg not in PATH or not working
        
        # Check known locations
        known_locations = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Users\\WALTON\\ffmpeg-2025-05-07-git-1b643e3f65-full_build\\ffmpeg-2025-05-07-git-1b643e3f65-full_build\\bin\\ffmpeg.exe",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")
        ]
        
        for location in known_locations:
            if os.path.exists(location):
                return location
                
        # Could not find FFmpeg, will use just the command and hope it works
        return "ffmpeg"
        
    def run(self):
        try:
            # Modify moviepy's FFMPEG_BINARY setting to use our detected FFmpeg path
            from moviepy.config import change_settings
            change_settings({"FFMPEG_BINARY": self.ffmpeg_path})
            
            # Load the video
            video = mp.VideoFileClip(self.video_path)
            
            # Create a list of segments to keep
            segments = []
            last_end = 0
            
            # Sort silent parts by start time
            sorted_parts = sorted(self.silent_parts, key=lambda x: x['start'])
            
            for part in sorted_parts:
                if part['selected']:  # Only cut if selected
                    if part['start'] > last_end:
                        # Add segment before the silence
                        segments.append(video.subclip(last_end, part['start']))
                    # Update last_end to be the end of this silent part
                    last_end = part['end']
                
            # Add the final segment if needed
            if last_end < video.duration:
                segments.append(video.subclip(last_end, video.duration))
            
            # If no segments were cut, just use the original video
            if not segments:
                result = video
            else:
                # Concatenate all segments
                result = mp.concatenate_videoclips(segments)
            
            # Create a unique temp filename for audio to avoid conflicts
            temp_audio_file = os.path.join(tempfile.gettempdir(), f"temp-audio-processing-{os.getpid()}-{int(time.time())}.m4a")
            
            # Export the result
            result.write_videofile(
                self.output_path, 
                codec="libx264", 
                audio_codec="aac",
                temp_audiofile=temp_audio_file, 
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            self.processing_complete.emit(self.output_path)
            
        except Exception as e:
            print(f"Error in video processing: {str(e)}")
            import traceback
            traceback.print_exc()
            self.processing_complete.emit("")

class SilencePreviewWidget(QWidget):
    selection_changed = pyqtSignal(dict)
    
    def __init__(self, silent_part, video_path):
        super().__init__()
        self.silent_part = silent_part
        self.video_path = video_path
        # Get the FFmpeg path - try environment or fallback to known location
        self.ffmpeg_path = self.get_ffmpeg_path()
        self.setup_ui()
        
    def get_ffmpeg_path(self):
        """Try to find FFmpeg executable path"""
        # First try directly if it's in PATH
        try:
            # Use subprocess to check if ffmpeg is available
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                return "ffmpeg"  # ffmpeg is in PATH and working
        except Exception:
            pass  # ffmpeg not in PATH or not working
        
        # Check known locations
        known_locations = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Users\\WALTON\\ffmpeg-2025-05-07-git-1b643e3f65-full_build\\ffmpeg-2025-05-07-git-1b643e3f65-full_build\\bin\\ffmpeg.exe",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")
        ]
        
        for location in known_locations:
            if os.path.exists(location):
                return location
                
        # Could not find FFmpeg, will use just the command and hope it works
        return "ffmpeg"
        
    def setup_ui(self):
        layout = QHBoxLayout()
        
        # Checkbox for selection
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.silent_part['selected'])
        self.checkbox.stateChanged.connect(self.on_selection_changed)
        layout.addWidget(self.checkbox)
        
        # Information label
        start_time = self.format_time(self.silent_part['start'])
        end_time = self.format_time(self.silent_part['end'])
        duration = self.silent_part['duration_ms'] / 1000
        
        info_label = QLabel(f"Silence {self.silent_part['id'] + 1}: {start_time} - {end_time} (Duration: {duration:.2f}s)")
        info_label.setFont(QFont("Arial", 10))
        layout.addWidget(info_label, 1)
        
        # Button to preview
        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self.on_preview_clicked)
        layout.addWidget(preview_btn)
        
        self.setLayout(layout)
        
    def on_selection_changed(self, state):
        self.silent_part['selected'] = (state == Qt.Checked)
        self.selection_changed.emit(self.silent_part)
        
    def on_preview_clicked(self):
        try:
            # Extract a short clip around the silent part for preview
            padding = 2.0  # seconds before and after silence
            start = max(0, self.silent_part['start'] - padding)
            end = min(mp.VideoFileClip(self.video_path).duration, self.silent_part['end'] + padding)
            
            # Create temporary file for preview clip in user temp directory with unique name
            preview_suffix = f"_silence_preview_{id(self)}_{int(time.time())}.mp4"
            temp_preview_path = os.path.join(tempfile.gettempdir(), f"silence_preview{preview_suffix}")
            
            # Extract preview clip
            video = mp.VideoFileClip(self.video_path)
            preview_clip = video.subclip(start, end)
            
            # Add a visual indicator for the silent part
            def highlight_silence(get_frame, t):
                frame = get_frame(t)
                # If we're in the silent region, add a red border
                if self.silent_part['start'] <= (start + t) <= self.silent_part['end']:
                    h, w = frame.shape[:2]
                    # Add a red border (20 pixels wide)
                    border_width = 20
                    frame[:border_width, :] = [0, 0, 255]  # Top border
                    frame[-border_width:, :] = [0, 0, 255]  # Bottom border
                    frame[:, :border_width] = [0, 0, 255]  # Left border
                    frame[:, -border_width:] = [0, 0, 255]  # Right border
                    
                    # Add text indicating this is a silent part
                    text = "SILENCE DETECTED"
                    cv2.putText(frame, text, (w//2 - 150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                return frame
            
            # Apply the visual indicator
            preview_clip = preview_clip.fl(highlight_silence)
            
            # Create a unique temp filename for audio to avoid conflicts
            temp_audio_file = os.path.join(tempfile.gettempdir(), f"temp-audio-{os.getpid()}-{id(self)}.m4a")
            
            # Modify moviepy's FFMPEG_BINARY setting to use our detected FFmpeg path
            from moviepy.config import change_settings
            change_settings({"FFMPEG_BINARY": self.ffmpeg_path})
            
            # Write the preview clip
            preview_clip.write_videofile(
                temp_preview_path,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=temp_audio_file,
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Open the preview with the default video player
            if sys.platform == "win32":
                os.startfile(temp_preview_path)
            elif sys.platform == "darwin":
                os.system(f"open {temp_preview_path}")
            else:
                os.system(f"xdg-open {temp_preview_path}")
                
        except Exception as e:
            error_message = f"Could not play preview: {str(e)}"
            QMessageBox.critical(self, "Preview Error", error_message)
            # Log the full error details
            print(f"Preview error details: {e}")
            import traceback
            traceback.print_exc()
    
    def format_time(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"

class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        
        # Create label to display the waveform image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0;")
        self.image_label.setText("No audio data loaded")
        
        # Add the label to the widget layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        
        # Initialize variables
        self.waveform_data = None
        self.silent_ranges = []
        self.duration_ms = 0
        self.error_message = None
        
    def set_audio_data(self, audio_path, silent_ranges=None):
        try:
            print(f"\n---------- WAVEFORM DEBUG ----------")
            print(f"Loading audio data from: {audio_path}")
            
            # Display a loading message
            self.image_label.setText("Loading waveform...")
            QApplication.processEvents()
            
            # Check if the file exists
            if not os.path.exists(audio_path):
                self.error_message = f"Audio file not found: {audio_path}"
                print(self.error_message)
                self.image_label.setText(f"Error: {self.error_message}")
                return
                
            # Check if the file has content
            file_size = os.path.getsize(audio_path)
            print(f"Audio file size: {file_size} bytes")
            if file_size == 0:
                self.error_message = "Audio file is empty (zero size)"
                print(self.error_message)
                self.image_label.setText(f"Error: {self.error_message}")
                return
                
            # Load audio
            try:
                # Report success loading the file directly
                print(f"Loading audio file into memory...")
                audio = AudioSegment.from_file(audio_path)
                self.duration_ms = len(audio)
                print(f"AudioSegment loaded successfully - Duration: {self.duration_ms}ms, Channels: {audio.channels}, Frame rate: {audio.frame_rate}Hz")
                
                # Get samples (downsample for performance)
                print(f"Converting to numpy array...")
                samples = np.array(audio.get_array_of_samples())
                print(f"Successfully converted to numpy array with shape: {samples.shape}")
                print(f"Sample type: {samples.dtype}, Min value: {np.min(samples)}, Max value: {np.max(samples)}")
                
                # Convert stereo to mono if needed
                if audio.channels == 2:
                    print(f"Converting stereo audio to mono...")
                    # Reshape to get left and right channels
                    samples = samples.reshape((-1, 2))
                    # Average the channels
                    samples = samples.mean(axis=1).astype(np.int16)
                    print(f"Stereo converted to mono: {samples.shape}")
                
                print(f"Audio loaded: {len(samples)} samples, {self.duration_ms}ms duration")
                
                # Check if we have data
                if len(samples) == 0:
                    self.error_message = "No samples found in audio file"
                    print(self.error_message)
                    self.image_label.setText(f"Error: {self.error_message}")
                    return
                
                max_samples = 10000  # Limit number of samples for performance
                
                if len(samples) > max_samples:
                    # Downsample
                    step = len(samples) // max_samples
                    samples = samples[::step]
                    print(f"Downsampled to {len(samples)} samples")
                
                # Normalize
                print(f"Normalizing waveform. Min: {np.min(samples)}, Max: {np.max(samples)}")
                if np.max(np.abs(samples)) > 0:
                    # Convert to float for normalization
                    samples = samples.astype(np.float64)
                    samples = samples / np.max(np.abs(samples))
                    print(f"Waveform normalized. New min: {np.min(samples)}, New max: {np.max(samples)}")
                else:
                    print("Warning: Audio contains no signal (all zeros)")
                
                # Verify the data doesn't contain NaN or Inf values
                if np.isnan(samples).any() or np.isinf(samples).any():
                    print("WARNING: Samples contain NaN or Inf values! Fixing...")
                    samples = np.nan_to_num(samples)
                
                print(f"Final waveform data: {len(samples)} samples, type: {samples.dtype}")
                self.waveform_data = samples
                self.error_message = None
                
                # Set silent ranges
                if silent_ranges is not None:
                    print(f"Setting {len(silent_ranges)} silent ranges")
                    self.silent_ranges = silent_ranges
                else:
                    print("No silent ranges provided")
                    self.silent_ranges = []
                
                # Generate and display the waveform image
                self._generate_waveform_image()
                print("Waveform image created and displayed")
                print(f"---------- END WAVEFORM DEBUG ----------\n")
                
            except Exception as e:
                self.error_message = f"Error processing audio: {str(e)}"
                print(self.error_message)
                import traceback
                traceback.print_exc()
                self.image_label.setText(f"Error: {self.error_message}")
                
        except Exception as e:
            self.error_message = f"Error loading audio data: {str(e)}"
            print(self.error_message)
            import traceback
            traceback.print_exc()
            self.image_label.setText(f"Error: {self.error_message}")
    
    def _generate_waveform_image(self):
        """Generate a waveform image and display it in the label"""
        try:
            # Create a matplotlib figure
            plt.figure(figsize=(10, 4), dpi=100)
            
            if self.waveform_data is None or len(self.waveform_data) <= 1:
                plt.text(0.5, 0.5, "No audio data", ha='center', va='center')
            else:
                # Create time axis (x-axis)
                time_axis = np.linspace(0, self.duration_ms / 1000, len(self.waveform_data))
                
                # Plot waveform
                plt.plot(time_axis, self.waveform_data, color='blue', linewidth=0.8)
                
                # Add horizontal line at y=0
                plt.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
                
                # Set axis limits
                plt.xlim(0, self.duration_ms / 1000)
                plt.ylim(-1.1, 1.1)
                
                # Highlight silent regions if any
                if self.silent_ranges and self.duration_ms > 0:
                    for start_ms, end_ms in self.silent_ranges:
                        start_s = start_ms / 1000
                        end_s = end_ms / 1000
                        plt.axvspan(start_s, end_s, color='red', alpha=0.3)
                
                # Set labels and grid
                plt.title("Audio Waveform")
                plt.xlabel("Time (s)")
                plt.ylabel("Amplitude")
                plt.grid(True, alpha=0.3)
            
            # Save to a temporary buffer
            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png')
            plt.close()
            
            # Convert buffer to QPixmap and display in the label
            buf.seek(0)
            image = QImage.fromData(buf.getvalue())
            pixmap = QPixmap.fromImage(image)
            
            # Scale the pixmap to fit the label while maintaining aspect ratio
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.width(), 
                self.image_label.height(),
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
            
        except Exception as e:
            print(f"Error generating waveform image: {str(e)}")
            import traceback
            traceback.print_exc()
            self.image_label.setText(f"Error: {str(e)}")
    
    def update_silent_ranges(self, silent_ranges):
        """Update just the silent ranges without reloading the audio data"""
        self.silent_ranges = silent_ranges
        self._generate_waveform_image()  # Regenerate the waveform image with new silent ranges
    
    def resizeEvent(self, event):
        """Handle widget resize events to scale the image properly"""
        super().resizeEvent(event)
        if hasattr(self, 'image_label') and self.image_label.pixmap() and not self.image_label.pixmap().isNull():
            # Rescale the existing pixmap to the new size
            pixmap = self.image_label.pixmap()
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.width(), 
                self.image_label.height(),
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))

class AudioVisualizationThread(QThread):
    waveform_ready = pyqtSignal(str, list)
    
    def __init__(self, video_path, silent_ranges=None):
        super().__init__()
        self.video_path = video_path
        self.silent_ranges = silent_ranges
        # Get FFmpeg path
        self.ffmpeg_path = self.get_ffmpeg_path()
    
    def get_ffmpeg_path(self):
        """Try to find FFmpeg executable path"""
        # First try directly if it's in PATH
        try:
            # Use subprocess to check if ffmpeg is available
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                return "ffmpeg"  # ffmpeg is in PATH and working
        except Exception:
            pass  # ffmpeg not in PATH or not working
        
        # Check known locations
        known_locations = [
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Users\\WALTON\\ffmpeg-2025-05-07-git-1b643e3f65-full_build\\ffmpeg-2025-05-07-git-1b643e3f65-full_build\\bin\\ffmpeg.exe",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")
        ]
        
        for location in known_locations:
            if os.path.exists(location):
                return location
                
        # Could not find FFmpeg, will use just the command and hope it works
        return "ffmpeg"
        
    def run(self):
        try:
            # Modify moviepy's FFMPEG_BINARY setting to use our detected FFmpeg path
            from moviepy.config import change_settings
            change_settings({"FFMPEG_BINARY": self.ffmpeg_path})
            
            # Extract audio from video
            video = mp.VideoFileClip(self.video_path)
            
            # Create temporary audio file with unique name
            temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_audio_path = temp_audio.name
            temp_audio.close()
            
            video.audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
            
            # Emit signal with audio path and silent ranges
            self.waveform_ready.emit(temp_audio_path, self.silent_ranges)
            
        except Exception as e:
            print(f"Error preparing audio visualization: {str(e)}")
            import traceback
            traceback.print_exc()

class SilenceCutterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.video_path = None
        self.silent_parts = []
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Video Silence Cutter")
        self.setMinimumWidth(900)
        self.setMinimumHeight(700)
        
        # Main layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # File selection area
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setFont(QFont("Arial", 10))
        
        select_btn = QPushButton("Select Video")
        select_btn.clicked.connect(self.select_video)
        
        file_layout.addWidget(select_btn)
        file_layout.addWidget(self.file_label, 1)
        main_layout.addLayout(file_layout)
        
        # Silence threshold controls
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel("Silence Threshold (dB):")
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(-60)
        self.threshold_slider.setMaximum(-20)
        self.threshold_slider.setValue(-40)
        self.threshold_value_label = QLabel("-40 dB")
        
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)
        
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold_slider)
        threshold_layout.addWidget(self.threshold_value_label)
        main_layout.addLayout(threshold_layout)
        
        # Min silence duration controls
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Min Silence Duration (ms):")
        self.duration_slider = QSlider(Qt.Horizontal)
        self.duration_slider.setMinimum(100)
        self.duration_slider.setMaximum(2000)
        self.duration_slider.setValue(500)
        self.duration_value_label = QLabel("500 ms")
        
        self.duration_slider.valueChanged.connect(self.update_duration_label)
        
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_slider)
        duration_layout.addWidget(self.duration_value_label)
        main_layout.addLayout(duration_layout)
        
        # Detect button
        self.detect_btn = QPushButton("Detect Silence")
        self.detect_btn.clicked.connect(self.detect_silence)
        self.detect_btn.setEnabled(False)
        main_layout.addWidget(self.detect_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Waveform visualization
        waveform_label = QLabel("Audio Waveform and Silence Visualization:")
        waveform_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(waveform_label)
        
        self.waveform_widget = WaveformWidget()
        main_layout.addWidget(self.waveform_widget)
        
        # Silence list
        silence_list_label = QLabel("Detected Silence Segments:")
        silence_list_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(silence_list_label)
        
        self.silence_list = QListWidget()
        main_layout.addWidget(self.silence_list)
        
        # Select/Deselect All buttons
        select_buttons_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_silences)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all_silences)
        
        select_buttons_layout.addWidget(select_all_btn)
        select_buttons_layout.addWidget(deselect_all_btn)
        main_layout.addLayout(select_buttons_layout)
        
        # Process button
        self.process_btn = QPushButton("Process and Save Video")
        self.process_btn.clicked.connect(self.process_video)
        self.process_btn.setEnabled(False)
        main_layout.addWidget(self.process_btn)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def update_threshold_label(self):
        value = self.threshold_slider.value()
        self.threshold_value_label.setText(f"{value} dB")
    
    def update_duration_label(self):
        value = self.duration_slider.value()
        self.duration_value_label.setText(f"{value} ms")
    
    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "", "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv)"
        )
        
        if file_path:
            self.video_path = file_path
            file_name = os.path.basename(file_path)
            self.file_label.setText(file_name)
            self.detect_btn.setEnabled(True)
            # Clear previous results
            self.silence_list.clear()
            self.silent_parts = []
            self.process_btn.setEnabled(False)
    
    def detect_silence(self):
        if not self.video_path:
            return
        
        # Get current threshold and duration values
        silence_threshold = self.threshold_slider.value()
        min_silence_duration = self.duration_slider.value()
        
        # Disable UI elements during detection
        self.detect_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Start the detection thread
        self.detection_thread = SilenceDetectionThread(
            self.video_path, 
            min_silence_duration=min_silence_duration,
            silence_threshold=silence_threshold
        )
        self.detection_thread.progress_updated.connect(self.update_detection_progress)
        self.detection_thread.detection_complete.connect(self.show_detection_results)
        self.detection_thread.start()
    
    def update_detection_progress(self, progress):
        self.progress_bar.setValue(progress)
    
    def show_detection_results(self, silent_parts):
        self.progress_bar.setVisible(False)
        self.detect_btn.setEnabled(True)
        
        print(f"\n---------- SILENCE DETECTION RESULTS ----------")
        print(f"Number of silent parts detected: {len(silent_parts)}")
        if silent_parts:
            for i, part in enumerate(silent_parts[:5]):  # Show first 5
                print(f"  Silence {i+1}: {part['start']:.2f}s - {part['end']:.2f}s (duration: {part['duration_ms']/1000:.2f}s)")
            if len(silent_parts) > 5:
                print(f"  ... and {len(silent_parts) - 5} more parts")
        else:
            print("  No silence parts were detected with current settings.")
        print(f"---------- END SILENCE DETECTION RESULTS ----------\n")
        
        if not silent_parts:
            QMessageBox.information(self, "Detection Results", "No silence detected with current settings.")
            return
        
        self.silent_parts = silent_parts
        self.silence_list.clear()
        
        # Convert silent_parts to ranges for visualization
        silent_ranges_ms = []
        for part in silent_parts:
            start_ms = int(part['start'] * 1000)
            end_ms = int(part['end'] * 1000)
            silent_ranges_ms.append((start_ms, end_ms))
        
        # Start thread to prepare and display audio visualization
        self.visualization_thread = AudioVisualizationThread(self.video_path, silent_ranges_ms)
        self.visualization_thread.waveform_ready.connect(self.update_waveform)
        self.visualization_thread.start()
        
        # Add each silent part to the list
        for part in silent_parts:
            item = QListWidgetItem()
            item.setSizeHint(QSize(self.silence_list.width(), 50))
            self.silence_list.addItem(item)
            
            widget = SilencePreviewWidget(part, self.video_path)
            widget.selection_changed.connect(self.on_silence_selection_changed)
            self.silence_list.setItemWidget(item, widget)
        
        self.process_btn.setEnabled(True)
    
    def on_silence_selection_changed(self, silent_part):
        # Update the visual appearance of the waveform
        self.update_waveform_highlighting()
    
    def update_waveform_highlighting(self):
        # Get only the selected silent parts
        silent_ranges_ms = []
        for part in self.silent_parts:
            if part['selected']:
                start_ms = int(part['start'] * 1000)
                end_ms = int(part['end'] * 1000)
                silent_ranges_ms.append((start_ms, end_ms))
        
        # Update the waveform with new highlighting
        self.waveform_widget.update_silent_ranges(silent_ranges_ms)
    
    def update_waveform(self, audio_path, silent_ranges):
        # Update the waveform visualization with the audio and silent ranges
        self.waveform_widget.set_audio_data(audio_path, silent_ranges)
        
        # Clean up the temporary audio file after a delay
        QTimer.singleShot(1000, lambda: os.unlink(audio_path) if os.path.exists(audio_path) else None)
    
    def select_all_silences(self):
        for i in range(self.silence_list.count()):
            item = self.silence_list.item(i)
            widget = self.silence_list.itemWidget(item)
            widget.checkbox.setChecked(True)
        
        # Update waveform highlighting
        self.update_waveform_highlighting()
    
    def deselect_all_silences(self):
        for i in range(self.silence_list.count()):
            item = self.silence_list.item(i)
            widget = self.silence_list.itemWidget(item)
            widget.checkbox.setChecked(False)
        
        # Update waveform highlighting
        self.update_waveform_highlighting()
    
    def process_video(self):
        if not self.video_path or not self.silent_parts:
            return
        
        # Check if any silence parts are selected for cutting
        if not any(part['selected'] for part in self.silent_parts):
            QMessageBox.information(
                self, 
                "No Selections", 
                "No silence segments are selected for cutting. Please select at least one segment."
            )
            return
        
        # Get output file path
        file_name = os.path.basename(self.video_path)
        base_name, ext = os.path.splitext(file_name)
        suggested_name = f"{base_name}_silences_removed{ext}"
        
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Output Video", suggested_name, f"Video Files (*{ext})"
        )
        
        if not output_path:
            return
        
        # Disable UI during processing
        self.process_btn.setEnabled(False)
        self.detect_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Start processing thread
        self.processing_thread = ProcessingThread(
            self.video_path,
            self.silent_parts,
            output_path
        )
        self.processing_thread.progress_updated.connect(self.update_processing_progress)
        self.processing_thread.processing_complete.connect(self.show_processing_results)
        self.processing_thread.start()
    
    def update_processing_progress(self, progress):
        self.progress_bar.setValue(progress)
    
    def show_processing_results(self, output_path):
        self.progress_bar.setVisible(False)
        self.detect_btn.setEnabled(True)
        self.process_btn.setEnabled(True)
        
        if output_path:
            QMessageBox.information(
                self,
                "Processing Complete",
                f"Video processed successfully and saved to:\n{output_path}"
            )
        else:
            QMessageBox.critical(
                self,
                "Processing Error",
                "An error occurred during video processing. Please check console for details."
            )

# Clean up any temporary files on exit
def cleanup_temp_files():
    temp_dir = tempfile.gettempdir()
    try:
        for filename in os.listdir(temp_dir):
            if filename.startswith("temp-audio-") and (filename.endswith(".m4a") or filename.endswith(".wav")):
                try:
                    os.unlink(os.path.join(temp_dir, filename))
                except:
                    pass
    except:
        pass

# Register the cleanup function
atexit.register(cleanup_temp_files)

def main():
    app = QApplication(sys.argv)
    window = SilenceCutterApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 