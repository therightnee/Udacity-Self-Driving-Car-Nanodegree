from moviepy.editor import ImageSequenceClip

mod_clip = ImageSequenceClip("./Bounded_Images", fps=10)
mod_clip.write_videofile("mod_test_video.mp4")