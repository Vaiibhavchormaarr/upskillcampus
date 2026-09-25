# 🎙️ Voice Command Calculator

A Python-based voice calculator that allows users to perform mathematical calculations using natural voice commands. It supports both **voice mode** and **text mode**, making it easy to use even when a microphone is unavailable.

## ✨ Features

* 🎤 Voice-based calculator
* ⌨️ Text input mode
* 🔊 Text-to-speech responses
* 🔢 Understands numbers written in words
* ➕ Addition
* ➖ Subtraction
* ✖️ Multiplication
* ➗ Division
* `%` Modulo operations
* √ Square root
* ² Square numbers
* ³ Cube numbers
* 📊 Percentage calculations
* ⚡ Power/exponent calculations
* 🔄 Use the previous answer in a new calculation
* 🛑 Voice commands to quit or exit
* 🧹 Clear/reset the previous answer
* 🔐 Safe expression evaluation without using `eval()`

## 🧮 Example Voice Commands

You can say commands such as:

```text
5 plus 3
twenty five times four
square root of 144
10 percent of 200
2 to the power of 8
answer divided by 2
quit
```

The calculator also supports using the previous result:

```text
5 plus 3
answer divided by 2
```

## 🛠️ Technologies Used

* Python
* SpeechRecognition
* PyAudio
* pyttsx3
* AST (Abstract Syntax Tree)
* Python Math and Operator modules

## 📁 Project Structure

```text
VoiceCalculator/
│
├── voice_calculator.py
├── voice_calculator_core.py
└── README.md
```

### `voice_calculator.py`

This file handles the main calculator application, microphone input, speech recognition, text input mode, and the main program loop.

### `voice_calculator_core.py`

This file contains the core calculator functionality, including voice-command conversion, mathematical operations, number-word conversion, text-to-speech, and safe calculation.

## ⚙️ Installation

Make sure Python is installed on your computer.

Install the required libraries:

```bash
pip install SpeechRecognition pyaudio pyttsx3
```

## ▶️ How to Run

### Voice Mode

Run:

```bash
python voice_calculator.py
```

The calculator will use your microphone to listen for commands.

### Text Mode

If you don't have a microphone or want to type commands instead, run:

```bash
python voice_calculator.py --text
```

You can then type commands directly into the terminal.

## 💡 Example

```text
🎙️ Voice calculator ready.

You: 5 plus 3

🤖 The answer is 8
```

Another example:

```text
You: square root of 144

🤖 The answer is 12
```

## 🔐 Safe Calculation

The calculator does not directly use Python's `eval()` function. Instead, it parses mathematical expressions using Python's AST module and allows only supported mathematical operations.

## 🚀 Future Improvements

* Support for more natural language commands
* Improved speech recognition
* Multiple language support
* Graphical User Interface (GUI)
* More advanced mathematical functions
* Offline speech recognition
* Better error handling

## 👨‍💻 Author

**Vaibhav Chormar**

Computer Science & Engineering Student

## 📄 License

This project is created for educational and learning purposes.
