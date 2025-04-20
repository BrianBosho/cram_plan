# Docker Guide: Running PyCRAM Simulation with VSCode and Windows X Server

This guide provides step-by-step instructions for running the PyCRAM simulation inside a Docker container, using VSCode on Windows, and displaying the GUI via an X server.

---

## Steps After Starting or Rebooting

### 1. Start the Docker Container
- Open your VSCode window (the same workspace as your project).
- Ensure your Docker container (e.g., `cram_robot`) is running. If not, start it from Docker Desktop or with:
  ```powershell
  docker start cram_robot
  ```

### 2. Set Up the X Server Display (First PowerShell Terminal)
- Open a new PowerShell terminal.
- Set the DISPLAY environment variable:
  ```powershell
  $env:DISPLAY = "192.168.1.196:0.0"
  ```
- Confirm it is set correctly:
  ```powershell
  echo $env:DISPLAY
  # Should output: 192.168.1.196:0.0
  ```

### 3. Start a Docker Bash Terminal (Second PowerShell Terminal)
- Open another PowerShell terminal.
- Enter the Docker container:
  ```powershell
  docker exec -it cram_robot bash
  ```

### 4. Launch ROS in the Docker Container
- In the same Docker terminal from step 3, run:
  ```bash
  roslaunch pycram ik_and_description.launch &
  ```
- Leave this terminal running.

### 5. Open Another Docker Terminal for Running Programs (Third PowerShell Terminal)
- Open a new PowerShell terminal.
- Enter the Docker container again:
  ```powershell
  docker exec -it cram_robot bash
  ```

### 6. Set the DISPLAY Variable in Docker
- In the Docker bash terminal, set the DISPLAY variable to match Windows:
  ```bash
  export DISPLAY=192.168.1.196:0.0
  ```
- Confirm it:
  ```bash
  echo $DISPLAY
  # Should output: 192.168.1.196:0.0
  ```

### 7. Run the PyCRAM Python Program
- In the same Docker terminal, navigate to your project directory (e.g., `~/cram_plan/src`).
- Run the API server:
  ```bash
  python3 api.py
  ```
- This should launch a window on your X server where you can interact with the PyCRAM simulation.

### 8. (Optional) Run Tests in Another Docker Terminal
- Repeat step 5 to open another Docker terminal if needed.
- Run your test script:
  ```bash
  python3 test_api.py
  ```

---

**Note:**
- Ensure your X server (e.g., Xming or VcXsrv) is running on Windows and allows connections from your Docker container's IP.
- Replace `192.168.1.196` with your actual host IP if different.
- All commands in Docker bash use `export DISPLAY=...` (not PowerShell syntax).
