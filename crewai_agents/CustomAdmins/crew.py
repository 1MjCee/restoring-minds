from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.db import transaction
from django.core.exceptions import PermissionDenied
from filelock import FileLock
import subprocess
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DockerConfig:
    """Docker configuration settings"""
    memory_limit: str = "2g"
    cpu_limit: str = "1.0"
    timeout: int = 30
    network: str = "crew_network"
    
class CrewError(Exception):
    """Base exception for crew operations"""
    pass

class DockerError(CrewError):
    """Docker-specific errors"""
    pass

class ProcessError(CrewError):
    """Process management errors"""
    pass

class DockerService:
    """Handles Docker container operations"""
    
    def __init__(self, config: DockerConfig):
        self.config = config
        
    def start_container(self, crew_id: int, script_path: str, env: Dict[str, str]) -> str:
        """Start a Docker container for the crew"""
        try:
            cmd = [
                'docker', 'run', '-d',
                '--memory', self.config.memory_limit,
                '--cpus', self.config.cpu_limit,
                '--network', self.config.network,
                '-v', f"{script_path}:/app/script.py",
                '--name', f"crew_{crew_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'crew-runtime:latest',
                'python', '/app/script.py'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            container_id = result.stdout.strip()
            
            if not container_id:
                raise DockerError("Failed to get container ID")
                
            return container_id
            
        except subprocess.CalledProcessError as e:
            raise DockerError(f"Docker command failed: {e.stderr}")
        except Exception as e:
            raise DockerError(f"Container start failed: {str(e)}")
    
    def stop_container(self, container_id: str) -> None:
        """Stop and remove a Docker container"""
        try:
            # Stop container
            subprocess.run(
                ['docker', 'stop', container_id],
                capture_output=True,
                check=True,
                timeout=self.config.timeout
            )
            
            # Remove container
            subprocess.run(
                ['docker', 'rm', container_id],
                capture_output=True,
                check=True,
                timeout=self.config.timeout
            )
        except subprocess.TimeoutExpired:
            raise DockerError(f"Container operation timed out: {container_id}")
        except subprocess.CalledProcessError as e:
            raise DockerError(f"Container operation failed: {e.stderr}")
    
    def check_container(self, container_id: str) -> bool:
        """Check if container is running"""
        try:
            result = subprocess.run(
                ['docker', 'inspect', '--format', '{{.State.Running}}', container_id],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().lower() == 'true'
        except subprocess.CalledProcessError:
            return False

class ProcessTracker:
    """Manages process tracking and status"""
    
    def __init__(self, process_file: str):
        self.process_file = process_file
        self.lock_file = f"{process_file}.lock"
        
    def _ensure_process_file(self) -> None:
        """Ensure process file exists and is valid"""
        with FileLock(self.lock_file):
            if not os.path.exists(self.process_file):
                self._create_process_file()
            self._validate_process_file()
    
    def _create_process_file(self) -> None:
        """Create new process file with secure permissions"""
        with open(self.process_file, 'w') as f:
            json.dump({}, f)
        os.chmod(self.process_file, 0o600)
    
    def _validate_process_file(self) -> None:
        """Validate process file content"""
        try:
            with open(self.process_file, 'r') as f:
                processes = json.load(f)
            if not isinstance(processes, dict):
                raise ProcessError("Invalid process file format")
        except json.JSONDecodeError:
            raise ProcessError("Corrupted process file")
    
    def get_process(self, crew_id: str) -> Optional[Dict[str, Any]]:
        """Get process information for crew"""
        self._ensure_process_file()
        with FileLock(self.lock_file):
            with open(self.process_file, 'r') as f:
                processes = json.load(f)
            return processes.get(str(crew_id))
    
    def save_process(self, crew_id: str, process_info: Dict[str, Any]) -> None:
        """Save process information"""
        self._ensure_process_file()
        with FileLock(self.lock_file):
            with open(self.process_file, 'r') as f:
                processes = json.load(f)
            processes[str(crew_id)] = process_info
            with open(self.process_file, 'w') as f:
                json.dump(processes, f)
    
    def remove_process(self, crew_id: str) -> None:
        """Remove process information"""
        self._ensure_process_file()
        with FileLock(self.lock_file):
            with open(self.process_file, 'r') as f:
                processes = json.load(f)
            processes.pop(str(crew_id), None)
            with open(self.process_file, 'w') as f:
                json.dump(processes, f)

class CrewAdmin(ModelAdmin):
    """Django admin interface for Crew management"""
    
    list_display = ('name', 'process', 'verbose', 'run_button', 'stop_button', 'status')
    filter_horizontal = ('agents', 'tasks')
    ordering = ('name',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.docker = DockerService(DockerConfig())
        self.tracker = ProcessTracker(settings.CREW_PROCESS_FILE)
    
    def run_button(self, obj):
        """Render run button"""
        return format_html(
            '<a class="button" href="{}" style="background-color: #28a745; '
            'color: white; padding: 5px 10px; text-decoration: none; '
            'border-radius: 4px;">Run</a>',
            reverse('admin:crewai_agents_crew_run_script', args=[obj.pk])
        )
    run_button.short_description = "Run Crew"
    
    def stop_button(self, obj):
        """Render stop button"""
        return format_html(
            '<a class="button" href="{}" style="background-color: #dc3545; '
            'color: white; padding: 5px 10px; text-decoration: none; '
            'border-radius: 4px;">Stop</a>',
            reverse('admin:crewai_agents_crew_stop_script', args=[obj.pk])
        )
    stop_button.short_description = "Stop Crew"
    
    def status(self, obj):
        """Display current status of the crew"""
        try:
            process = self.tracker.get_process(str(obj.pk))
            if process and self.docker.check_container(process['container_id']):
                return format_html(
                    '<span style="color: #28a745;">Running</span>'
                )
            return format_html(
                '<span style="color: #dc3545;">Stopped</span>'
            )
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            return format_html(
                '<span style="color: #dc3545;">Error</span>'
            )
    
    def _check_permissions(self, request) -> None:
        """Check user permissions"""
        if not request.user.is_authenticated or not request.user.is_staff:
            raise PermissionDenied("Staff access required")
    
    @transaction.atomic
    def run_script_view(self, request, crew_id):
        """Handle run script action"""
        try:
            self._check_permissions(request)
            
            # Get script path
            script_path = os.path.join(settings.BASE_DIR, 'crewai_agents', 'crew', 'main.py')
            if not os.path.exists(script_path):
                raise CrewError(f"Script not found: {script_path}")
            
            # Prepare environment
            env = {
                'PYTHONPATH': str(settings.BASE_DIR),
                'PYTHONUNBUFFERED': '1',
                'CREW_ID': str(crew_id)
            }
            
            # Start container
            container_id = self.docker.start_container(crew_id, script_path, env)
            
            # Save process info
            self.tracker.save_process(str(crew_id), {
                'container_id': container_id,
                'start_time': datetime.now().isoformat(),
                'script_path': script_path,
                'status': 'running'
            })
            
            messages.success(request, f"Crew {crew_id} started successfully!")
            
        except PermissionDenied as e:
            messages.error(request, str(e))
        except CrewError as e:
            logger.error(f"Error running crew {crew_id}: {e}")
            messages.error(request, f"Error starting crew: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error running crew {crew_id}: {e}", exc_info=True)
            messages.error(request, "An unexpected error occurred")
        
        return self.response_post_save_change(request, None)
    
    @transaction.atomic
    def stop_script_view(self, request, crew_id):
        """Handle stop script action"""
        try:
            self._check_permissions(request)
            
            process = self.tracker.get_process(str(crew_id))
            if not process:
                messages.info(request, f"No running process found for crew {crew_id}")
                return self.response_post_save_change(request, None)
            
            # Stop container
            self.docker.stop_container(process['container_id'])
            
            # Remove process tracking
            self.tracker.remove_process(str(crew_id))
            
            messages.success(request, f"Crew {crew_id} stopped successfully!")
            
        except PermissionDenied as e:
            messages.error(request, str(e))
        except CrewError as e:
            logger.error(f"Error stopping crew {crew_id}: {e}")
            messages.error(request, f"Error stopping crew: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error stopping crew {crew_id}: {e}", exc_info=True)
            messages.error(request, "An unexpected error occurred")
        
        return self.response_post_save_change(request, None)
    
    def get_urls(self):
        """Get admin URLs"""
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