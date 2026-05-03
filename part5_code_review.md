### Code review

#### Correctness issues
1. using decimal instead of float, because there might be case of 14999.99999999 or 15000.00000001 and then when check the cost and balance might be wrong and cause bug. Especially computation like price diff should change to decimal type and quantize it.

2. no input validation type and value which is price, quantity must be positive value

3. sell order type does not validate holding amount before update transaction.

4. customer id might not found in database, this should handle when get current balance of customer by check is customer valid first.

5. no checking market price is 0, this will cause division by 0 error raise. Validate the market price before compute.

#### security and data integrity
1. balance manipulation should in balance_lock statement. The balance that get before check order type might invalid from other thread processing. When checking the balance >= cost, the real balance might changed and it can cause negative balance value update to customer.

#### concurency
1. lock statement should lock in whole transaction in each order to prevent race condition of updating balance and order_log. Because if other thread has update in the same customer, balance might go wrong.

#### other improvement
1. in get_batch_summary function change from single line list conprehension to for loop of results instead, checking type of status to compute cost and revenue if it's filled type. (reduce from 4 loops to 1 loops)

2. change order dict to dataclass object to prevent missing require key in function and it will have a interface of order.

#### Before Merge

I would request changes for
- using Decimal instead of float
- adding input validation
- validating customer existence
- validating sell holdings
- fixing lock scope
- protecting order log updates
- and adding unit tests for invalid input, insufficient balance, insufficient holdings, unknown customer, and concurrent orders
