import videoSentiments_analyzer as VSA
import yt_extractor as ytext
import api_communications as APICOM 
from api_communications import FPATH, SLEEP_FOR_SEC, JSON
import os


def main() -> None:
    DATA_DIR: FPATH             = "./data/";

    # Youtube initializations
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
    ytVideoExtractor            = ytext.YTVideoExtractor(ydl)
    videoInfo                   = ytVideoExtractor.getVideoInfo(video_url)
    audioURL                    = ytext.YTAudioExtractor(videoInfo).getAudioURL()

    # Api initialisations
    jsonData: JSON             = {
        "audio_url": audioURL,
        "sentiment_analysis": True
    };

    speech2textApi              = APICOM.AssemblyAISpeech2TextApi(jsonData)
    # Sentiments Analyses
    sentimentsAnalyzer          = VSA.YTVideoSentimentAnalyzer(videoInfo, speech2textApi)
    sentimentsFile: FPATH       = sentimentsAnalyzer.write(DATA_DIR);
    sentimentsAnalyzer.fetch(sentimentsFile)

    SLEEP_FOR_SEC(1);
    print('\033c', end = '', flush=True);
    
    sentimentsAnalyzer.print()

def DelData() -> None:
    for filename in os.listdir("./data/"):
        if os.path.isfile(os.path.join("./data/", filename)):
            os.remove(os.path.join("./data/", filename));

if ("__main__" == __name__):
    try: main()
    except KeyboardInterrupt: pass
    finally:
        print("\nexiting application !")
        exit()
        # DelData();
