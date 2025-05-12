import logging
import os
import time
import tempfile
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import cv2
from moviepy.editor import VideoFileClip, concatenate_videoclips
from pydub import AudioSegment
from pydub.silence import detect_silence
import matplotlib.pyplot as plt

from app.core.config import settings
from app.models.video import ProcessingStatus, VideoProcessingSettings, SilenceSegment
from app.services.storage_service import save_file_to_storage, delete_file, get_file_url
from app.services.video_service import update_video_status

logger = logging.getLogger("silence-cutter")

async def detect_silence_segments(
    audio_file_path: str,
    processing_settings: VideoProcessingSettings
) -> List[Tuple[int, int]]:
    """
    Detect silence segments in an audio file
    Returns a list of tuples with (start_ms, end_ms)
    """
    try:
        # Load audio file
        audio = AudioSegment.from_file(audio_file_path)
        
        # Detect silence
        silence_segments = detect_silence(
            audio,
            min_silence_len=processing_settings.min_silence_duration_ms,
            silence_thresh=processing_settings.silence_threshold_db
        )
        
        return silence_segments
    except Exception as e:
        logger.error(f"Error detecting silence: {str(e)}")
        raise

async def generate_silence_visualization(
    audio_file_path: str,
    silence_segments: List[Tuple[int, int]],
    output_path: str
):
    """Generate a visualization of the audio waveform with silence segments highlighted"""
    try:
        # Load audio file
        audio = AudioSegment.from_file(audio_file_path)
        
        # Convert audio to numpy array
        samples = np.array(audio.get_array_of_samples())
        
        # Create figure
        plt.figure(figsize=(15, 5))
        
        # Plot waveform
        plt.plot(samples, color='blue', alpha=0.5)
        
        # Highlight silence segments
        max_amplitude = max(abs(samples))
        for start_ms, end_ms in silence_segments:
            start_idx = int(start_ms * audio.frame_rate / 1000)
            end_idx = int(end_ms * audio.frame_rate / 1000)
            
            if start_idx < len(samples) and end_idx <= len(samples):
                plt.axvspan(start_idx, end_idx, color='red', alpha=0.3)
        
        plt.title("Audio Waveform with Silence Segments")
        plt.xlabel("Samples")
        plt.ylabel("Amplitude")
        plt.tight_layout()
        
        # Save figure
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    except Exception as e:
        logger.error(f"Error generating silence visualization: {str(e)}")
        return None

