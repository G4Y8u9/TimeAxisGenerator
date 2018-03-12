from moviepy.editor import VideoFileClip
from PIL import Image
from math import floor


def getTime(sec):
    ms = (sec - floor(sec)) * 1000
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return '%02d:%02d:%02d,%03d' % (h, m, s, ms)


def split_image(img, part_size=(64, 64)):
    w, h = img.size
    pw, ph = part_size
    return [img.crop((i, j, i + pw, j + ph)).copy() for i in range(0, w, pw) for j in range(0, h, ph)]


def hist_similar(lh, rh):
    assert len(lh) == len(rh)
    return sum(1 - (0 if q == r else float(abs(q - r)) / max(q, r)) for q, r in zip(lh, rh)) / len(lh)


def calc_similar(li, ri):
    return sum(hist_similar(l.histogram(), r.histogram()) for l, r in zip(split_image(li), split_image(ri))) / 16.0


def getTimeAxis(video_file_path, video_frame, srt_file_path, x, y, w, h):
    """
    x, y, w, h means the cut position of the video
    :return: output a srt subtitle file which contains time axis set
    """
    myclip = VideoFileClip(video_file_path)
    dt = 1. / video_frame
    frames = int(myclip.duration / dt)
    keyFrames = list([])
    keyFrames.append(0)

    im1 = Image.fromarray(myclip.get_frame(0)).crop((x, y, x+w, y+h))
    for i in range(frames):
        im2 = Image.fromarray(myclip.get_frame(i/24.)).crop((x, y, x+w, y+h))
        print("\nimg: %d\timg: %d" % (i-1, i), end='\t')
        ratio = calc_similar(im2, im1)
        print(ratio)
        if ratio/2.4375 < 0.7:  # idk why sometimes the ratio > 1 so i adjust it with a factor of some number
            keyFrames.append(i)
            # print("ratio: ", ratio, " < 0.7, add key frame!-------------------")
        # else:
            # print("ratio: ", ratio, " > 0.7, they are the same words!")
        im1 = im2

    print(keyFrames)

    with open(srt_file_path, 'w') as f:
        for i in range(len(keyFrames) - 1):
            f.writelines(('%d' % i, '\n', getTime(keyFrames[i]/24), ' --> ', getTime(keyFrames[i + 1]/24), '\n\n'))


"""
used for test
"""
video_file_path = 'test03.mp4'
video_frame = 30
srt_file_path = 'test03.srt'
x = 560
y = 900
w = 800
h = 140
getTimeAxis(video_file_path, video_frame, srt_file_path, x, y, w, h)
