from flask import Flask, render_template, request, send_file
from music21 import stream, note, tempo
import openai
import os
import datetime

app = Flask(__name__)
api = ""

client = openai.OpenAI(api_key=api)

# Ensure folder exists
if not os.path.exists("generated_midi"):
    os.makedirs("generated_midi")


@app.route("/", methods=["GET", "POST"])
def index():
    midi_file_path = None
    if request.method == "POST":
        song_name = request.form.get("song_name")

        # Create music21 stream
        melody = stream.Stream()
        melody.append(tempo.MetronomeMark(number=120))

        # Generate notes using OpenAI
        chat = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"Create a sequence of notes for {song_name} using Music21 notation (e.g., C4 D4 E4). Use sharps and flats too. No explanations."
            }]
        )

        note_str = chat.choices[0].message.content.strip()
        notes = note_str.split()

        for n in notes:
            try:
                melody.append(note.Note(n, quarterLength=1))
            except:
                continue  # skip invalid notes

        # Save MIDI
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        midi_file_path = f"generated_midi/{song_name.replace(' ', '_')}_{timestamp}.mid"
        melody.write('midi', fp=midi_file_path)

    return render_template("index.html", midi_file_path=midi_file_path)


@app.route("/download/<path:filename>")
def download(filename):
    return send_file(filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
