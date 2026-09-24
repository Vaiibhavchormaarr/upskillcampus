import sys
from voice_calculator_core import normalize, calculate, format_result, speak# ---------- Input ----------
def make_voice_listener():
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("🎙️  Calibrating for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

    def listen():
        with mic as source:
            print("\n🎧 Listening...")
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=8)
        try:
            text = recognizer.recognize_google(audio)
            print(f"🗣️  You said: {text}")
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            speak("Speech service is unavailable. Check your internet connection.")
            return ""

    return listen


def make_text_listener():
    def listen():
        return input("\n⌨️  Type a command: ")
    return listen


# ---------- Main loop ----------



def main():
    text_mode = "--text" in sys.argv
    try:
        listen = make_text_listener() if text_mode else make_voice_listener()
    except Exception as e:
        print(f"Microphone unavailable ({e}). Falling back to text mode.")
        listen = make_text_listener()

    speak("Voice calculator ready. Say a calculation, or say quit to exit.")
    last_answer = None

    while True:
        try:
            spoken = listen()
        except (EOFError, KeyboardInterrupt):
            speak("Goodbye!")
            break
        except Exception:
            # e.g. listening timeout
            continue

        if not spoken.strip():
            speak("Sorry, I didn't catch that.")
            continue

        lowered = spoken.lower()
        if any(w in lowered for w in ("quit", "exit", "stop", "goodbye")):
            speak("Goodbye!")
            break
        if any(w in lowered for w in ("clear", "reset")):
            last_answer = None
            speak("Cleared.")
            continue

        try:
            expression = normalize(spoken, last_answer)
            print(f"🧮 Expression: {expression}")
            result = calculate(expression)
            last_answer = format_result(result)
            speak(f"The answer is {last_answer}")
        except ZeroDivisionError:
            speak("You can't divide by zero.")
        except (ValueError, SyntaxError, OverflowError):
            speak("Sorry, I couldn't calculate that.")


if __name__ == "__main__":
    main()
