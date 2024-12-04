from json import load as JSON_LOAD
from api_communications import FPATH, SITE_RESPONSE, REQ_GET, ISpeech2TextApi
import yt_extractor as ytext
from abc import ABC, abstractmethod

type SENTIMENTS_TYPE = dict[str, list[str | None]]

class IVideoSentimentWriter(ABC):
    @abstractmethod
    def write(self, toPath: FPATH) -> FPATH: pass

class IVideoSemtimentsFetcher(ABC):
    @abstractmethod
    def fetch(self, fromFile: FPATH) -> None: pass

    @abstractmethod
    def print(self) -> None: pass


class IVideoSentimentAnalyzer(IVideoSentimentWriter, IVideoSemtimentsFetcher): pass

class YTVideoSentimentWriter(IVideoSentimentWriter):
    def __init__(self, videoInfo: ytext.VID_INFO, speech2TextApi: ISpeech2TextApi) -> None:
        self.__videoInfo = videoInfo
        self.__speech2TextApi = speech2TextApi

    def write(self, toPath: FPATH) -> FPATH:       

        infoExtractor = ytext.YTInfoExtractor(self.__videoInfo)

        title = infoExtractor.getTitle()
        thumbReq: SITE_RESPONSE     = REQ_GET(url = infoExtractor.getThumbnailURL());

        with open(toPath+"thumbnail.jpg", "wb") as fobj: fobj.write(thumbReq.content);

        self.__speech2TextApi.saveTranscript(title, toPath);
        return toPath + title + "_ytVideoSentiments.json";

class YTVideoSentimentsFetcher(IVideoSemtimentsFetcher):
    def __init__(self) -> None:
        self.__sentiments: SENTIMENTS_TYPE = {
            "NEGATIVE"  : [],
            "NEUTRAL"   : [],
            "POSITIVE"  : [],
        };

    def fetch(self, fromFile: str) -> None:
        print("Analyzing Sentiments !\n");
        with open(fromFile, "r") as fobj:
            data    = JSON_LOAD(fobj);

        for res in data:
            text: str   = res["text"];
            self.__sentiments[res["sentiment"]].append(text);
    

    def print(self) -> None:
        tot_neg: int    = len(self.__sentiments["NEGATIVE"]);
        tot_neu: int    = len(self.__sentiments["NEUTRAL"]);
        tot_pos: int    = len(self.__sentiments["POSITIVE"]);

        print("Positive sentiments  :", tot_pos);
        print("Negative sentiments  :", tot_neg);
        print("Neutral sentiments   :", tot_neu);

        try:
            pos_ratio: float  = tot_pos / (tot_pos + tot_neg);
        except ZeroDivisionError:
            pos_ratio: float    = 0;
        print(f"Positive ratio       : {pos_ratio:.3f}");

class YTVideoSentimentAnalyzer(IVideoSentimentAnalyzer, YTVideoSentimentWriter, YTVideoSentimentsFetcher):
    def __init__(self, videoInfo: ytext.VID_INFO, speech2TextApi: ISpeech2TextApi) -> None:
        super().__init__(videoInfo, speech2TextApi)

    def write(self, toPath: FPATH) -> FPATH:
        return super().write(toPath)

    def fetch(self, fromFile: FPATH) -> None:
        return super().fetch(fromFile)
    
    def print(self) -> None:
        return super().print()
