"""Album artwork handling with caching and Kitty protocol support."""
import os
import hashlib
import tempfile
import base64
from pathlib import Path
from typing import Optional, Tuple
import requests
from PIL import Image
from io import BytesIO


class ArtworkHandler:
    """Handles album artwork downloading, caching, and rendering."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize artwork handler with cache directory."""
        if cache_dir is None:
            cache_dir = Path.home() / ".cache" / "bass-senpai" / "artwork"
        
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.current_art_url = None
        self.current_cache_path = None
        self.is_kitty = self._detect_kitty()
    
    def _detect_kitty(self) -> bool:
        """Detect if running in Kitty terminal."""
        term = os.environ.get('TERM', '')
        return 'kitty' in term.lower()
    
    def _get_cache_path(self, art_url: str) -> Path:
        """Get cache file path for an artwork URL."""
        # Use hash of URL as filename
        url_hash = hashlib.md5(art_url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.jpg"
    
    def _download_artwork(self, art_url: str) -> Optional[Path]:
        """Download artwork from URL and save to cache."""
        try:
            # Handle file:// URLs
            if art_url.startswith('file://'):
                local_path = art_url[7:]
                cache_path = self._get_cache_path(art_url)
                
                # Copy local file to cache
                with open(local_path, 'rb') as src:
                    img = Image.open(src)
                    img = img.convert('RGB')
                    img.save(cache_path, 'JPEG', quality=85)
                
                return cache_path
            
            # Download from HTTP(S)
            response = requests.get(art_url, timeout=5)
            response.raise_for_status()
            
            cache_path = self._get_cache_path(art_url)
            
            # Save as JPEG
            img = Image.open(BytesIO(response.content))
            img = img.convert('RGB')
            img.save(cache_path, 'JPEG', quality=85)
            
            return cache_path
        
        except Exception as e:
            # Silently fail, will use fallback
            return None
    
    def get_artwork(self, art_url: Optional[str]) -> Optional[Path]:
        """Get artwork for the given URL, using cache if available."""
        if not art_url:
            self.current_art_url = None
            self.current_cache_path = None
            return None
        
        # Check if this is the same artwork as before
        if art_url == self.current_art_url and self.current_cache_path:
            if self.current_cache_path.exists():
                return self.current_cache_path
        
        # Update current URL
        self.current_art_url = art_url
        
        # Check cache first
        cache_path = self._get_cache_path(art_url)
        if cache_path.exists():
            self.current_cache_path = cache_path
            return cache_path
        
        # Download and cache
        downloaded = self._download_artwork(art_url)
        self.current_cache_path = downloaded
        return downloaded
    
    def render_kitty(self, image_path: Path, width: int = 40, height: int = 20) -> str:
        """Render image using Kitty graphics protocol."""
        try:
            # Load and resize image
            img = Image.open(image_path)
            img.thumbnail((width * 10, height * 20), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save to bytes
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode('ascii')
            
            # Kitty graphics protocol
            # Using chunked transmission for large images
            chunk_size = 4096
            chunks = [img_data[i:i+chunk_size] for i in range(0, len(img_data), chunk_size)]
            
            output = []
            for i, chunk in enumerate(chunks):
                if i == 0:
                    # First chunk - specify format and size
                    output.append(f"\x1b_Gf=100,a=T,m={(1 if i < len(chunks)-1 else 0)};{chunk}\x1b\\")
                elif i == len(chunks) - 1:
                    # Last chunk
                    output.append(f"\x1b_Gm=0;{chunk}\x1b\\")
                else:
                    # Middle chunks
                    output.append(f"\x1b_Gm=1;{chunk}\x1b\\")
            
            # Add newlines to move cursor down after image
            # The image will be displayed at current cursor position
            # We need to advance the cursor to account for the image height
            result = ''.join(output)
            # Text-art format has: 1 top border + height content + 1 bottom border = height+2 lines
            # For Kitty, we put the image on the first line, then add empty lines to match
            lines = [result]
            lines.extend([''] * (height + 1))  # height + 1 to match text-art's height + 2 total
            return '\n'.join(lines)
        
        except Exception as e:
            return ""
    
    def render_textart(self, image_path: Path, width: int = 40, height: int = 20) -> str:
        """Render image as colored text art using Unicode blocks."""
        try:
            # Load and resize image
            img = Image.open(image_path)
            img = img.resize((width, height * 2), Image.Resampling.LANCZOS)
            img = img.convert('RGB')
            
            pixels = img.load()
            output = []
            
            # Top border
            output.append('╔' + '═' * width + '╗')
            
            # Use half-block characters for better resolution
            for y in range(0, height * 2, 2):
                line = ['║']  # Left border
                for x in range(width):
                    # Get upper and lower pixel colors
                    r1, g1, b1 = pixels[x, y]
                    r2, g2, b2 = pixels[x, min(y + 1, height * 2 - 1)]
                    
                    # Use upper half block (▀) with appropriate colors
                    # Top half is foreground, bottom half is background
                    line.append(f"\x1b[38;2;{r1};{g1};{b1}m\x1b[48;2;{r2};{g2};{b2}m▀\x1b[0m")
                
                line.append('║')  # Right border
                output.append(''.join(line))
            
            # Bottom border
            output.append('╚' + '═' * width + '╝')
            
            return '\n'.join(output)
        
        except Exception as e:
            return ""
    
    def render(self, art_url: Optional[str], width: int = 40, height: int = 20) -> str:
        """Render artwork, automatically choosing best method."""
        artwork_path = self.get_artwork(art_url)
        
        if not artwork_path or not artwork_path.exists():
            # Return placeholder
            return self._render_placeholder(width, height)
        
        if self.is_kitty:
            result = self.render_kitty(artwork_path, width, height)
            if result:
                return result
        
        # Fallback to text art
        return self.render_textart(artwork_path, width, height)
    
    def _render_placeholder(self, width: int = 40, height: int = 20) -> str:
        """Render a placeholder when no artwork is available."""
        lines = []
        
        # Top border
        lines.append('╔' + '═' * width + '╗')
        
        # Middle lines with vertical borders
        for y in range(height):
            if y == height // 2:
                text = "No Artwork"
                padding = (width - len(text)) // 2
                content = ' ' * padding + text + ' ' * (width - padding - len(text))
                lines.append('║' + content + '║')
            else:
                lines.append('║' + ' ' * width + '║')
        
        # Bottom border
        lines.append('╚' + '═' * width + '╝')
        
        return '\n'.join(lines)
