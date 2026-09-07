import speech_recognition as sr


_recognizer = sr.Recognizer()
_recognizer.energy_threshold = 260
_recognizer.dynamic_energy_threshold = True
_recognizer.pause_threshold = 1.25
_recognizer.non_speaking_duration = 0.45


def _recognize(audio):
    for language in ("en-IN", "en-US", "en-GB"):
        try:
            text = _recognizer.recognize_google(audio, language=language)
            if text and text.strip():
                return text.strip()
        except sr.UnknownValueError:
            continue
        except sr.RequestError:
            continue
    return None


def listen_and_transcribe():
    """
    Listen to the microphone and transcribe speech to text.
    Uses a wider capture window for more natural commands.
    """
    try:
        with sr.Microphone() as source:
            _recognizer.adjust_for_ambient_noise(source, duration=0.7)

            for attempt in range(2):
                try:
                    audio = _recognizer.listen(
                        source,
                        timeout=7 if attempt == 0 else 4,
                        phrase_time_limit=15,
                    )
                except sr.WaitTimeoutError:
                    continue

                text = _recognize(audio)
                if text:
                    return text

        return None
    except Exception as exc:
        print(f"Mic error: {exc}")
        return None
