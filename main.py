from json import load as JSON_LOAD
from api_communications import *
from api_communications import FPATH
import yt_extractor as ytext
import os


class IVideoSentimentAnalyzer(ABC):
    @abstractmethod
    def saveSentiments(toPath: FPATH) -> FPATH: pass

    @abstractmethod
    def analyzeSentiments(fromFile: FPATH) -> None: pass

class YTVideoSentimentAnalyzer(IVideoSentimentAnalyzer):
    def __init__(self, videoURL: ytext.URL, videoExtractor: ytext.IYTVideoExtractor, apiTranscriptManager: IApiTranscriptManager) -> None:
        self.__videoURL = videoURL
        self.__videoExtractor = videoExtractor
        self.__apiTranscriptManager = apiTranscriptManager

    def saveSentiments(self, toPath: FPATH) -> FPATH:
        videoInfo = self.__videoExtractor.getVideoInfo(self.__videoURL)
        
        audioURL = ytext.YTAudioExtractor(videoInfo).getAudioURL()
        infoExtractor = ytext.YTInfoExtractor(videoInfo)

        title = infoExtractor.getTitle()
        thumbReq: SITE_RESPONSE     = REQ_GET(url = infoExtractor.getThumbnailURL());

        with open(toPath+"thumbnail.jpg", "wb") as fobj: fobj.write(thumbReq.content);

        self.__apiTranscriptManager.saveTranscript(title, toPath);
        return toPath + title + "_sentiments.json";


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

            

# json_data: JSON             = {
#     "audio_url": audioURL,
#     "sentiment_analysis": True
#     };

def AnalyzeSentiments(file_path: FPATH) -> None:
    print("Analyzing Sentiments !\n");
    with open(file_path, "r") as fobj:
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


def main() -> None:
    DATA_DIR: FPATH             = "./data/";
    ydl_opts: dict[str, any]    = {
        "outtmpl": DATA_DIR+"audio",
        "format": "bestaudio/wav",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "141",
            },
        ],
    };

    ydl: ytext.YTDL             = ytext.YoutubeDL(ydl_opts);
    video_url: ytext.URL        = input("Enter video url: ");
    json_file: FPATH            = YTVIDSaveSentiments(ydl, video_url, DATA_DIR);

    SLEEP_FOR_SEC(1);
    print('\033c', end = '', flush=True);
    AnalyzeSentiments(json_file);

def DelData() -> None:
    for filename in os.listdir("./data/"):
        if os.path.isfile(os.path.join("./data/", filename)):
            os.remove(os.path.join("./data/", filename));

if ("__main__" == __name__):
    try:
        main();
    except KeyboardInterrupt:
        pass
    finally:
        print("\nexiting application !");
        exit();
        # DelData();