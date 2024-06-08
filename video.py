import asyncio
import random
import string
import subprocess
import json

class FFmpegBuilder:
    def __init__(self):
        self._inputs: list[str] = []

        self._vcodec = "libx264" # support libx264/libx265
        self._vmode = "crf" # crf/cbr
        self._crf = 23
        self._cbr = 0 
        self._vbv_maxrate = 0 
        self._vbv_bufsize = 0
        self._vfilter = ""
        self._pix_fmt = "yuv420p"
        
        self._acodec = "aac"
        self._omit_abr = False
        self._abr = 128000
        self._afilter = ""

        self._maxsize = 0 
        self._preparams = []
        self._postparams = []

        self._output = "".join(random.choices(string.ascii_letters + string.digits, k=12)) + ".mp4" # default to 12 random alphanumeric digits

    def __str__(self):
        return str(self.build())

    def __repr__(self):
        return str(self.__dict__) + "\n" + str(self)

    def build(self):
        command = ["ffmpeg", "-y"]

        for param in self._preparams:
            command.append(f"-{param}")

        for input in self._inputs:
            command.extend(["-i", input])

        if (self._vfilter != ""):
            command.extend(["-vf", f"{self._vfilter},format={self._pix_fmt}"])
        else:
            command.extend(["-vf", f"format={self._pix_fmt}"])

        if (self._afilter != ""):
            command.extend(["-af", self._afilter])

        command.extend(["-c:v", self._vcodec])
        if (self._vcodec != "copy" and self._vcodec != "vn"):
            if (self._vmode == "crf"):
                command.extend(["-crf", str(self._crf)])
            elif (self._vmode == "cbr"):
                command.extend(["-b:v", str(self._cbr)])

            if (self._vbv_maxrate != 0 and self._vbv_bufsize != 0):
                command.extend(["-maxrate", str(self._vbv_maxrate), "-bufsize", str(self._vbv_bufsize)])
        
        if (self._acodec == "copy"):
            command.extend(["-c:a", "copy"])
        elif (self._abr == 0):
            command.extend(["-c:a", "an"])
        else:
            command.extend(["-c:a", self._acodec])
            if (not self._omit_abr and self._acodec != "an"):
                command.extend(["-b:a", str(self._abr)])

        if (self._maxsize != 0):
            command.extend(["-fs", str(self._maxsize)])

        for param in self._postparams:
            command.append("-{param}")

        command.append(self._output)

        return command

    def run(self):
        return subprocess.run(self.build())

    async def run_async(self):
        proc = await asyncio.create_subprocess_exec(*self.build())
        return proc

    def input(self, *inputs: str):
        self._inputs.extend(inputs)
        return self

    def vcodec(self, codec: str):
        self._vcodec = codec
        return self

    def vcopy(self):
        self._vcodec = "copy"
        return self

    def novideo(self):
        self._vcodec = "vn"
        return self

    def crf(self, crf: int):
        self._vmode = "crf"
        self._crf = crf
        return self

    def cbr(self, bitrate: int):
        self._vmode = "cbr"
        self._cbr = bitrate
        return self

    def vbv(self, maxrate: int, bufsize: int = 0):
        if (bufsize == 0):
            bufsize = 2 * maxrate
        self._vbv_maxrate = maxrate
        self._vbv_bufsize = bufsize
        return self

    def vfilter(self, filter: str):
        self._vfilter = filter
        return self

    def pix_fmt(self, pix_fmt: str):
        self._pix_fmt = pix_fmt
        return self

    def acodec(self, codec: str, omit_bitrate: bool = False):
        self._acodec = codec
        self._omit_abr = omit_bitrate
        return self

    def acopy(self):
        self._acodec = "copy"
        return self

    def noaudio(self):
        self._acodec = "an"
        return self

    def abr(self, bitrate: int):
        self._abr = bitrate
        return self

    def afilter(self, filter: str):
        self._afilter = filter
        return self

    def maxsize(self, size: int):
        self._maxsize = size
        return self

    def preparams(self, *params: str):
        self._preparams.extend(params)
        return self

    def postparams(self, *params: str):
        self._postparams.extend(params)
        return self

    def output(self, output: str):
        self._output = output
        return self

async def ffprobe(file: str):
    proc = await asyncio.create_subprocess_exec(*["ffprobe", file, "-v", "-8", "-show_entries", "format:stream", "-of", "json"], stdout=subprocess.PIPE)
    out, err = await proc.communicate()
    return json.loads(out)

