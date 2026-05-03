## Tasks
### 1. In your own words, what does this function do?
Ans: This function create a new transaction of gold order for given customer with validating the balancing of customer account before update. If 

### 2. Identify at least four distinct problems with this implementation. Consider security, correctness, reliability, and maintainability.
Ans:
- 2.1. sql injection of sql execution
- 2.2. no input validation
- 2.3. no customer holding validation when order type is sell
- 2.4. no transaction safety

### 3. For each problem, explain why it matters — especially in a system that handles real financial transactions.
Ans:
- from 2.1. we should use sql paramter instread of string construction with passing the arguments. If I pass customer_id with "1 OR 1", the statement which is get customer balance will get the other customer balance and when update will update all record to the same balance. That will break the database.

- from 2.2. to prevent the sql injection we should validate the input argument of this function by check a type and value range

- from 2.3. In sell condition, there is no validate the quantity that customer holding. So I can spam sell the order even I do not have any gold and I will get a balance more.

- from 2.4. No transaction safety when execute sql. If execute update statement is pass but there are error such as OprationalError when execute insert statement, this should handle with rollback the transaction to prevent data integrity error.

### 4. Briefly propose a fix for each problem.
Ans:
- from 3.1. Every sql execution must change to be like
```
conn.execute( "UPDATE customers SET balance = ? WHERE id = ?", [new_balance, customer_id] )
```

- from 3.2. We can check a type by using assert statement, like
```
assert isinstance(customer_id, int)
assert isinstance(order_type, str)
assert isinstance(quantity, int)
assert isinstance(price, int)
```

- from 3.3. In this architecture we must compute a quantity of gold that customer holding by get all orders of given customer and process it. Then validate with given quantity if gold balance does not have enough, will return a failed response.

- from 3.4. Execute using transaction flow and handle when got error from execution by rollback this execute, then commit if pass.

