"""
5주차 시험대비 요약 - 뉴럴 음성(Microsoft Edge TTS) 버전
Gemini/ChatGPT 수준의 자연스러운 음성
실행 전 설치: pip install edge-tts
"""

import asyncio
import edge_tts
import os
import re

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(OUTPUT_DIR, "## ■ 자주 나올 질문 — 구어체 답변.txt")


def clean_text(text):
    """마크다운/특수문자를 제거하고 자연스러운 읽기용 텍스트만 남긴다."""
    # 의미를 가진 기호는 자연어로 치환
    text = text.replace("→", " ")
    text = text.replace("·", " ")
    # 한글/영문/숫자/공백과 문장부호(. , ? !)만 남기고 나머지 특수문자 제거
    text = re.sub(r"[^\w\s.,?!]", " ", text, flags=re.UNICODE)
    text = text.replace("_", " ")
    # 줄 단위로 공백 정리 후, 빈 줄 과다 제거
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines()]
    cleaned = "\n".join(ln for ln in lines if ln)
    return cleaned

VOICES = {
    "여자_선희": "ko-KR-SunHiNeural",
    "남자_인준": "ko-KR-InJoonNeural",
    "여자_혜진": "ko-KR-HyunsuNeural",
}

SELECTED_VOICE = VOICES["여자_선희"]
RATE = "+0%"
PITCH = "+0Hz"

with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    EXAM_TEXT = clean_text(f.read())


async def generate_audio():
    print(f"뉴럴 음성 생성 중... (음성: {SELECTED_VOICE})")

    communicate = edge_tts.Communicate(
        text=EXAM_TEXT,
        voice=SELECTED_VOICE,
        rate=RATE,
        pitch=PITCH,
    )

    output_path = os.path.join(OUTPUT_DIR, "자주_나올_질문_구어체_답변.mp3")
    await communicate.save(output_path)

    print(f"완료: {output_path}")
    print(f"파일 크기: {os.path.getsize(output_path) / 1024:.1f} KB")


if __name__ == "__main__":
    asyncio.run(generate_audio())
