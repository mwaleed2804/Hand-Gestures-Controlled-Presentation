import cv2
import os
import numpy as np
import time
import pyautogui
from cvzone.HandTrackingModule import HandDetector

#Configuration
SLIDE_FOLDER = r"C:\\BTechCSEAI\\Python\\Venv\\HandGesturePresentation\\Presentation"
GESTURE_THRESHOLD = 300
ANNOTATION_COLOR = (100, 150, 255)
ANNOTATION_THICKNESS = 10
COOLDOWN = 30 

#Initialization
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Camera", 320, 180)
cv2.namedWindow("Presentation", cv2.WINDOW_NORMAL)

#Load slides
pathImages = sorted(os.listdir(SLIDE_FOLDER), key=len)
slides = [cv2.imread(os.path.join(SLIDE_FOLDER, img)) for img in pathImages]
if not slides:
    print("No slides found!")
    exit()

#Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=2)

#State variables
imgNumber = 0
presentationStarted = False
standbyMode = False
annotations = [[]]
annotationNumber = -1
annotationStart = False
buttonPressed = False
cooldownCounter = 0

pointerMode = False
highlightColor = (100, 150, 255)
exitGestureConfirmed = False
exitStartTime = 0

blackScreenMode = False
whiteboardMode = False
presentationPaused = False

previousIndex = None

