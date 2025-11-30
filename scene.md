# C# LINQ Refactoring
```csharp @step1
var numbers = new List { 1, 2, 3, 4, 6 };
var filtered = numbers.Where(x => x > 2);
```
```@step2
Now we see how we need to filter it
```
```csharp @step3
var numbers = new List { 1, 2, 3, 4, 6 };
var result = numbers
    .Where(x => x > 2)
    .Select(x => x * 2);
```
```csharp @step4
var numbers = new List { 1, 2, 3, 4, 6 };
var result = numbers
    .Where(x => x > 2)
    .Select(x => x * 2)
    .ToList();
```