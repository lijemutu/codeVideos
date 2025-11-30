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
            code = match.group(3).strip()
            
            step_match = re.search(r'@step(\d+)', annotations)
            highlight_match = re.search(r'@highlight\[(.*?)\]', annotations)
            transform_match = re.search(r'@transform\[(.*?)\]', annotations)
            isolate_match = re.search(r'@isolate\[(.*?)\]', annotations)
            
            code_blocks.append({
                'language': language,  # Can be None for plain text
                'code': code,
                'step': int(step_match.group(1)) if step_match else 0,
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
        # A more complete style map based on VS Code's "Dark+" theme
        # FIXED: Using color_to_rgb or direct hex colors that ManimGL understands
        style_map = {
            Token.Comment:                   "#6A9955",
            Token.Comment.Single:            "#6A9955",
            Token.Comment.Multiline:         "#6A9955",
            Token.Keyword:                   "#569CD6",
            Token.Keyword.Constant:          "#569CD6",
            Token.Keyword.Declaration:       "#569CD6",
            Token.Keyword.Namespace:         "#569CD6",
            Token.Keyword.Type:              "#569CD6",
            Token.Name:                      "#9CDCFE",
            Token.Name.Class:                "#4EC9B0",
            Token.Name.Function:             "#DCDCAA",
            Token.Name.Builtin:              "#569CD6",
            Token.Name.Variable:             "#9CDCFE",
            Token.Name.Attribute:            "#DCDCAA",
            Token.Name.Tag:                  "#569CD6",
            Token.Name.Decorator:            "#DCDCAA",
            Token.String:                    "#CE9178",
            Token.String.Double:             "#CE9178",
            Token.String.Single:             "#CE9178",
            Token.Number:                    "#B5CEA8",
            Token.Number.Integer:            "#B5CEA8",
            Token.Number.Float:              "#B5CEA8",
            Token.Operator:                  "#D4D4D4",
            Token.Operator.Word:             "#569CD6",
            Token.Punctuation:               "#D4D4D4",
            Token.Generic.Heading:           "#FFFFFF",
            Token.Generic.Subheading:        "#FFFFFF",
            Token.Generic.Emph:              "#D4D4D4",
            Token.Generic.Strong:            "#D4D4D4",
            Token.Error:                     "#F44747",
            Token.Text:                      "#D4D4D4",
        }

        # Common LINQ and C# extension methods to highlight
        linq_methods = {
            'Where', 'Select', 'SelectMany', 'OrderBy', 'OrderByDescending',
            'ThenBy', 'ThenByDescending', 'GroupBy', 'Join', 'GroupJoin',
            'First', 'FirstOrDefault', 'Last', 'LastOrDefault', 'Single',
            'SingleOrDefault', 'Any', 'All', 'Count', 'Sum', 'Average',
            'Min', 'Max', 'Take', 'Skip', 'TakeWhile', 'SkipWhile',
            'Distinct', 'Union', 'Intersect', 'Except', 'Concat',
            'Aggregate', 'ToList', 'ToArray', 'ToDictionary', 'ToLookup',
            'AsEnumerable', 'AsQueryable', 'Cast', 'OfType', 'Zip',
            'Contains', 'ElementAt', 'ElementAtOrDefault', 'DefaultIfEmpty',
            'Range', 'Repeat', 'Empty', 'Reverse'
        }

        def get_color_for_token(ttype, tvalue):
            """Get color for a token type, checking parent types if needed"""
            # Special handling for LINQ methods in C#
            if block['language'].lower() in ['csharp', 'c#', 'cs']:
                if tvalue in linq_methods:
                    return "#DCDCAA"  # Function color (yellow)
            
            # First check exact match
            if ttype in style_map:
                return style_map[ttype]
            
            # Walk up the token type hierarchy
            current = ttype
            while current.parent is not None:
                current = current.parent
                if current in style_map:
                    return style_map[current]
            
            # Default color
            return "#D4D4D4"

        code_mobs = []
        for block in code_blocks:
            # Check if this is plain text (no language specified)
            if not block['language']:
                # Create simple text display for plain text blocks
                text_lines = block['code'].split('\n')
                text_group = VGroup()
                
                for line in text_lines:
                    if line.strip():  # Skip empty lines
                        line_text = Text(line, font_size=font_size, color=WHITE)
                        text_group.add(line_text)
                
                text_group.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
                text_group.move_to(ORIGIN)
                code_mobs.append(text_group)
                continue
            
            # Process code blocks with syntax highlighting
            try:
                lexer = get_lexer_by_name(block['language'], stripall=True)
            except:
                lexer = get_lexer_by_name('text', stripall=True)

            tokens = list(lex(block['code'], lexer))
            
            # Debug: Print first few tokens to see what we're getting
            # print(f"\n=== Lexing {block['language']} code ===")
            for i, (ttype, tvalue) in enumerate(tokens[:15]):
                color = get_color_for_token(ttype, tvalue)
                # print(f"Token {i}: {ttype} = '{tvalue}' -> color: {color}")
            
            lines = VGroup()
            current_line = VGroup()

            for ttype, tvalue in tokens:
                # Get the appropriate color for this token
                color = get_color_for_token(ttype, tvalue)

                if "\n" in tvalue:
                    parts = tvalue.split("\n")
                    for i, part in enumerate(parts):
                        if part:
                            # FIXED: Ensure color is applied correctly
                            text_mob = Text(part, font="Monospace", font_size=font_size)
                            text_mob.set_color(color)
                            current_line.add(text_mob)
                        if i < len(parts) - 1:
                            if len(current_line.submobjects) > 0:
                                current_line.arrange(RIGHT, buff=0.08, aligned_edge=DOWN)
                            lines.add(current_line)
                            current_line = VGroup()
                else:
                    if tvalue:
                        # FIXED: Ensure color is applied correctly
                        text_mob = Text(tvalue, font="Monospace", font_size=font_size)
                        text_mob.set_color(color)
                        current_line.add(text_mob)

            if len(current_line.submobjects) > 0:
                current_line.arrange(RIGHT, buff=0.08, aligned_edge=DOWN)
            lines.add(current_line)
            
            code = lines.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
            code.move_to(ORIGIN)
            code_mobs.append(code)
        
        # Animate the code blocks
        if code_mobs:
            current_code = code_mobs[0]
            self.play(Write(current_code))
            self.wait(1.5)
            
            for next_code in code_mobs[1:]:
                self.play(ReplacementTransform(current_code, next_code), run_time=1.5)
                self.wait(1.5)
                current_code = next_code
            
            if title_mob:
                self.play(FadeOut(current_code), FadeOut(title_mob))
            else:
                self.play(FadeOut(current_code))