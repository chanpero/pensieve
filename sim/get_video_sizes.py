import os

TOTAL_VIDEO_CHUNCK = 49
BITRATE_LEVELS = 6
VIDEO_PATH = '../video_server/'
VIDEO_FOLDER = 'video'

# assume videos are in ../video_servers/video[1, 2, 3, 4, 5, 6]
# the quality at video6 is the lowest and video1 is the highest

# store size of each chunk in file video_size_# (#=0 smallest, #=5 largest)
for bitrate in range(BITRATE_LEVELS):
    with open('video_size_' + str(bitrate), 'wb') as f:
        for chunk_num in range(1, TOTAL_VIDEO_CHUNCK + 1):
            video_chunk_path = VIDEO_PATH + \
                               VIDEO_FOLDER + \
                               str(BITRATE_LEVELS - bitrate) + \
                               '/' + \
                               str(chunk_num) + \
                               '.m4s'
            chunk_size = os.path.getsize(video_chunk_path)
            f.write((str(chunk_size) + '\n').encode())
