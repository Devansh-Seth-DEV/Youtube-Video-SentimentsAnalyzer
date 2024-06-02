from requests import Response as REQ_RESPONSE
from requests import get as REQ_GET
from requests import post as REQ_POST
from time import sleep as SLEEP_FOR_SEC
from json import dump as JSON_DUMP
import api_secrets

type FPATH           = str;
type SITE_RESPONSE   = REQ_RESPONSE;
type URL             = str; 
type JSON            = dict[str, str];
type SENT            = dict[str, list[str]]
type TRSRESULT       = tuple[any, None | str]

# Read audio file -------------------------------------------------------------------------------------
def AUDReadfile(file_path: FPATH, chunkSize: int = 5242880):
    with open(file_path, "rb") as fobj:
        while (1):
            data: bytes = fobj.read(chunkSize);
            if (not data): break;
            yield data;

# Upload ----------------------------------------------------------------------------------------------
def AUDGetUploadURL(file_path: FPATH) -> URL:
    uploadResponse: SITE_RESPONSE   = REQ_POST(
        url     = api_secrets.UPLOAD_URL,
        headers = api_secrets.HEADERS,
        data    = AUDReadfile(file_path)
    );

    # print(uploadResponse.json());
    return uploadResponse.json()["upload_url"];

# Transcribe ------------------------------------------------------------------------------------------
def AUDGetTransribeID(json_data: JSON) -> str:
    transcribeIDResponse: SITE_RESPONSE   = REQ_POST(
            url     = api_secrets.TRANSCRIPT_URL,
            headers = api_secrets.HEADERS,
            json    = json_data
        );

    # print(transcribeResponse.json());
    return transcribeIDResponse.json()["id"];

# Poll -----------------------------------------------------------------------------------------------
def AUDGetPollJSON(transcript_id: str) -> any:
    poll_url: URL               = api_secrets.POLL_URL+transcript_id;
    pollResponse: SITE_RESPONSE = REQ_GET(
        url     = poll_url,
        headers = api_secrets.HEADERS
    );

    return pollResponse.json();

def AUDGetTranscriptResult(json_data: JSON) -> TRSRESULT:
    transcript_id: str  = AUDGetTransribeID(json_data);

    print("Please have patience it may take a while", end = ' ', flush=True);
    while (1):
        data: any = AUDGetPollJSON(transcript_id);

        if ("completed" == data["status"]): print(); return data, None;
        elif ("error" == data["status"]): print(); return data, data["error"];
        else:
            print('.', end = '', flush = True);
            SLEEP_FOR_SEC(30);

# Save Transcript --------------------------------------------------------------------------------------
def AUDSaveTranscript(file_path: FPATH, json_data: JSON) -> None:
    print("Creating transcript ...")
    data, error = AUDGetTranscriptResult(json_data);

    if (data):
        filename: FPATH   = file_path + ".txt";
        with open(filename, 'w') as fobj:
            if (None != data["text"]):
                fobj.write(data["text"]);

        if ("sentiment_analysis" in json_data.keys()):
            filename: FPATH    = file_path + "_sentiments.json";
            with open(filename, 'w') as fobj:
                sentiments  = data["sentiment_analysis_results"];
                JSON_DUMP(sentiments, fobj, indent = 4);


        print("Location:", file_path);
        print("Transcription successfully saved.");

    elif (error): print("Error:", error);