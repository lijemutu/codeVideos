# Refactoring EF Core to Fix an N+1 Query

A common performance issue when using an ORM like Entity Framework Core is the "N+1 query" problem. This happens when you query for a list of entities (the "1" query) and then loop through them, triggering a new query for related data for each of the "N" entities.

Let's assume we have these two simple EF Core models for our examples:
```csharp
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

---
### The Problem: The N+1 Query

Here is a typical example of code that causes an N+1 query. We want to get all authors and print the title of one of their books.

```csharp @step1
// BAD: This causes an N+1 query.
var authors = context.Authors.ToList();

foreach (var author in authors)
{
    // This access to author.Books triggers a NEW query for EACH author!
    var firstBookTitle = author.Books.FirstOrDefault()?.Title ?? "No Books";
    Console.WriteLine($"- {author.Name} ({firstBookTitle})");
}
```

This code looks simple, but it's very inefficient. It executes:
1.  **One query** to fetch all authors (`context.Authors.ToList()`).
2.  **N additional queries** inside the loop, one for each author, to fetch their books (`author.Books`).

If you have 50 authors, this code runs 51 queries against your database.

---
### The Solution: Eager Loading

The fix is to tell EF Core to load the related data ahead of time in a single query. This is called "eager loading," and you do it with the `.Include()` method.

```csharp @step2
// GOOD: This executes a single query.
var authors = context.Authors
    .Include(author => author.Books) // Eagerly load books in the same query
    .ToList();

foreach (var author in authors)
{
    // NO query here! The book data is already in memory.
    var firstBookTitle = author.Books.FirstOrDefault()?.Title ?? "No Books";
    Console.WriteLine($"- {author.Name} ({firstBookTitle})");
}
```

By adding `.Include(author => author.Books)`, we instruct EF Core to generate a more complex SQL query that joins `Authors` and `Books` and fetches all the required data at once. The loop can then run without making any extra database calls, reducing 51 queries to just 1.
