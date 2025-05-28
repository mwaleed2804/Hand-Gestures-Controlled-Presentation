Hand Gestures Controlled Presentation

Users can control presentation slides with basic hand motions using a computer vision-based system. Built for contactless interaction during lectures, meetings, or public speaking events.

📌 Features
-  Hand gestures let you navigate next ➡️ and previous ⬅️ slides.
-  🖊️ Annotation on slides using finger tracking.
-✋ Standby mode toggled off with an open-palm gesture.
- 👇 Using index finger, highlight components.
- 🎯 TensorFlow for manual gesture identification.
- 🎥 OpenCV and CVZone's real-time gesture recognition.

🧠 Technologies Used

- Python
- OpenCV
- CVZone
- TensorFlow
- PyAutoGUI (for mimicking keyboard/mouse inputs)

🎮 How It Works
1. The webcam captures the user's hand in real time.
2. CVZone identifies hand landmarks.
3. Gestures are coupled with pre-trained custom models (using TensorFlow).
4. The gesture provides the basis for the system simulating keypresses to:
- Move to the next/previous slide.
- Start or end the presentation.
- Annotate or point during the presentation.
