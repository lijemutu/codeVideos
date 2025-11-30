# Refactoring EF Core to Fix an N+1 Query

```csharp @step1
public class Author
{
    public int Id { get; set; }
    public string Name { get; set; }
    public List<Book> Books { get; set; } = new();
}
```
```csharp @step1
public class Book
{
    public int Id { get; set; }
    public string Title { get; set; }
    public int AuthorId { get; set; }
    public Author Author { get; set; }
}
```

``` @step2
The "N+1 query" problem happens when you make one query to get a list of items (the "1")
```
``` @step2
and then make N additional queries to fetch related data for each of those N items.
```
``` @step2
This is very inefficient and can severely degrade performance.
```

```csharp @step3
var authors = context.Authors.ToList();

foreach (var author in authors)
{
    var firstBookTitle = author.Books.FirstOrDefault()?.Title ?? "No Books";
    Console.WriteLine($"- {author.Name} ({firstBookTitle})");
}
```

``` @step4
If you have 50 authors, this code runs:
```

``` @step4
1 query for all authors
+ 50 queries (1 for each author's books)
= 51 total database queries!
```

``` @step4
This can easily overwhelm your database.
```

```csharp @step5
var authors = context.Authors
    .Include(author => author.Books) 
    .ToList(); 

foreach (var author in authors)
{
    var firstBookTitle = author.Books.FirstOrDefault()?.Title ?? "No Books";
    Console.WriteLine($"- {author.Name} ({firstBookTitle})");
}
```

``` @step6
By using `.Include()`, we reduce 51 queries down to just 1.
```

``` @step6
This significantly improves performance by minimizing database round-trips.
```

``` @step6
Always consider eager loading related data when you know you'll need it.
```