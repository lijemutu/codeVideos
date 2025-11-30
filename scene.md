# C# for loop
```csharp @step1
var rows = new List { 1, 2, 3, 4, 6 };
var filtered = numbers.Where(x => x > 2);
```
```csharp @step2
var numbers = new List { 1, 2, 3, 4, 6 };
var result = numbers
    .Where(x => x > 2)
    .Select(x => x * 2);
```
```csharp @step3
var numbers = new List { 1, 2, 3, 4, 6 };
var result = numbers
    .Where(x => x > 2)
    .Select(x => x * 2)
    .ToList();
```