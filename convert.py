from moviepy.editor import VideoFileClip
import tg_send
import cv2


def avi_to_mp4_and_send(input_file, fps, output_file, caption):
    try:
        video = VideoFileClip(input_file)
        video.write_videofile(output_file, codec='libx264', fps=fps)  # Adjust codec and fps as needed
        video.close()
        print(f"Conversion completed: {output_file}")
        tg_send.send_video_tg(output_file, caption)
    except Exception as e:
        print(f"Error during conversion: {e}")


def save_photo_and_send(frame, file_name, caption):
    cv2.imwrite(file_name, frame)
    tg_send.send_photo_tg(file_name, caption)

