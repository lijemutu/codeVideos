"""
Manim Code Transform Animation Generator
Works with both ManimCE and ManimGL
Parses markdown files with annotations to create code transformation animations
"""

import re
import os
import sys
from typing import List, Dict, Optional
from pathlib import Path
from manimlib import *


class MarkdownCodeParser:
    """Parses markdown files with special annotations for code transformations"""
    
    @staticmethod
    def parse_markdown(content: str) -> List[Dict]:
        """
        Parse markdown content with code blocks annotated with transformation metadata
        
        Expected format:
        ```csharp @step1 @highlight[var,result]
        var result = list.Where(x => x > 0);
        ```
        """
        code_blocks = []
        pattern = r'```(\w+)\s+(.*?)\n(.*?)```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            language = match.group(1)
            annotations = match.group(2)
            code = match.group(3).strip()
            
            step_match = re.search(r'@step(\d+)', annotations)
            highlight_match = re.search(r'@highlight\[(.*?)\]', annotations)
            transform_match = re.search(r'@transform\[(.*?)\]', annotations)
            isolate_match = re.search(r'@isolate\[(.*?)\]', annotations)
            
            code_blocks.append({
                'language': language,
                'code': code,
                'step': int(step_match.group(1)) if step_match else 0,
                'highlights': highlight_match.group(1).split(',') if highlight_match else [],
                'transforms': dict(t.split('->') for t in transform_match.group(1).split(',')) if transform_match else {},
                'isolate': isolate_match.group(1).split(',') if isolate_match else []
            })
        
        return sorted(code_blocks, key=lambda x: x['step'])


class MarkdownCodeScene(Scene):
    """Scene that loads and animates code from a markdown file"""
    
    def __init__(self, markdown_path: Optional[str] = None, **kwargs):
        """
        Initialize the scene with a markdown file path
        
        Args:
            markdown_path: Path to the markdown file (absolute or relative)
            **kwargs: Additional arguments passed to Scene
        """
        self.markdown_path = markdown_path
        super().__init__(**kwargs)
    
    def load_markdown_file(self, file_path: str) -> Optional[str]:
        """
        Load markdown content from various possible locations
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Markdown content as string, or None if not found
        """
        # Try multiple locations
        search_paths = [
            file_path,  # Exact path provided
            os.path.abspath(file_path),  # Absolute path
            os.path.join(os.getcwd(), file_path),  # Current working directory
            os.path.join(os.path.dirname(__file__), file_path),  # Same directory as script
            os.path.expanduser(file_path),  # Expand ~ for home directory
        ]
        
        for path in search_paths:
            try:
                if os.path.isfile(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        return f.read()
            except (OSError, IOError):
                continue
        
        return None
    
    def construct(self):
        # Determine which markdown file to use
        # Check for command-line argument
        if len(sys.argv) > 1:
            markdown_file = sys.argv[3]
        
        # Load the markdown content
        markdown_content = self.load_markdown_file(markdown_file)
        
        if markdown_content is None:
            error = Text(
                f"File not found: {markdown_file}\nSearched in:\n- Current directory\n- Script directory\n- Absolute path",
                color=RED,
                font_size=20
            )
            error.move_to(ORIGIN)
            self.play(Write(error))
            self.wait(3)
            return
        
        # Parse the markdown
        parser = MarkdownCodeParser()
        code_blocks = parser.parse_markdown(markdown_content)
        
        if not code_blocks:
            error = Text("No code blocks found in markdown", color=RED, font_size=24)
            self.play(Write(error))
            self.wait(2)
            return
        
        # Create text mobjects for each code block
        code_mobs = []
        for block in code_blocks:
            code = Text(
                block['code'],
                font="Monospace",
                font_size=24,
                color=WHITE
            )
            code.move_to(ORIGIN)
            code_mobs.append(code)
        
        # Animate the code blocks
        if code_mobs:
            self.play(FadeIn(code_mobs[0]))
            self.wait(1)
            
            for i in range(len(code_mobs) - 1):
                self.play(Transform(code_mobs[0], code_mobs[i + 1]), run_time=2)
                self.wait(1)
            
            self.play(FadeOut(code_mobs[0]))
