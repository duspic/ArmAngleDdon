import streamlit as st
import mediapipe as mp
import pandas as pd
import numpy as np
import cv2
import csv  


# local import
import utils

VIDEO_SOURCE = 'static/video1.mp4'
DATA_SOURCE = 'Angles.csv'
RIGHT_PROTRACTOR = 'static/right.png'
LEFT_PROTRACTOR = 'static/left.png'




@st.cache(allow_output_mutation=True)
def loadOnce():
    pose = mp_pose.Pose(min_detection_confidence=0.8, min_tracking_confidence=0.8)
    rprotractor = cv2.imread(RIGHT_PROTRACTOR,cv2.IMREAD_UNCHANGED)
    lprotractor = cv2.imread(LEFT_PROTRACTOR,cv2.IMREAD_UNCHANGED)

    return pose,rprotractor,lprotractor

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

pose, rprotractor, lprotractor = loadOnce()



st.title('Video stream')
start_it = st.sidebar.button('Start')
stop_it = st.sidebar.button('Stop')
video_placeholder = st.empty()



vid = cv2.VideoCapture(VIDEO_SOURCE)
frame_no = 0

if start_it:

    with open(DATA_SOURCE, 'w', encoding='UTF8') as data:
        header = ['Left_arm_angles','Right_arm_angles']
        writer = csv.writer(data)
        writer.writerow(header)

        while vid.isOpened():

            success, image = vid.read()
            if not success:
                print("End.")
                break

            height,width = image.shape[:2]

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True

            # Fetch shoulder and elbow points
            point_list = results.pose_landmarks.landmark[11:15]

            # Make them into regular x,y coordinates
            for i in range(len(point_list)):
                point_list[i] = utils.denormalizePoint(point_list[i],height,width)
                x,y = point_list[i]
                # Draw them for visualization
                image[y-2:y+2,x-2:x+2,:] = [255,0,0]

            lshoulder,rshoulder,lelbow,relbow = point_list

            langle = utils.drawAngle(lelbow,lshoulder,image,'left',rprotractor)
            rangle = utils.drawAngle(relbow,rshoulder,image,'right',lprotractor)

            writer.writerow([langle,rangle])


            # draw
            video_placeholder.image(image)
        

    st.write("Video Done.")

if stop_it:
    data = pd.read_csv(DATA_SOURCE)
    st.subheader('Raw Data')
    st.write(data)
    
    lefthand = np.array(data[data.columns[0]]).round(2)
    righthand = np.array(data[data.columns[1]]).round(2)
    
    l_max = np.amax(lefthand)
    r_max = np.amax(righthand)
    st.write("left hand maximum: %s"%l_max)
    st.write("right hand maximum: %s"%r_max)

    st.line_chart(data)

