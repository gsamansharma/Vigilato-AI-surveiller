import re
import subprocess
import time
from flask import *
import cv2
import os
from simple_facerec import SimpleFacerec

app = Flask(__name__)


@app.route('/')
def main():
    return render_template("login.html")


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        phone_no=request.form.get("phone_number")
        files = request.files.getlist("file")
        print(phone_no)
        image_folder='faces_'+phone_no+'/'
        print(image_folder)
        bash_command="mkdir "+image_folder
        print(bash_command)
        os.system(bash_command)
        for file in files:
            file.save(os.path.join(image_folder,file.filename))
        return "<h1>Files Uploaded Successfully.!</h1><br><A href=\"/\">Go back to login</A>"


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/surveil', methods=['POST'])
def surveil():
    if request.method == 'POST':
        phone_no = request.form.get("phone_number")
        img_database='faces_'+phone_no+'/'
        IP_address = request.form.get("camera_address")
        camera_address='http://'+IP_address+'/videofeed'
        # camera_address=0
        print(img_database)
        print(IP_address)
        print(IP_address)

        sfr = SimpleFacerec()
        sfr.load_encoding_images(img_database)

        # Load Camera
        cap = cv2.VideoCapture(camera_address)
        # return render_template("signup.html")
        while True:
            ret, frame = cap.read()

            # Detect Faces
            name = 'Unknown'
            face_locations, face_names = sfr.detect_known_faces(frame)

            for face_loc, name in zip(face_locations, face_names):
                y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
                cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
                if name == 'Unknown':
                    time.sleep(5)
                    cv2.imwrite(os.path.join('unknown_faces/', 'alert0.jpg'), frame)
                    cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
                    result = subprocess.run(['imgur-uploader', 'unknown_faces/alert0.jpg'], stdout=subprocess.PIPE)
                    result.stdout.decode('utf8')
                    res = result.stdout.splitlines()
                    res1 = str(res[1])
                    img_url = re.findall('(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+', res1)
                    print(img_url[0])
                    message = 'kdeconnect-cli -d b3ea48a377a40a72 --destination +91' + str(
                        phone_no) + ' --send-sms \"Unknown visitor detected ' + img_url[0] + '\"'
                    print(message)
                    os.system(message)

            if(ret):
                cv2.imshow("Frame", frame)

            key = cv2.waitKey(1)
            if key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()


        return "<h1>Files Uploaded Successfully.!</h1>"


if __name__ == "__main__":
    app.run(host= '0.0.0.0')