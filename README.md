# **SafeCave | CavemanAI Monitoring Hub**

**SafeCave** is a high-performance MJPEG stream monitor designed to repurpose older hardware into a dedicated security mesh. Built as part of the **CavemanAI** ecosystem, it focuses on ease of use and the revitalization of "drawer tech" like Samsung Galaxy J3 phones to serve as "Cave Eyes".

The application features a "Mothership" viewing grid and a persistent "Command Center" for rapid situational snapshots.

### **Core Features**

* **Surgical MJPEG Handling**: A specialized `SafeCaveStreamWorker` designed to eliminate "Two SOI" terminal errors by strictly locating JPEG start/end bytes in the buffer.  
* **Auto-Rotation**: Intelligent frame detection that automatically rotates 90° if the mobile device is in a vertical orientation.  
* **Persistent Control**: A "Command Center" window that stays on top of other applications for instant access to the "Snapshot" trigger.  
* **Stone & Mint Palette**: Signature branding using deep slate tones with mint and purple accents for high visibility in low-light "cave" environments.

### **Technical Specifications**

* **Backbone**: Python 3.12.  
* **GUI**: PySide6.  
* **Networking**: Threaded `requests.Session` management.  
* **Default Target Hardware**: Android devices running IP Webcam or similar MJPEG servers (configured for IPs `192.168.1.109` and `192.168.1.241` by default).  Based on what IP is assigned to the Android device(s) by your router, the script’s IP’s will need to be replaced with your local device’s assigned IP.

### **Installation & Setup**

1. **Environment**: Ensure you are running Python 3.12+.

**Dependencies**:  
Bash  
	pip install PySide6 requests

	**Assets**: Ensure `SafeCave.jpeg` (the branding logo) is in the root directory.

2. **Network**: Verify your mobile devices are on the same local network and the IP addresses in the `PHONE_IPS` list match your hardware.  
3. **Execution**:  
   Bash  
   python SafeCave.py

