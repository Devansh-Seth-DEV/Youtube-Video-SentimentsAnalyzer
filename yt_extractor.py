from yt_dlp import YoutubeDL

type YTDL       = YoutubeDL;
type VID_INFO   = (any | dict[str, any] | None);
type URL        = str;
type FPATH      = str;

def YDLGetVideoInfo(ydl: YTDL, vidURL: URL) -> VID_INFO:
    with ydl:
        result: VID_INFO  = ydl.extract_info(
            url      = vidURL,
            download = True,
        );

    if ("entries" in result): return result["entries"][0];

    print("[thumbnail]:", result["thumbnails"][-2]["url"]);
    print("[duration]:", result["duration"], 's');
    print("[audio channels]:", result["audio_channels"]);

    return result;

def YDLGetAudioURL(video_info: VID_INFO) -> URL:
    for fmt in video_info["formats"]:
        if ("m4a" == fmt["ext"]): return fmt["url"];

YDLGetVideoThumbnailURL = lambda video_info : video_info["thumbnails"][-2]["url"];
YDLGetVideoDuration     = lambda video_info : video_info["duration"];
YDLGetAudioChannels     = lambda video_info : video_info["audio_channels"];
YDLGetTitle             = lambda video_info : video_info["title"];