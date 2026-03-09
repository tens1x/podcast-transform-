import time
import requests
from http import HTTPStatus
from dashscope.audio.asr import Transcription


def transcribe_audio(audio_url: str, language: str = 'zh') -> str:
    print('Submitting transcription task...')
    task_response = Transcription.async_call(
        model='paraformer-v2',
        file_urls=[audio_url],
        language_hints=[language, 'en'],
    )

    if task_response.status_code != HTTPStatus.OK:
        raise RuntimeError(
            f'Transcription submission failed: '
            f'{task_response.code} - {task_response.message}'
        )

    task_id = task_response.output.task_id
    print(f'Task submitted. Task ID: {task_id}')
    print('Waiting for transcription to complete...')

    # Poll every 5 seconds with progress feedback
    while True:
        time.sleep(5)
        result = Transcription.fetch(task=task_id)
        status = result.output.task_status
        print(f'\rTranscription status: {status}', end='', flush=True)

        if status == 'SUCCEEDED':
            print()
            return _extract_text(result)
        elif status == 'FAILED':
            print()
            raise RuntimeError(
                f'Transcription failed: {result.output}'
            )


def _extract_text(result) -> str:
    results = result.output.get('results')
    if not results:
        raise RuntimeError('No transcription results returned')

    transcription_url = results[0].get('transcription_url')
    if not transcription_url:
        raise RuntimeError('No transcription URL in result')

    resp = requests.get(transcription_url, timeout=30)
    resp.raise_for_status()
    transcript_data = resp.json()

    full_text = ''
    for transcript in transcript_data.get('transcripts', []):
        full_text += transcript.get('text', '')

    if not full_text:
        raise RuntimeError('Transcription result is empty')

    return full_text
