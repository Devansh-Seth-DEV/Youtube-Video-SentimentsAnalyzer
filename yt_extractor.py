from yt_dlp import YoutubeDL
from abc import ABC, abstractmethod
from typing import TypeAlias

YTDL       :TypeAlias = YoutubeDL;
VID_INFO   :TypeAlias = '(any | dict[str, any] | None)';
URL        :TypeAlias = str;
FPATH      :TypeAlias = str;

class IYTVideoExtractor(ABC):
    @abstractmethod
    def getVideoInfo(self, videoURL: URL) -> VID_INFO: pass

    @abstractmethod
    def getVideoDuration(self, videoInfo: VID_INFO): pass


class IYTAudioExtractor(ABC):
    @abstractmethod
    def getAudioURL(self) -> URL: pass

    @abstractmethod
    def getAudioChannels(self): pass

class IYTInfoExtractor(ABC):
    @abstractmethod
    def getTitle(self): pass

    @abstractmethod
    def getThumbnailURL(self): pass


class YTVideoExtractor(IYTVideoExtractor):
    def __init__(self, ydl: YTDL) -> None:
        self.__ydl = ydl

    def getVideoInfo(self, videoURL: URL) -> VID_INFO:
        with self.__ydl:
            videoInfo: VID_INFO  = self.__ydl.extract_info(
                url      = videoURL,
                download = True,
            );

        if ("entries" in videoInfo): return videoInfo["entries"][0];

        # print("[thumbnail]:", result["thumbnails"][-2]["url"]);
        # print("[duration]:", result["duration"], 's');
        # print("[audio channels]:", result["audio_channels"]);

        return videoInfo;

    def getVideoDuration(self, videoInfo: VID_INFO): return videoInfo["duration"]


class YTAudioExtractor(IYTAudioExtractor):
    def __init__(self, videoInfo: VID_INFO) -> None:
        self.__videoInfo = videoInfo

    def getAudioURL(self) -> URL:
        for fmt in self.__videoInfo["formats"]:
            if ("m4a" == fmt["ext"]): return fmt["url"];

        return ""

    def getAudioChannels(self): return self.__videoInfo["audio_channels"]


class YTInfoExtractor(IYTInfoExtractor):
    def __init__(self, videoInfo: VID_INFO) -> None:
        self.__videoInfo = videoInfo

    def getTitle(self): return self.__videoInfo["title"]

    def getThumbnailURL(self): return self.__videoInfo["thumbnails"][-2]["url"]
