from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
import subprocess
import os
import sys
import json
import psutil
import tempfile
import logging
import time

logger = logging.getLogger(__name__)

class CrewAdmin(ModelAdmin):
    list_display = ('name', 'process', 'verbose', 'run_button', 'stop_button', 'status')
    filter_horizontal = ('agents', 'tasks')
    ordering = ('name',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        docker_temp = os.getenv('DOCKER_TEMP_DIR', '/tmp')
        self.process_file = os.path.join(docker_temp, 'crew_processes.json')
        self._ensure_process_file()
    
    def is_running_in_docker(self):
        """Check if we're running inside a Docker container"""
        return os.path.exists('/.dockerenv')

    def get_container_id(self):
        """Get current Docker container ID if running in Docker"""
        try:
            with open('/proc/1/cpuset') as f:
                path = f.read().strip()
                return path.split('/')[-1]
        except:
            return None
    
    def _ensure_process_file(self):
        """Ensure the process file exists and is valid JSON with proper permissions"""
        try:
            if not os.path.exists(self.process_file):
                with open(self.process_file, 'w') as f:
                    json.dump({}, f)
                os.chmod(self.process_file, 0o666)
            else:
                try:
                    with open(self.process_file, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError:
                    with open(self.process_file, 'w') as f:
                        json.dump({}, f)
        except Exception as e:
            logger.error(f"Error ensuring process file: {e}")
            raise

    def load_processes(self):
        """Load running processes from temporary file with Docker-aware error handling"""
        try:
            with open(self.process_file, 'r') as f:
                processes = json.load(f)
            valid_processes = {}
            for crew_id, process_info in processes.items():
                if self.is_process_running(process_info):
                    valid_processes[crew_id] = process_info
            self.save_processes(valid_processes)
            return valid_processes
        except Exception as e:
            logger.error(f"Error loading processes in Docker: {e}")
            return {}

    def save_processes(self, processes):
        """Save running processes to temporary file with Docker-aware error handling"""
        try:
            temp_file = f"{self.process_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(processes, f)
            os.replace(temp_file, self.process_file)
        except Exception as e:
            logger.error(f"Error saving processes in Docker: {e}")

    def is_process_running(self, process_info):
        """Check if a process is running with Docker considerations"""
        try:
            if isinstance(process_info, dict):
                pid = process_info['pid']
            else:
                pid = process_info
                
            try:
                process = psutil.Process(pid)
                if process.is_running() and process.status() != psutil.STATUS_ZOMBIE:
                    return True
            except:
                result = subprocess.run(['ps', '-p', str(pid)], capture_output=True)
                return result.returncode == 0
                
            return False
        except Exception as e:
            logger.error(f"Error checking process status in Docker: {e}")
            return False

    def _get_script_path(self):
        """Get the path to the main script with Docker-aware validation"""
        try:
            project_root = settings.BASE_DIR
            
            script_path = os.getenv('CREW_SCRIPT_PATH', os.path.join(
                project_root,
                'crewai_agents',
                'crew',
                'main.py'
            ))
            
            logger.debug(f"Resolved script path in Docker: {script_path}")
            
            if not os.path.exists(script_path):
                logger.error(f"Script not found at {script_path} in Docker environment")
                raise FileNotFoundError(f"Script not found at: {script_path}")
            
            return script_path
        except Exception as e:
            logger.error(f"Error getting script path in Docker: {e}")
            raise

    def run_script_view(self, request, crew_id):
        """Handle the run script action with Docker considerations"""
        logger.info(f"Running script for crew {crew_id} in Docker environment")

        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, "You must be logged in as staff to perform this action.")
            return self.response_post_save_change(request, None)

        try:
            processes = self.load_processes()
            
            try:
                main_script_path = self._get_script_path()
                logger.info(f"Script path in Docker: {main_script_path}")
                
                if not os.path.exists(main_script_path):
                    raise FileNotFoundError(f"Script not found at: {main_script_path}")
                
                script_dir = os.path.dirname(main_script_path)
                logger.info(f"Directory contents in Docker {script_dir}: {os.listdir(script_dir)}")
                
            except Exception as e:
                logger.error(f"Error locating script in Docker: {str(e)}")
                messages.error(request, f"Error locating script in Docker: {str(e)}")
                return self.response_post_save_change(request, None)

            try:
                env = os.environ.copy()
                env['PYTHONUNBUFFERED'] = '1'
                
                process = subprocess.Popen(
                    f"python {main_script_path}",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                    env=env,
                    text=True,
                    cwd=script_dir
                )
                
                time.sleep(2)
                
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    error_msg = (
                        f"Process failed to start in Docker.\n"
                        f"Return code: {process.returncode}\n"
                        f"stdout: {stdout}\n"
                        f"stderr: {stderr}"
                    )
                    logger.error(error_msg)
                    messages.error(request, "Process failed to start in Docker. Check server logs for details.")
                    return self.response_post_save_change(request, None)
                
                logger.info(f"Process started in Docker with PID: {process.pid}")
                
                # Store process information
                process_info = {
                    'pid': process.pid,
                    'start_time': time.time(),
                    'script_path': main_script_path,
                    'working_dir': script_dir,
                    'container_id': self.get_container_id()
                }
                processes[str(crew_id)] = process_info
                self.save_processes(processes)
                
                stored_processes = self.load_processes()
                logger.info(f"Stored process info in Docker: {stored_processes}")
                
                messages.success(request, f"Crew {crew_id} Has started!")
                
            except Exception as e:
                logger.error(f"Error starting process in Docker: {e}", exc_info=True)
                messages.error(request, f"Error starting process in Docker: {str(e)}")
                return self.response_post_save_change(request, None)

        except Exception as e:
            logger.error(f"Error in run_script_view Docker: {e}", exc_info=True)
            messages.error(request, f"Error starting crew {crew_id} in Docker: {str(e)}")

        return self.response_post_save_change(request, None)

    def stop_script_view(self, request, crew_id):
        """Handle the stop script action with Docker considerations"""
        logger.info(f"Stopping script for crew {crew_id} in Docker")
        
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, "You must be logged in as staff to perform this action.")
            return self.response_post_save_change(request, None)

        try:
            processes = self.load_processes()
            crew_id_str = str(crew_id)

            if crew_id_str in processes:
                process_info = processes[crew_id_str]
                pid = process_info['pid']
                
                try:
                    subprocess.run(['kill', '-TERM', str(pid)], check=False)
                    time.sleep(2)
                    
                    if self.is_process_running(pid):
                        subprocess.run(['kill', '-9', str(pid)], check=False)
                except Exception as e:
                    logger.error(f"Error killing process in Docker: {e}")
                
                del processes[crew_id_str]
                self.save_processes(processes)
                messages.success(request, f"Crew {crew_id} has stopped!")
            else:
                messages.info(request, f"No running process found for crew {crew_id} in Docker.")

        except Exception as e:
            logger.error(f"Error in stop_script_view Docker: {e}")
            messages.error(request, f"Error stopping crew {crew_id} in Docker: {str(e)}")

        return self.response_post_save_change(request, None)

    def run_button(self, obj):
        return format_html(
            '<a class="button" style="background-color: #28a745; color: white; padding: 5px 10px; '
            'text-decoration: none; border-radius: 4px;" href="{}">Start Agents</a>',
            reverse('admin:crewai_agents_crew_run_script', args=[obj.pk])
        )
    run_button.short_description = "Run Crew"

    def stop_button(self, obj):
        return format_html(
            '<a class="button" style="background-color: #dc3545; color: white; padding: 5px 10px; '
            'text-decoration: none; border-radius: 4px;" href="{}">Stop Agents</a>',
            reverse('admin:crewai_agents_crew_stop_script', args=[obj.pk])
        )
    stop_button.short_description = "Stop Crew"

    def status(self, obj):
        processes = self.load_processes()
        if str(obj.pk) in processes and self.is_process_running(processes[str(obj.pk)]):
            return format_html(
                '<span style="color: #28a745;">Running</span>'
            )
        return format_html(
            '<span style="color: #dc3545;">Not Running</span>'
        )
    status.short_description = "Status"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'run-script/<int:crew_id>/',
                self.admin_site.admin_view(self.run_script_view),
                name='crewai_agents_crew_run_script'
            ),
            path(
                'stop-script/<int:crew_id>/',
                self.admin_site.admin_view(self.stop_script_view),
                name='crewai_agents_crew_stop_script'
            ),
        ]
        return custom_urls + urls