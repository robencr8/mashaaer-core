# Add to app.py to support audio testing

from flask import render_template

@app.route("/audio-test")
def audio_test():
    """Audio test page for debugging autoplay issues"""
    return render_template("render_static", path="/audio_test.html")

@app.route("/audio-fix")
def audio_fix_guide():
    """Display the audio fix documentation"""
    with open("AUDIO_FIX.md", "r") as f:
        content = f.read()
    return render_template("markdown.html", content=content, title="Audio Fix Guide")
