from io import BytesIO
from typing import BinaryIO
from pydub import AudioSegment

import pysilk

async def mp3_to_pcm(mp3_data: BinaryIO) -> BytesIO:
    audio_segment = AudioSegment.from_file(mp3_data, format="mp3")
    
    pcm_data = audio_segment.set_frame_rate(24000).set_channels(1).raw_data

    return BytesIO(pcm_data)

def pcm_to_silk(pcm_data: BinaryIO) -> BytesIO:
    silk_io = BytesIO()

    pcm_bytes = pcm_data.read()
    with BytesIO() as pcm_io:
        pcm_io.write(pcm_bytes)
        pcm_io.seek(0)
        pysilk.encode(pcm_io, silk_io, 24000, 24000)

    silk_io.seek(0)
    return silk_io

async def mp3_to_silk(mp3_data: BinaryIO) -> BytesIO:
    pcm_data = await mp3_to_pcm(mp3_data)
    silk_data = pcm_to_silk(pcm_data)
    return silk_data