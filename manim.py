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
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token


class MarkdownCodeParser:
    """Parses markdown files with special annotations for code transformations"""
    
    @staticmethod
    def parse_markdown(content: str) -> Dict:
        """
        Parse markdown content with code blocks and an optional title.
        
        Expected format:
        # My Awesome Title
        ```csharp @step1 @highlight[var,result]
        var result = list.Where(x => x > 0);
        ```
        ```@step2
        Plain text explanation here
        ```
        """
        title_match = re.search(r"^#\s+(.*)", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else None
        
        code_blocks = []
        # Updated pattern to make language optional
        pattern = r'```(\w*)\s*(.*?)\n(.*?)```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            language = match.group(1) if match.group(1) else None
            annotations = match.group(2)
            code = match.group(3).lstrip('\n').rstrip('\n')
            
            step_match = re.search(r'@step(\d+)', annotations)
            highlight_match = re.search(r'@highlight\[(.*?)\]', annotations)
            transform_match = re.search(r'@transform\[(.*?)\]', annotations)
            isolate_match = re.search(r'@isolate\[(.*?)\]', annotations)
            wait_match = re.search(r'@wait\[([\d.]+)\]', annotations)
            transform_flag = re.search(r'@transform', annotations)
            write_flag = re.search(r'@write', annotations)
            fontsize_match = re.search(r'@fontsize\[(\d+)\]', annotations)
            
            code_blocks.append({
                'language': language,  # Can be None for plain text
                'code': code,
                'step': int(step_match.group(1)) if step_match else 0,
                'wait': float(wait_match.group(1)) if wait_match else 1.5,
                'use_transform': bool(transform_flag),
                'use_write': bool(write_flag),
                'fontsize': int(fontsize_match.group(1)) if fontsize_match else 24,
                'highlights': highlight_match.group(1).split(',') if highlight_match else [],
                'transforms': dict(t.split('->') for t in transform_match.group(1).split(',')) if transform_match else {},
                'isolate': isolate_match.group(1).split(',') if isolate_match else []
            })
        
        return {"title": title, "code_blocks": sorted(code_blocks, key=lambda x: x['step'])}


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
        parsed_data = parser.parse_markdown(markdown_content)
        title = parsed_data.get("title")
        code_blocks = parsed_data.get("code_blocks", [])
        
        title_mob = None
        if title:
            title_mob = Text(title).to_edge(UP)
            self.play(Write(title_mob))
        
        if not code_blocks:
            error = Text("No code blocks found in markdown", color=RED, font_size=24)
            self.play(Write(error))
            self.wait(2)
            return
        
        # Manually create syntax-highlighted code from basic Text objects
        font_size = 24
        
        code_mobs = []
        for block in code_blocks:
            # Get fontsize for this specific block, defaulting to 24
            font_size = block.get('fontsize', 24)

            # Conditional rendering based on whether a language is specified
            if not block['language']:
                # It's a text-only slide
                text_mobject = Text(
                    block['code'],
                    font_size=font_size,
                    color=WHITE
                )
                text_mobject.move_to(ORIGIN)
                code_mobs.append(text_mobject)
                continue
            
            # Use Code class which handles lexing, tokenizing, and syntax highlighting internally
            try:
                code_obj = Code(
                    block['code'],
                    language=block['language'],
                    font="Consolas",
                    font_size=font_size,
                    code_style="monokai"
                )
                code_obj.move_to(ORIGIN)
                code_mobs.append(code_obj)
            except Exception as e:
                print(f"Error creating Code object: {e}")
                # Fallback to plain text if Code fails
                text_mobject = Text(
                    block['code'],
                    font_size=font_size,
                    color=WHITE
                )
                text_mobject.move_to(ORIGIN)
                code_mobs.append(text_mobject)
        
        # Animate the code blocks
        if code_mobs:
            # Animate the first slide's appearance
            current_code = code_mobs[0]
            if code_blocks[0].get('use_write', False):
                self.play(Write(current_code), run_time=2)
            else:
                self.play(FadeIn(current_code)) # Default to FadeIn
            self.wait(code_blocks[0].get('wait', 1.5))

            # Animate transitions for subsequent slides
            for i in range(1, len(code_mobs)):
                next_code = code_mobs[i]
                
                # Check for @write first (highest priority)
                if code_blocks[i].get('use_write', False):
                    self.play(FadeOut(current_code))
                    self.play(Write(next_code), run_time=2)
                
                # Then check for @transform
                elif code_blocks[i].get('use_transform', False):
                    self.play(ReplacementTransform(current_code, next_code), run_time=1.5)
                
                # Default to cross-fade
                else:
                    self.play(FadeOut(current_code), FadeIn(next_code), run_time=0.75)
                
                # Wait for the duration specified for the new slide
                self.wait(code_blocks[i].get('wait', 1.5))

                current_code = next_code
            
            # Fade out the final slide
            if title_mob:
                self.play(FadeOut(current_code), FadeOut(title_mob))
            else:
                self.play(FadeOut(current_code))
                
                
class InlineMarkdownExample(MarkdownCodeScene):
    """Example scene with inline markdown content"""
    
    def construct(self):
        markdown_content = """
# C# LINQ Refactoring
```csharp @step1
var numbers = new List<int> { 1, 2, 3, 4, 5 };
var filtered = numbers.Where(x => x > 2);
```

```csharp @step2
var numbers = new List<int> { 1, 2, 3, 4, 5 };
var result = numbers
    .Where(x => x > 2)
    .Select(x => x * 2);
```

```csharp @step3
var numbers = new List<int> { 1, 2, 3, 4, 5 };
var result = numbers
    .Where(x => x > 2)
    .Select(x => x * 2)
    .ToList();
```
"""
        parser = MarkdownCodeParser()
        parsed_data = parser.parse_markdown(markdown_content)
        
        title = parsed_data['title']
        code_blocks = parsed_data['code_blocks']
        
        # Display title if present
        if title:
            title_mob = Text(title, font_size=36, color=BLUE)
            title_mob.to_edge(UP)
            self.play(Write(title_mob))
            self.wait(1)
        
        # Create and animate code mobjects
        code_mobs = [Text(block['code'], font="Monospace", font_size=24, color=WHITE) 
                     for block in code_blocks]
        
        for mob in code_mobs:
            if title:
                mob.next_to(title_mob, DOWN, buff=0.5)
            else:
                mob.move_to(ORIGIN)
        
        self.play(FadeIn(code_mobs[0]))
        self.wait(1)
        
        for i in range(len(code_mobs) - 1):
            self.play(Transform(code_mobs[0], code_mobs[i + 1]), run_time=2)
            self.wait(1)
        
        # Fade out everything
        if title:
            self.play(FadeOut(code_mobs[0]), FadeOut(title_mob))
        else:
            self.play(FadeOut(code_mobs[0]))
