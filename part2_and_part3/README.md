### How to run
Main file is `order_validation.py` run by
```
python3 order_validation.py 1 buy 0.5 70000
```
command `python3 order_validation.py <customer_id> <order_type> <quantity> <quoted_price>` Argument passing is
- customer_id: id of customer (eg. 1, 2, 3,..)
- order_type: type of order, should be buy or sell
- quantity: quantity of making order, must be increment of 0.5
- quoted_price: price when make order

in this file has define mock data and value in mock db class.

For unittest run by
```
python3 -m unittest tests.test_order_validation
```
