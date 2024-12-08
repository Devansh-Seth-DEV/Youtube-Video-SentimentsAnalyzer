from requests import Response as REQ_RESPONSE
from requests import get as REQ_GET
from requests import post as REQ_POST
from requests.exceptions import JSONDecodeError, RequestException
from time import sleep as SLEEP_FOR_SEC
from json import dump as JSON_DUMP
from abc import ABC, abstractmethod
from typing import TypeAlias

# TypeAlias -----------------------------------------------------------
APICONFIG: TypeAlias = 'dict[str, dict[str, dict[str, str | None] | str | None]]';

# Constants ------------------------------------------------------------
FPATH: TypeAlias            = str;
SITE_RESPONSE: TypeAlias    = REQ_RESPONSE;
URL: TypeAlias              = str; 
JSON: TypeAlias             = dict[str, str];
TRSRESULT: TypeAlias        = tuple[any, None | str];


class IFileManager(ABC):
    @property
    @abstractmethod
    def file(self) -> FPATH: pass

class IJsonManager(ABC):
    @property
    @abstractmethod
    def jsonData(self) -> JSON: pass

class IAudioManager(IFileManager):
    @property
    @abstractmethod
    def chunkSize(self) -> int: pass

    @abstractmethod
    def readAudio(self): pass

class ISpeech2TextApiManager(IJsonManager):
    @property
    @abstractmethod
    def api(self): pass

    @abstractmethod
    def getURL(self, audioReader: IAudioManager) -> URL: pass

    @abstractmethod
    def getTranscribeID(self) -> str: pass

    @abstractmethod
    def pollJson(self) -> any: pass


class IApiTranscriptManager(ABC):
    @property
    @abstractmethod
    def transcripter(self): pass

    @abstractmethod
    def getTranscript(self) -> TRSRESULT: pass

    @abstractmethod
    def saveTranscript(self, asFileName: str, toPath: FPATH) -> None: pass

class ISpeech2TextApi(ISpeech2TextApiManager, IApiTranscriptManager): pass



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
    _siteURL = "https://api.assemblyai.com/v2"
    _config: APICONFIG = {
        "uploadURL": f"{_siteURL}/upload",
        "transcriptURL": f"{_siteURL}/transcript",
        "pollURL": f"{_siteURL}/transcript/"
    }
    
    def __init__(self, key: str, jsonData: JSON) -> None:
        self.__jsonData = jsonData
        self.__headers = {
            "authorization": key
        }

    @property
    def jsonData(self) -> JSON:
        return self.__jsonData

    @property
    def api(self): return self

    def getURL(self, audioReader: IAudioManager) -> URL:
        try:
            uploadResponse: SITE_RESPONSE   = REQ_POST(
                url     = self._config["uploadURL"],
                headers = self.__headers,
                data    = audioReader.readAudio(audioReader.file)
            );


            uploadResponse.raise_for_status()

            return uploadResponse.json()["upload_url"];

        except JSONDecodeError as e:
            print(f"JSONDecodeError: {3}")
            print("Response content:", uploadResponse.text)

        except RequestException as e:
            print(f"Request failed: {e}")

    def getTranscribeID(self) -> str:
        try:
            transcribeIDResponse: SITE_RESPONSE   = REQ_POST(
                    url     = self._config["transcriptURL"],
                    headers = self.__headers,
                    json    = self.__jsonData
                    );

            transcribeIDResponse.raise_for_status()

            #print("ID:",transcribeIDResponse.json()["id"])
            return transcribeIDResponse.json()["id"];

        except JSONDecodeError as e:
            print(f"JSONDecodeError: {3}")
            print("Response content:", transcribeIDResponse.text)

        except RequestException as e:
            print(f"Request failed: {e}")

    def pollJson(self) -> any:
        #pollURL: URL                = f"{self._config["pollURL"]}{self.getTranscribeID()}"
        pollResponse: SITE_RESPONSE = REQ_GET(
            url     = f"{self._config['pollURL']}{self.getTranscribeID()}",
            headers = self.__headers
        );

        return pollResponse.json();

    
class AssemblyAIApiTranscriptManager(IApiTranscriptManager):
    def __init__(self, speech2TextApi: AssemblyAISpeech2TextApi) -> None:
        self._api = speech2TextApi

    @property
    def transcripter(self): return self

    def getTranscript(self) -> TRSRESULT:
        transcript_id: str  = self._api.getTranscribeID();

        print("Please have patience it may take a while\n", flush=True);
        print("Processing", end = ' ', flush = True)

        while (1):
            data: any = self._api.pollJson();
            #print(data)

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

            if ("sentiment_analysis" in self._api.jsonData.keys()):
                filename: FPATH    = toPath + asFileName + "_sentiments.json";
                with open(filename, 'w') as fobj:
                    sentiments  = data["sentiment_analysis_results"];
                    JSON_DUMP(sentiments, fobj, indent = 4);


            print("Location:", toPath + asFileName);
            print("Transcription successfully saved.");

        elif (error): print("Error:", error);

class AssemblyAIApi(ISpeech2TextApi, AssemblyAISpeech2TextApi, AssemblyAIApiTranscriptManager):
    def __init__(self, key: str, jsonData: JSON) -> None:
        AssemblyAISpeech2TextApi.__init__(self, key, jsonData)
        AssemblyAIApiTranscriptManager.__init__(self, self.api)
