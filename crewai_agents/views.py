import subprocess
import os
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.http import HttpResponse
import psutil

# Simple global variable to track status (for MVP without database)
SCRIPT_STATUS = {
    'running': False,
    'pid': None
}

@staff_member_required
def run_script(request):
    """
    View to run the main.py script
    """
    global SCRIPT_STATUS
    
    # If already running, don't start again
    if SCRIPT_STATUS['running']:
        messages.warning(request, "The agents are already running.")
        return redirect('admin:index')
    
    try:
        # Get the absolute path to the project root
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Path to the script
        script_path = os.path.join(base_dir, 'crewai_agents', 'crew', 'main.py')
        
        # Check if in debug mode
        from django.conf import settings
        
        # First try with system Python
        python_executable = 'python'

        # If we're in DEBUG mode and system Python fails, try using virtual environment
        if settings.DEBUG:
            try:
                # Test if the system Python works
                subprocess.run([python_executable, "--version"], 
                            check=True, 
                            capture_output=True)
            except (subprocess.SubprocessError, FileNotFoundError):
                # System Python didn't work, try virtual environment
                venv_dir = os.path.join(base_dir, '.venv')
                
                # On Unix/Linux/Mac
                if os.name == 'posix':
                    python_executable = os.path.join(venv_dir, 'bin', 'python')
                # On Windows
                else:
                    python_executable = os.path.join(venv_dir, 'Scripts', 'python.exe')
        
        # Run the script with process output logging
        process = subprocess.Popen(
            [python_executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Update status
        SCRIPT_STATUS['running'] = True
        SCRIPT_STATUS['pid'] = process.pid
        
        messages.success(request, "Agents are now running! This may take some time to complete.")
    except Exception as e:
        messages.error(request, f"Error running script: {str(e)}")
    
    return redirect('admin:index')

@staff_member_required
def stop_script(request):
    """
    View to stop the running script
    """
    global SCRIPT_STATUS
    
    if not SCRIPT_STATUS['running']:
        messages.warning(request, "The agents are not currently running.")
        return redirect('admin:index')
    
    try:
        if SCRIPT_STATUS['pid']:
            # On Unix/Linux/Mac
            if os.name == 'posix':
                os.kill(SCRIPT_STATUS['pid'], 15)  # SIGTERM
            # On Windows
            else:
                import signal
                os.kill(SCRIPT_STATUS['pid'], signal.SIGTERM)
        
        SCRIPT_STATUS['running'] = False
        SCRIPT_STATUS['pid'] = None
        
        messages.success(request, "Agents have been stopped.")
    except Exception as e:
        messages.error(request, f"Error stopping script: {str(e)}")
    
    return redirect('admin:index')

def get_script_status(request):
    """
    View to get the current status of the script
    """
    global SCRIPT_STATUS
    
    # Check if process is still running
    if SCRIPT_STATUS['running'] and SCRIPT_STATUS['pid']:
        try:
            # On Unix/Linux/Mac
            if os.name == 'posix':
                os.kill(SCRIPT_STATUS['pid'], 0)  
            # On Windows
            else:
                import psutil
                psutil.Process(SCRIPT_STATUS['pid']).status()
        except (OSError, ProcessLookupError, psutil.NoSuchProcess):
            # Process is no longer running
            SCRIPT_STATUS['running'] = False
            SCRIPT_STATUS['pid'] = None
    
    return JsonResponse({
        'status': 'running' if SCRIPT_STATUS['running'] else 'stopped',
        'is_running': SCRIPT_STATUS['running']
    })

def test_view(request):
    return HttpResponse("Test view is working!")