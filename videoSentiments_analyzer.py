from json import load as JSON_LOAD
from api_communications import FPATH, SITE_RESPONSE, REQ_GET, SENT, IApiTranscriptManager
import yt_extractor as ytext
from abc import ABC, abstractmethod

class IVideoSentimentAnalyzer(ABC):
    @abstractmethod
    def saveSentiments(toPath: FPATH) -> FPATH: pass

    @abstractmethod
    def analyzeSentiments(fromFile: FPATH) -> None: pass

class YTVideoSentimentAnalyzer(IVideoSentimentAnalyzer):
    def __init__(self, videoInfo: ytext.VID_INFO, apiTranscriptManager: IApiTranscriptManager) -> None:
        self.__videoInfo = videoInfo
        self.__apiTranscriptManager = apiTranscriptManager

    def saveSentiments(self, toPath: FPATH) -> FPATH:       

        infoExtractor = ytext.YTInfoExtractor(self.__videoInfo)

        title = infoExtractor.getTitle()
        thumbReq: SITE_RESPONSE     = REQ_GET(url = infoExtractor.getThumbnailURL());

        with open(toPath+"thumbnail.jpg", "wb") as fobj: fobj.write(thumbReq.content);

        self.__apiTranscriptManager.saveTranscript(title, toPath);
        return toPath + title + "_ytVideoSentiments.json";


    def analyzeSentiments(fromFile: str) -> None:
        print("Analyzing Sentiments !\n");
        with open(fromFile, "r") as fobj:
            data    = JSON_LOAD(fobj);

        sentiments: SENT    = {
            "NEGATIVE"  : [],
            "NEUTRAL"   : [],
            "POSITIVE"  : [],
        };

        for res in data:
            text: str   = res["text"];
            sentiments[res["sentiment"]].append(text);

        tot_neg: int    = len(sentiments["NEGATIVE"]);
        tot_neu: int    = len(sentiments["NEUTRAL"]);
        tot_pos: int    = len(sentiments["POSITIVE"]);

        print("Positive sentiments  :", tot_pos);
        print("Negative sentiments  :", tot_neg);
        print("Neutral sentiments   :", tot_neu);

        try:
            pos_ratio: float  = tot_pos / (tot_pos + tot_neg);
        except ZeroDivisionError:
            pos_ratio: float    = 0;
        print(f"Positive ratio       : {pos_ratio:.3f}");
