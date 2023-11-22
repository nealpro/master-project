import subprocess

def speak(content):
    p = subprocess.Popen(f"espeak-ng -v mb-us1 \"{content}\"",
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    print("Speak finished.")

speak("Hello, world!")