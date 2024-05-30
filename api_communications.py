import requests
import api_secrets
import time
import json

type FPATH           = str;
type SITE_RESPONSE   = requests.Response;
type URL             = str; 
type JSON            = dict[str, str];
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
    uploadResponse: SITE_RESPONSE   = requests.post(
        api_secrets.UPLOAD_URL,
        headers = api_secrets.HEADERS,
        data    = AUDReadfile(file_path)
    );

    # print(uploadResponse.json());
    return uploadResponse.json()["upload_url"];

# Transcribe ------------------------------------------------------------------------------------------
def AUDGetTransribeID(json_data: JSON) -> str:
    transcribeResponse: SITE_RESPONSE   = requests.post(
            api_secrets.TRANSCRIPT_URL,
            headers = api_secrets.HEADERS,
            json    = json_data
        );

    # print(transcribeResponse.json());
    return transcribeResponse.json()["id"];

# Poll -----------------------------------------------------------------------------------------------
def AUDGetPollJSON(transcript_id: str) -> any:
    poll_url: URL               = api_secrets.POLL_URL+transcript_id;
    pollResponse: SITE_RESPONSE = requests.get(poll_url, headers=api_secrets.HEADERS);
    return pollResponse.json();

def AUDGetTranscriptResult(json_data: JSON) -> TRSRESULT:
    transcript_id: str  = AUDGetTransribeID(json_data);

    print("Please have patience it may take a while", end = ' ', flush=True);
    while (1):
        data: any = AUDGetPollJSON(transcript_id);

        if ("completed" == data["status"]): print(); return data, None;
        elif ("error" == data["status"]): print(); return data, data["error"];

        print('.', end = '', flush = True);
        time.sleep(30);

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
                json.dump(sentiments, fobj, indent = 4);


        print("Location:", file_path);
        print("Transcription successfully saved.");

    elif (error): print("Error:", error);