#Main Loop
while True:
    success, img = cap.read()
    if not success:
        continue

    img = cv2.flip(img, 1)

    #Choose slide background
    if whiteboardMode:
        currentSlide = 255 * np.ones_like(slides[imgNumber])
    elif blackScreenMode:
        currentSlide = np.zeros_like(slides[imgNumber])
    else:
        currentSlide = slides[imgNumber].copy()

    #Hand Detection
    hands, img = detector.findHands(img)

    #Gesture threshold line
    cv2.line(img, (0, GESTURE_THRESHOLD), (1280, GESTURE_THRESHOLD), (0, 255, 0), 5)
    cv2.putText(img, "Gesture Zone", (20, GESTURE_THRESHOLD - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    #START presentation with thumbs up from both hands
    if not presentationStarted and len(hands) == 2:
        fingers1 = detector.fingersUp(hands[0])
        fingers2 = detector.fingersUp(hands[1])
        if fingers1 == [1, 0, 0, 0, 0] and fingers2 == [1, 0, 0, 0, 0]:
            presentationStarted = True
            buttonPressed = True
            print("Presentation started")

    for hand in hands:
        cx, cy = hand["center"]
        lmList = hand["lmList"]
        fingers = detector.fingersUp(hand)

        #Show finger array
        cv2.putText(img, str(fingers), (cx - 100, cy - 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

        xVal = int(np.interp(lmList[8][0], [640, 1280], [0, 1280]))
        yVal = int(np.interp(lmList[8][1], [150, 570], [0, 720]))
        indexFinger = (xVal, yVal)

        if presentationStarted:
            if fingers == [1, 1, 1, 1, 1] and not buttonPressed:
                standbyMode = not standbyMode
                buttonPressed = True
                print("Standby Mode:", standbyMode)

            elif not standbyMode:
                if cy <= GESTURE_THRESHOLD and not buttonPressed:
                    if fingers == [0, 0, 0, 0, 1]:
                        if imgNumber < len(slides) - 1:
                            imgNumber += 1
                            annotations = [[]]
                            annotationNumber = -1
                            annotationStart = False
                            blackScreenMode = False
                            whiteboardMode = False
                            buttonPressed = True
                            pyautogui.press('right')
                            print("Next Slide")
                        #Show end of slides message
                        else:
                            cv2.putText(currentSlide, "End of Slides!", (40, 100), 
                                      cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)

                    elif fingers == [1, 0, 0, 0, 0]:
                        if imgNumber > 0:
                            imgNumber -= 1
                            annotations = [[]]
                            annotationNumber = -1
                            annotationStart = False
                            blackScreenMode = False
                            whiteboardMode = False
                            buttonPressed = True
                            pyautogui.press('left')
                            print("Previous Slide")

                    elif fingers == [0, 1, 1, 1, 0]:
                        annotations = [[]]
                        annotationNumber = -1
                        annotationStart = False
                        buttonPressed = True
                        print("Annotations Cleared")

                    elif fingers == [0, 1, 0, 1, 0]:
                        blackScreenMode = not blackScreenMode
                        whiteboardMode = False
                        annotations = [[]]
                        annotationNumber = -1
                        buttonPressed = True
                        print("Black Screen Toggled")

                    elif fingers == [1, 1, 1, 0, 0]:
                        whiteboardMode = not whiteboardMode
                        blackScreenMode = False
                        annotations = [[]]
                        annotationNumber = -1
                        buttonPressed = True
                        print("Whiteboard Mode Toggled")

                if fingers == [0, 0, 0, 0, 0] and imgNumber == len(slides) - 1:
                    if not exitGestureConfirmed:
                        exitGestureConfirmed = True
                        exitStartTime = time.time()
                    elif time.time() - exitStartTime > 1:
                        cv2.putText(currentSlide, "Exiting...", (40, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)
                        cv2.imshow("Presentation", currentSlide)
                        cv2.imshow("Camera", img)
                        cv2.waitKey(1000)
                        cap.release()
                        cv2.destroyAllWindows()
                        print("Exited Presentation.")
                        exit()
                else:
                    exitGestureConfirmed = False

                if fingers == [0, 1, 0, 0, 0]:
                    if not annotationStart:
                        annotationStart = True
                        annotationNumber += 1
                        annotations.append([])
                    if previousIndex is None:
                        previousIndex = indexFinger
                    xSmooth = int((3 * previousIndex[0] + indexFinger[0]) / 4)
                    ySmooth = int((3 * previousIndex[1] + indexFinger[1]) / 4)
                    previousIndex = (xSmooth, ySmooth)
                    annotations[annotationNumber].append(previousIndex)
                    cv2.circle(currentSlide, previousIndex, 8, ANNOTATION_COLOR, cv2.FILLED)
                else:
                    annotationStart = False
                    previousIndex = None

                if fingers == [0, 1, 1, 0, 0]:
                    pointerMode = True
                    cv2.circle(currentSlide, indexFinger, 12, highlightColor, cv2.FILLED)
                else:
                    pointerMode = False

    if buttonPressed:
        cooldownCounter += 1
        if cooldownCounter > COOLDOWN:
            buttonPressed = False
            cooldownCounter = 0

    if not blackScreenMode:
        for annotation in annotations:
            for j in range(1, len(annotation)):
                cv2.line(currentSlide, annotation[j - 1], annotation[j], ANNOTATION_COLOR, ANNOTATION_THICKNESS)

    imgSmall = cv2.resize(img, (213, 120))
    h, w, _ = currentSlide.shape
    cv2.rectangle(currentSlide, (w - 215, 0), (w, 122), (230, 230, 230), cv2.FILLED)
    currentSlide[1:121, w - 214:w - 1] = imgSmall

    cv2.putText(currentSlide, f"Slide {imgNumber + 1}/{len(slides)}", (w - 250, h - 30),
                cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

    if not presentationStarted:
        cv2.putText(currentSlide, "Show Thumbs Up to Start", (40, 100),
                    cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)
    elif standbyMode:
        overlay = currentSlide.copy()
        cv2.rectangle(overlay, (0, 0), (1280, 720), (0, 0, 0), -1)
        currentSlide = cv2.addWeighted(overlay, 0.4, currentSlide, 0.6, 0)
        cv2.putText(currentSlide, "Standby Mode", (40, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 2)
    elif presentationPaused:
        overlay = currentSlide.copy()
        cv2.rectangle(overlay, (0, 0), (1280, 720), (0, 0, 0), -1)
        currentSlide = cv2.addWeighted(overlay, 0.4, currentSlide, 0.6, 0)
        cv2.putText(currentSlide, "Gesture Recognition Paused", (40, 100),
                    cv2.FONT_HERSHEY_PLAIN, 3, (200, 200, 200), 2)

    cv2.imshow("Presentation", currentSlide)
    cv2.imshow("Camera", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()