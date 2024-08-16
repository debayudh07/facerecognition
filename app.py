from flask import Flask, render_template, Response, redirect, url_for
from camera import Video
import os
import cv2
import time

app = Flask(__name__)

# Ensure the static folder exists
if not os.path.exists('static'):
    os.makedirs('static')

@app.route('/')
def index():
    # Get the latest screenshot filename
    screenshots = sorted([f for f in os.listdir('static') if f.startswith('screenshot_')],
                         key=lambda x: os.path.getctime(os.path.join('static', x)),
                         reverse=True)
    latest_screenshot = screenshots[0] if screenshots else None

    return render_template('index.html', latest_screenshot=latest_screenshot)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame +
              b'\r\n\r\n')

@app.route('/video')
def video():
    return Response(gen(Video()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/screenshot')
def screenshot():
    video_capture = cv2.VideoCapture(0)
    
    ret, frame = video_capture.read()
    if ret:
        filename = f'static/screenshot_{int(time.time())}.jpg'
        cv2.imwrite(filename, frame)
    
    video_capture.release()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
