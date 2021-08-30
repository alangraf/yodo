import ssl
from pytube import YouTube
ssl._create_default_https_context = ssl._create_unverified_context


class Video:
    def __init__(self, url):
        self.url = url
        self.youtube = YouTube(url)

    def title(self):
        return self.youtube.title

    def videolength(self):
        yt = self.youtube.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        # video_size = float(self.youtube.streams.first().filesize/1000000)
        video_size = float(yt.filesize/1000000)
        video_size = round(video_size, 2)

        return str(video_size)

    def duration(self):
        seconds = self.youtube.length % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        return "%02d:%02d:%02d" % (hour, minutes, seconds)

    def download(self, extension, location):
        if extension == 'mp3':
            file = self.youtube.streams.filter(only_audio=True)
            file[0].download(location)
        elif extension == 'mp4':
            file = self.youtube.streams.get_highest_resolution()
            file.download(location)
        else:
            pass