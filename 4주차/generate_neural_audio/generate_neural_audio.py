"""
4주차 시험대비 요약 - 뉴럴 음성(Microsoft Edge TTS) 버전
Gemini/ChatGPT 수준의 자연스러운 음성
실행 전 설치: pip install edge-tts
"""

import asyncio
import edge_tts
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(OUTPUT_DIR, "제조데이터_4주차_오디오_학습_스크립트.txt")

VOICES = {
    "여자_선희": "ko-KR-SunHiNeural",
    "남자_인준": "ko-KR-InJoonNeural",
    "여자_혜진": "ko-KR-HyunsuNeural",
}

SELECTED_VOICE = VOICES["여자_선희"]
RATE = "+0%"
PITCH = "+0Hz"

with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    EXAM_TEXT = f.read()


async def generate_audio():
    print(f"뉴럴 음성 생성 중... (음성: {SELECTED_VOICE})")

    communicate = edge_tts.Communicate(
        text=EXAM_TEXT,
        voice=SELECTED_VOICE,
        rate=RATE,
        pitch=PITCH,
    )

    output_path = os.path.join(OUTPUT_DIR, "4주차_시험대비_뉴럴음성.mp3")
    await communicate.save(output_path)

    print(f"완료: {output_path}")
    print(f"파일 크기: {os.path.getsize(output_path) / 1024:.1f} KB")


if __name__ == "__main__":
    asyncio.run(generate_audio())
