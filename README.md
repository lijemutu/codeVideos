# Manim Code Animator

## Overview
This project leverages Manim (specifically `manimlib`/ManimGL) to generate sophisticated code transformation and explanation animations directly from a simple markdown file. It provides a declarative way to create animated presentations of code refactoring, tutorials, and technical explanations with minimal effort.

## Features
-   **Animate Code Blocks:** Transforms code snippets defined in markdown files into Manim animations.
-   **Syntax Highlighting:** Automatically applies rich syntax highlighting to code blocks for a wide variety of programming languages.
-   **Scene Titles:** Parses the first H1 header (`# Your Scene Title`) from your markdown file and displays it as the animation's scene title.
-   **Text-Only Slides:** Supports creating slides with plain text explanations alongside or instead of code.
-   **Customizable Pacing:** Control the duration each slide stays on screen.
-   **Flexible Transitions:** Choose between performant cross-fades, dynamic code transformations, or a "typing" effect for how slides appear.

## Prerequisites
To run this project, you will need:
-   **Python 3.7+**
-   **Manim (ManimGL/manimlib)**: Follow the installation instructions for `manimlib`.
-   **Pygments**: Used for syntax highlighting. Install via pip:
    ```bash
    pip install Pygments
    ```

## How to Use

### 1. Create Your Markdown Animation File
Create a new markdown file (e.g., `my_animation.md`) that defines your animation's slides, code, and explanations.

### 2. Markdown File Format
Your markdown file should follow this structure:

#### Scene Title
The very first H1 header in your file will be used as the title for your Manim scene.
```markdown
# My Awesome Code Explanation
```

#### Slides
Each "slide" in your animation (whether it's a code snippet or a block of explanatory text) must be enclosed within a standard markdown code block (```` ``` ````).

#### Annotations
Add special attributes to the header line of each code block to control its behavior and animation. All annotations must be on the same line as the opening ` ``` `.

-   `@step<number>`: **(Required)** Specifies the order of the slide in the animation. E.g., `@step1`, `@step2`.
-   `@wait[<seconds>]`: **(Optional)** Defines how long the animation will pause after this slide appears. Defaults to `1.5` seconds if not specified. E.g., `@wait[3.0]`.
-   `@write`: **(Optional)** If present, this slide will appear using the `Write` animation (like being typed out).
-   `@transform`: **(Optional)** If present, the transition *to* this slide will use a `ReplacementTransform` animation, morphing the previous slide into the current one.
    -   **Precedence**: `@write` takes precedence over `@transform`. If both are present, `@write` will be used. If neither are present, the default is a fast cross-fade (`FadeOut`/`FadeIn`).

#### Code Slides
To display syntax-highlighted code, specify the programming language immediately after the opening backticks.
```markdown
```csharp @step1 @write @wait[4]
// Your C# code here
var example = "Hello, Manim!";
```

#### Text-Only Slides
To display a block of plain text as a slide (e.g., for explanations), simply omit the language specifier.
```markdown
``` @step2 @wait[3]
This is an explanation slide.
It supports multiple lines of text.
It will appear with a larger font size.
```

### 3. Running the Animation
Once your markdown file is ready, you can generate your Manim animation using the following command in your terminal:

```bash
manimgl manim.py MarkdownCodeScene .\my_animation.md
```
Replace `my_animation.md` with the path to your markdown file.

## Example
Here is an example of a markdown file (`efcore_refactor.md`) that demonstrates various features:
```markdown
# Refactoring EF Core to Fix an N+1 Query

```csharp @step1
// Intro: The N+1 Query Problem in EF Core
// We want to fetch Authors and their Books.
// Let's assume these EF Core models:
public class Author
{
    public int Id { get; set; }
    public string Name { get; set; }
    public List<Book> Books { get; set; } = new();
}

public class Book
{
    public int Id { get; set; }
    public string Title { get; set; }
    public int AuthorId { get; set; }
    public Author Author { get; set; }
}
```

``` @step2
// Understanding the N+1 Problem
The "N+1 query" problem happens when you make one query to get a list of items (the "1"),
and then make N additional queries to fetch related data for each of those N items.
This is very inefficient and can severely degrade performance.
```

```csharp @step3
// BAD: The N+1 Problem in action
// This code looks simple, but it's a performance trap.
var authors = context.Authors.ToList(); // 1 query to get all authors

foreach (var author in authors)
{
    // This line triggers a NEW database query for EACH author!
    var firstBookTitle = author.Books.FirstOrDefault()?.Title ?? "No Books";
    Console.WriteLine($"- {author.Name} ({firstBookTitle})");
}
```

``` @step4 @wait[3]
// Why this is bad
If you have 50 authors, this code runs:
1 query for all authors
+ 50 queries (1 for each author's books)
= 51 total database queries!
This can easily overwhelm your database.
```

```csharp @step5 @transform
// GOOD: The Solution with Eager Loading (Include())
// We tell EF Core to fetch related data in a single, efficient query.
var authors = context.Authors
    .Include(author => author.Books) // Eagerly load books with authors
    .ToList(); // Only 1 query to get authors AND their books

foreach (var author in authors)
{
    // NO query here! The book data is already in memory.
    var firstBookTitle = author.Books.FirstOrDefault()?.Title ?? "No Books";
    Console.WriteLine($"- {author.Name} ({firstBookTitle})");
}
```

``` @step6 @wait[4]
// The Benefit
By using `.Include()`, we reduce 51 queries down to just 1.
This significantly improves performance by minimizing database round-trips.
Always consider eager loading related data when you know you'll need it.
```
