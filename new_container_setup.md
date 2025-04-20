# New Container Setup Guide for cram_plan (with ROS, PyCRAM, and VcXsrv)

This guide walks you through setting up and running the cram_plan application in a Docker container on Windows, with graphical support via VcXsrv. It includes all steps from environment preparation to launching the application, plus the additional ROS launch command.

---

## 1. Prerequisites
- **Docker Desktop** (WSL 2 backend recommended)
- **Git** (e.g., Git for Windows)
- **VcXsrv** (X Server for Windows)
- **cram_plan application code**

---

## 2. Prepare Host Environment
- Clone your cram_plan repository:
  ```sh
  git clone https://github.com/BrianBosho/cram_plan.git PycramCode/cram_plan
  ```
- Prepare a folder for the Docker build and place your Dockerfile there.

---

## 3. Build the Docker Image
- Open a terminal and navigate to your Dockerfile directory:
  ```sh
  cd C:\Users\Bosho\docker_pycram_build
  docker build -t cram_robot .
  ```

---

## 4. Configure and Launch VcXsrv
- Start **XLaunch** from the Start Menu.
- Select:
  - "Multiple windows"
  - Display number: 0
  - "Start no client"
  - **Check** "Disable access control"
  - Enable "Clipboard" if desired
- Finish setup and ensure VcXsrv is running (icon in system tray).

---

## 5. Start the Docker Container
- Find your host IP address (e.g., via `ipconfig`).
- Set the DISPLAY variable in your terminal:
  ```powershell
  $env:DISPLAY = "<YOUR_IP>:0.0"
  ```
- Stop/remove any previous container (ignore errors if not found):
  ```powershell
  docker stop cram_robot
  docker rm cram_robot
  ```
- Run the container (adjust the volume path as needed):
  ```powershell
  docker run -d -p 8001:8001 `
    -e "DISPLAY=$env:DISPLAY" `
    -v "C:\Users\Bosho\Desktop\PycramCode\cram_plan:/home/capstone/cram_plan" `
    --name cram_robot cram_robot
  ```
- Verify the container is running:
  ```sh
  docker ps
  ```

---

## 6. One-Time Container Setup (ROS Workspace)
- Get a shell inside the container:
  ```sh
  docker exec -it cram_robot bash
  ```
- Inside the container, run:
  ```sh
  cd /home/capstone/workspace/ros/src/pycram
  git checkout 3e21535d633b7e2c668edac5f020e0cdc1565e07
  cd /home/capstone/workspace/ros
  catkin build
  source devel/setup.bash
  echo "source /home/capstone/workspace/ros/devel/setup.bash" >> ~/.bashrc
  ```

---

## 7. Install Application Dependencies
- Still inside the container:
  ```sh
  cd /home/capstone/cram_plan
  pip3 install -r requirements.txt
  ```

---

## 8. Run Your Application
- Still inside `/home/capstone/cram_plan` in the container:
  - **Start ROS launch (for IK and robot description):**
    ```sh
    roslaunch pycram ik_and_description.launch &
    ```
  - For the API/Web UI:
    ```sh
    python3 src/http_api.py
    ```
  - For the CLI:
    ```sh
    python3 src/cli.py
    ```
- If your app opens a GUI (e.g., PyBullet), it should appear on your Windows desktop via VcXsrv.

---

## 9. Accessing the Application (if running http_api.py)
- Open a browser on Windows and go to: [http://localhost:8001](http://localhost:8001)

---

## 10. Stopping and Restarting
- **Stop:**
  ```sh
  docker stop cram_robot
  ```
- **Start:**
  ```sh
  docker start cram_robot
  # Then docker exec -it cram_robot bash to re-enter the container
  ```

---

**Note:**
- The host IP may change if your network changes.
- Always start VcXsrv with "Disable access control" before running the container.
- You may need to re-run the `roslaunch` and your application command after restarting the container.
