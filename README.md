### Assignment
This repository contains 5 parts of assignment. For part 1, 4, and 5 is .md files. For part 2 and 3 is in folder `part2_and_part3`.

For run and execute part 2 and part 3 you can to go to directory and run with step in README.md in folder.

Alternative way is run in this directory by export PYTHONPATH first

```
export PYTHONPATH=`pwd`/part2_and_part3:$PYTHONPATH
```

and run by 

```
python3 part2_and_part3/order_validation.py 1 buy 0.5 70000
```

command `python3 part2_and_part3/order_validation.py <customer_id> <order_type> <quantity> <quoted_price>` Argument passing is
- customer_id: id of customer (eg. 1, 2, 3,..)
- order_type: type of order, should be buy or sell
- quantity: quantity of making order, must be increment of 0.5
- quoted_price: price when make order

and unittest run by
```
python3 -m unittest part2_and_part3.tests.test_order_validation
```