async def process_video(
    video_id: str,
    input_file_path: str,
    processing_settings: VideoProcessingSettings
) -> Dict[str, Any]:
    """
    Process a video to remove silence segments
    """
    # Create temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Update status to processing
            await update_video_status(
                video_id=video_id,
                status=ProcessingStatus.PROCESSING
            )
            
            start_time = time.time()
            
            # Get full input file path
            full_input_path = os.path.join(settings.STATIC_FILES_DIR, input_file_path)
            if not os.path.exists(full_input_path):
                raise FileNotFoundError(f"Input file not found: {full_input_path}")
            
            # Extract audio from video
            audio_path = os.path.join(temp_dir, "audio.wav")
            with VideoFileClip(full_input_path) as video:
                video.audio.write_audiofile(audio_path, logger=None)
            
            # Detect silence segments
            raw_silence_segments = await detect_silence_segments(
                audio_path,
                processing_settings
            )
            
            # Convert to seconds and create SilenceSegment objects
            silence_segments = []
            for start_ms, end_ms in raw_silence_segments:
                start_sec = start_ms / 1000.0
                end_sec = end_ms / 1000.0
                duration_sec = end_sec - start_sec
                
                # Add some padding if configured
                if processing_settings.padding_ms > 0:
                    padding_sec = processing_settings.padding_ms / 1000.0
                    start_sec = max(0, start_sec - padding_sec)
                    end_sec = end_sec + padding_sec
                
                silence_segments.append(
                    SilenceSegment(
                        start_time=start_sec,
                        end_time=end_sec,
                        duration=duration_sec
                    )
                )
            
            # Generate visualization
            visualization_path = os.path.join(temp_dir, "silence_visualization.png")
            await generate_silence_visualization(
                audio_path,
                raw_silence_segments,
                visualization_path
            )
            
            # Save visualization to storage
            visualization_storage_path = f"visualizations/{video_id}_silence.png"
            await save_file_to_storage(
                visualization_path,
                visualization_storage_path
            )
            
            # Process video based on preference
            output_path = os.path.join(temp_dir, "processed_video.mp4")
            
            with VideoFileClip(full_input_path) as video:
                if processing_settings.keep_silence_markers:
                    # Mark silence segments without removing
                    await mark_silence_segments(
                        video,
                        silence_segments,
                        output_path
                    )
                else:
                    # Remove silence segments
                    await remove_silence_segments(
                        video,
                        silence_segments,
                        output_path
                    )
            
            # Save processed video to storage
            processed_file_path = f"processed/{video_id}/processed_video.mp4"
            await save_file_to_storage(
                output_path,
                processed_file_path
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Update video status
            await update_video_status(
                video_id=video_id,
                status=ProcessingStatus.COMPLETED,
                processed_file_path=processed_file_path,
                processing_time_seconds=processing_time,
                silence_segments=[s.model_dump() for s in silence_segments]
            )
            
            return {
                "status": "success",
                "video_id": video_id,
                "silence_segments": [s.model_dump() for s in silence_segments],
                "processed_file_path": processed_file_path,
                "processing_time_seconds": processing_time,
                "visualization_path": visualization_storage_path
            }
            
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {str(e)}")
            # Update status to failed
            await update_video_status(
                video_id=video_id,
                status=ProcessingStatus.FAILED,
                error_message=str(e)
            )
            
            return {
                "status": "error",
                "video_id": video_id,
                "error": str(e)
            }

async def remove_silence_segments(
    video: VideoFileClip,
    silence_segments: List[SilenceSegment],
    output_path: str
) -> str:
    """
    Remove silence segments from a video and save the result
    """
    try:
        # Get total duration
        duration = video.duration
        
        # Create a list of segments to keep
        keep_segments = []
        current_time = 0
        
        for segment in silence_segments:
            # Add segment from current_time to start of silence
            if segment.start_time > current_time:
                keep_segments.append(video.subclip(current_time, segment.start_time))
            
            # Update current time to end of silence
            current_time = segment.end_time
        
        # Add final segment from last silence to end
        if current_time < duration:
            keep_segments.append(video.subclip(current_time, duration))
        
        # Concatenate all segments
        if keep_segments:
            final_video = concatenate_videoclips(keep_segments)
            final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
            final_video.close()
        else:
            # If no segments to keep, just copy the original
            video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        
        return output_path
    except Exception as e:
        logger.error(f"Error removing silence segments: {str(e)}")
        raise

async def mark_silence_segments(
    video: VideoFileClip,
    silence_segments: List[SilenceSegment],
    output_path: str
) -> str:
    """
    Mark silence segments in a video without removing them
    """
    try:
        # Create a temporary file for the intermediate result
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # First write the video to the temporary file
        video.write_videofile(temp_path, codec="libx264", audio_codec="aac")
        
        # Open the video with OpenCV for adding visual markers
        cap = cv2.VideoCapture(temp_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Process the video frame by frame
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Calculate current time in seconds
            current_time = frame_count / fps
            
            # Check if current frame is in a silence segment
            is_silence = False
            for segment in silence_segments:
                if segment.start_time <= current_time <= segment.end_time:
                    is_silence = True
                    break
            
            # If in silence, add a red border
            if is_silence:
                # Add "SILENCE" text
                cv2.putText(
                    frame,
                    "SILENCE",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA
                )
                
                # Add red border
                frame = cv2.rectangle(
                    frame,
                    (0, 0),
                    (width-1, height-1),
                    (0, 0, 255),
                    3
                )
            
            # Write the frame
            out.write(frame)
            frame_count += 1
            
            # Print progress every 1000 frames
            if frame_count % 1000 == 0:
                logger.info(f"Processed {frame_count}/{total_frames} frames ({frame_count/total_frames*100:.1f}%)")
        
        # Release video objects
        cap.release()
        out.release()
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        return output_path
    except Exception as e:
        logger.error(f"Error marking silence segments: {str(e)}")
        raise 