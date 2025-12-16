"""MPRIS integration for bass-senpai using playerctl."""
import subprocess
import json
from typing import Optional, Dict, Any


class MPRISClient:
    """Client for interacting with MPRIS via playerctl."""
    
    def __init__(self):
        self.playerctl_available = self._check_playerctl()
    
    def _check_playerctl(self) -> bool:
        """Check if playerctl is available."""
        try:
            subprocess.run(
                ["playerctl", "--version"],
                capture_output=True,
                timeout=2
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """Get current track metadata from MPRIS."""
        if not self.playerctl_available:
            return None
        
        try:
            # Get all metadata at once for efficiency
            result = subprocess.run(
                ["playerctl", "metadata", "--format", 
                 "{{artist}}|{{title}}|{{album}}|{{status}}|{{position}}|{{mpris:length}}|{{mpris:artUrl}}"],
                capture_output=True,
                text=True,
                timeout=1
            )
            
            if result.returncode != 0:
                return None
            
            output = result.stdout.strip()
            if not output:
                return None
            
            parts = output.split('|')
            if len(parts) < 7:
                return None
            
            artist, title, album, status, position, length, art_url = parts[:7]
            
            # Convert position and length from microseconds to seconds
            try:
                position_sec = int(position) / 1000000 if position else 0
                length_sec = int(length) / 1000000 if length else 0
            except (ValueError, ZeroDivisionError):
                position_sec = 0
                length_sec = 0
            
            return {
                'artist': artist or 'Unknown Artist',
                'title': title or 'Unknown Title',
                'album': album or 'Unknown Album',
                'status': status or 'Stopped',
                'position': position_sec,
                'length': length_sec,
                'art_url': art_url or None
            }
        
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            return None
    
    def get_playback_status(self) -> str:
        """Get current playback status."""
        if not self.playerctl_available:
            return "Stopped"
        
        try:
            result = subprocess.run(
                ["playerctl", "status"],
                capture_output=True,
                text=True,
                timeout=1
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            return "Stopped"
        
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            return "Stopped"
