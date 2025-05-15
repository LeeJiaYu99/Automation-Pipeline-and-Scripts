import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import subprocess
import os
import sys

class CustomizedService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ModelInferenceAPI"
    _svc_display_name_ = "Model Inference API"
    _svc_description_ = "Runs Flask API for model inferencing"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("ModelInferenceAPI - Starting service")
        self.main()

    def main(self):
        # Start your Flask app as a subprocess
        python_exe = sys.executable
        script_path = os.path.join(os.path.dirname(__file__), "app.py")
        self.proc = subprocess.Popen([python_exe, script_path])
        
        # Wait until service is stopped
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
        self.proc.terminate()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(CustomizedService)
