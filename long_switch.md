# The Long Switch: A Refactoring Story

``` @step1 @write @wait[2]
Our developer gets a new ticket.
"Task: Add 'GiftCard' as a new payment method."
```

``` @step1 @transform @wait[2]
Sounds simple enough.
They open the `PaymentProcessor` file and find... this.
```

``` @step1 @transform @wait[2]
A wild switch statement appears!
```

```csharp @step2 @wait[6]
public decimal CalculateFee(Order order)
{
    decimal fee = 0;
    switch (order.PaymentMethod)
    {
        case "CreditCard":
            fee = order.Amount * 0.025m + 0.30m;
            break;
        case "PayPal":
            fee = order.Amount * 0.03m;
            if (order.IsInternational) fee += order.Amount * 0.015m;
            break;
            // ... Google, applepay, banktransfer ...
    }
    return fee;
}
```

``` @step3 @write @wait[3]
To add the new 'GiftCard' method,
the developer has to carefully scroll and find the right place to add a new 'case'.
```

``` @step3 @transform @wait[2]
The method gets longer. The risk of breaking something grows.
This feels wrong.
```

``` @step3 @transform @wait[2]
Just one more case... what's the harm?
```

```csharp @step4 @write @wait[5] @fontsize[21]
public decimal CalculateFee(Order order)
{
    decimal fee = 0;
    switch (order.PaymentMethod)
    {
        case "CreditCard":
            fee = order.Amount * 0.025m + 0.30m;
            break;
        case "PayPal":
            fee = order.Amount * 0.03m;
            if (order.IsInternational) fee += order.Amount * 0.015m;
            break;
        // ... other cases ...
        case "GiftCard": // The new case is added at the end
            fee = 0; // No fee for gift cards
            break;
    }
    return fee;
}
```

``` @step5 @write @wait[3]
The "quick fix" worked, but the code is now harder to read and maintain.
The developer knows this isn't sustainable. They decide to refactor.
```

``` @step5 @write @wait[3]
The goal: Make the code open for extension, but closed for modification.
A Dictionary-based Strategy Pattern is perfect for this.
```

```csharp @step6 @write  @wait[7] @fontsize[20]
private static readonly Dictionary<string, Func<Order, decimal>> _feeCalculators =
    new Dictionary<string, Func<Order, decimal>>
    {
        { "CreditCard",   order => order.Amount * 0.025m + 0.30m },
        { "PayPal",       order => {
            var fee = order.Amount * 0.03m;
            if (order.IsInternational) fee += order.Amount * 0.015m;
            return fee;
        }},
        { "Stripe",       order => order.Amount * 0.029m + 0.25m },
        { "ApplePay",     order => order.Amount * 0.025m + 0.30m },
        { "GooglePay",    order => order.Amount * 0.025m + 0.25m },
        { "BankTransfer", order => 5.00m },
        { "Crypto",       order => order.Amount * 0.01m },
        { "GiftCard",     order => 0 },
    };
```
``` @step5 @write @wait[3]
Then call it in CaclulateFee method
```

```csharp @step7 @write  @wait[6]
public decimal CalculateFee(Order order)
{
    if (_feeCalculators.TryGetValue(order.PaymentMethod, out var calculateFee))
    {
        return calculateFee(order);
    }

    throw new NotSupportedException("Payment method not supported.");
}
```

``` @step8 @write @wait[2]
Look at that! Clean, readable, and maintainable.
```
``` @step8 @write @wait[3]

To add a new payment method now, the developer only needs to add one line to the dictionary.
No more scary switch statements!
```
``` @step8 @write

The struggle was worth it.
```