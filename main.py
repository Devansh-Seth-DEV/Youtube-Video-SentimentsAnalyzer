from json import load as JSON_LOAD
from requests import get as REQ_GET
from api_communications import FPATH, JSON, SENT, SITE_RESPONSE, AUDSaveTranscript
from time import sleep as SLEEP_FOR_SEC
import yt_extractor as ytext
import os

def YTVIDSaveSentiments(ydl: ytext.YTDL, url: ytext.URL, data_dir: FPATH) -> FPATH:
    video_info: ytext.VID_INFO  = ytext.YDLGetVideoInfo(ydl, url);
    audio_url: ytext.URL        = ytext.YDLGetAudioURL(video_info);
    
    title: FPATH                = data_dir+"video";
    thumbReq: SITE_RESPONSE     = REQ_GET(url = ytext.YDLGetVideoThumbnailURL(video_info));

    with open(data_dir+"thumbnail.jpg", "wb") as fobj: fobj.write(thumbReq.content);

    json_data: JSON             = {
        "audio_url": audio_url,
        "sentiment_analysis": True
        };

    AUDSaveTranscript(title, json_data);
    return title + "_sentiments.json";

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