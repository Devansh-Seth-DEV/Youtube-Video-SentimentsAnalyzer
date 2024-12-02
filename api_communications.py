from requests import Response as REQ_RESPONSE
from requests import get as REQ_GET
from requests import post as REQ_POST
from time import sleep as SLEEP_FOR_SEC
from json import dump as JSON_DUMP
from abc import ABC, abstractmethod

# TypeAlias -----------------------------------------------------------
type APICONFIG_TYPE = dict[str, dict[str, dict[str, str | None] | str | None]]

# Constants ------------------------------------------------------------
type FPATH           = str;
type SITE_RESPONSE   = REQ_RESPONSE;
type URL             = str; 
type JSON            = dict[str, str];
type SENT            = dict[str, list[str]]
type TRSRESULT       = tuple[any, None | str]

# Config Profile Functions --------------------------------------------
def assemblyAIConfigProfile() -> APICONFIG_TYPE:
    key = "2396e3cdd1b345549d7a9fdb0f27c9e8"
    transcriptURL = "https://api.assemblyai.com/v2/transcript"
    
    return {
        "key": key,
        "headers": {
            "authorization": key
        },
        "uploadURL": "https://api.assemblyai.com/v2/upload",
        "transcriptURL": transcriptURL,
        "pollURL": transcriptURL + "/"
    }


# API Config Profiles ------------------------------------------------
apiConfigProfiles: APICONFIG_TYPE = {
    "assemblyAI": assemblyAIConfigProfile()
}

class IFileManager(ABC):
    @abstractmethod
    @property
    def file(self) -> FPATH: pass

class IJsonManager(ABC):
    @abstractmethod
    @property
    def jsonData(self) -> JSON: pass

class IAudioManager(IFileManager):
    @abstractmethod
    @property
    def chunkSize(self) -> int: pass

    @abstractmethod
    def readAudio(self): pass

class ISpeech2TextApiManager(IJsonManager):
    @abstractmethod
    def getURL(self, audioReader: IAudioManager) -> URL: pass

    @abstractmethod
    def getTranscribeID(self) -> str: pass

    @abstractmethod
    def pollJson(self) -> any: pass

class IApiTranscriptManager(ABC):
    @abstractmethod
    def getTranscript(self) -> TRSRESULT: pass

    @abstractmethod
    def saveTranscript(self, asFileName: str, toPath: FPATH) -> None: pass


class AudioReader(IAudioManager):
    def __init__(self, file: FPATH, size: int = 5242880) -> None:
        self._file = file
        self._chunkSize = size
    
    @property
    def file(self) -> FPATH:
        return self._file

    @property
    def chunkSize(self) -> int:
        return self._chunkSize

    def readAudio(self):
        with open(self._file, "rb") as audFile:
            while(1):
                data: bytes = audFile.read(self._chunkSize)
                if not data: break
                yield data


class AssemblyAISpeech2TextApi(ISpeech2TextApiManager):
    def __init__(self, jsonData: JSON) -> None:
        self.__apiConfig = apiConfigProfiles["assemblyAI"]
        self.__jsonData = jsonData

    @property
    def jsonData(self) -> JSON:
        return self.__jsonData

    def getURL(self, audioReader: IAudioManager) -> URL:
        uploadResponse: SITE_RESPONSE   = REQ_POST(
            url     = self.__apiConfig["uploadURL"],
            headers = self.__apiConfig["headers"],
            data    = audioReader.readAudio(audioReader.file)
        );

        # print(uploadResponse.json());
        return uploadResponse.json()["upload_url"];

    def getTranscribeID(self) -> str:
        transcribeIDResponse: SITE_RESPONSE   = REQ_POST(
                url     = self.__apiConfig["uploadURL"],
                headers = self.__apiConfig["headers"],
                json    = self.__jsonData
            );

        # print(transcribeResponse.json());
        return transcribeIDResponse.json()["id"];

    def pollJson(self) -> any:
        pollURL: URL                = POLL_URL + self.getTranscribeID();
        pollResponse: SITE_RESPONSE = REQ_GET(
            url     = self.__apiConfig["pollURL"],
            headers = self.__apiConfig["headers"]
        );

        return pollResponse.json();
    
class AssemblyAIApiTranscriptManager(IApiTranscriptManager):
    def __init__(self, speech2TextApi: ISpeech2TextApiManager) -> None:
        self.__asmSpeech2TextApi = speech2TextApi

    def getTranscript(self) -> TRSRESULT:
        transcript_id: str  = self.__asmSpeech2TextApi.getTranscribeID(self.__speech2TextApi.jsonData);

        print("Please have patience it may take a while", end = ' ', flush=True);
        while (1):
            data: any = self.__asmSpeech2TextApi.pollJson(transcript_id);

            if ("completed" == data["status"]): print(); return data, None;
            elif ("error" == data["status"]): print(); return data, data["error"];
            else:
                print('.', end = '', flush = True);
                SLEEP_FOR_SEC(30);


    def saveTranscript(self, asFileName: str, toPath: FPATH) -> None:
        print("Creating transcript ...")
        data, error = self.getTranscript();

        if (data):
            filename: FPATH   = toPath + asFileName + ".txt";
            with open(filename, 'w') as fobj:
                if (None != data["text"]):
                    fobj.write(data["text"]);

            if ("sentiment_analysis" in self.__apiReciever.jsonData.keys()):
                filename: FPATH    = toPath + asFileName + "_sentiments.json";
                with open(filename, 'w') as fobj:
                    sentiments  = data["sentiment_analysis_results"];
                    JSON_DUMP(sentiments, fobj, indent = 4);


            print("Location:", toPath + asFileName);
            print("Transcription successfully saved.");

        elif (error): print("Error:", error);
