##############################
#
# Standart Import
#
from decimal import Decimal
import unittest
from unittest.mock import Mock

##############################
#
# Local Import
#
from order_validation import (
    TOLERANCE_ORDER_AMOUNT,
    OrderValidator,
    ORDER_TYPE_BUY,
    ORDER_TYPE_SELL,
    MARGIN,
)

##############################
#
# Class
#
class TestOrderValidator( unittest.TestCase ):

    def setUp( self ):
        ''' setup test case with mock the test db
            and construct validator object for test
        '''
        super().setUp()

        # mock db
        self.mock_test_db = Mock()
        self.mock_test_db.get_customer_info = Mock()
        self.mock_test_db.get_market_price = Mock()
        self.mock_test_db.get_customer_balance = Mock()
        self.mock_test_db.get_holding_quantity = Mock()
        self.mock_test_db.get_orders = Mock()

        self.setup_mock_customer()

        # construct validator
        self.validator = OrderValidator(self.mock_test_db, MARGIN)

    def setup_mock_customer( self ):
        ''' setup mock customer data in function get_customer_info
        '''
        self.mock_test_db.get_customer_info.return_value = {
            'id': 1,
            'name': 'Alice',
        }

    def test_validate_buy_order_success( self ):
        ''' test validate function in case success proceed buy order

            expected result status should be passed
                buy order spread amount must be computed with market price * margin
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        # define input argument to test function
        customer_id = 1
        order_type = ORDER_TYPE_BUY
        quantity = 1
        quoted_price = 72420

        # call test function
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        # check status should be passed
        self.assertEqual( result[ 'status' ], 'passed' )
        spread_amount = Decimal( '71000.00' ) * MARGIN
        self.assertEqual( result[ 'spread_amount' ], spread_amount.quantize( Decimal( '0.01' ) ) )

    def test_validate_sell_order_success( self ):
        ''' test validate function in case success proceed sell order

            expected result status should be passed
                sell order spread amount must be 0.00
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        # define input argument to test function
        customer_id = 1
        order_type = ORDER_TYPE_SELL
        quantity = 1
        quoted_price = 71000

        # call test function
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        # check status should be passed
        self.assertEqual( result[ 'status' ], 'passed' )
        spread_amount = Decimal( '0' )
        self.assertEqual( result[ 'spread_amount' ], spread_amount.quantize( Decimal( '0.01' ) ) )

    def test_validate_invalid_order_type( self ):
        ''' test validate function in case failed proceed invalid order type

            expected result status should be failed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        # define input argument to test function
        customer_id = 1
        order_type = 'invalid'
        quantity = 1
        quoted_price = 71000

        # call test function
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        # check status should be failed
        self.assertEqual( result[ 'status' ], 'failed' )
        self.assertIn( 'Unsupported order type', result[ 'reason' ] )

    def test_validate_quantity_must_be_number( self ):
        ''' test validate function in case failed proceed
            with type assertions quantity

            expected result status should be failed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        customer_id = 1
        order_type = ORDER_TYPE_BUY
        quantity = 'abc'
        quoted_price = 71000
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        self.assertEqual( result[ 'status' ], 'failed' )
        self.assertIn( 'quantity must be a number', result[ 'reason' ] )

    def test_validate_price_must_be_number( self ):
        ''' test validate function in case failed proceed
            with type assertions price

            expected result status should be failed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        customer_id = 1
        order_type = ORDER_TYPE_BUY
        quantity = 1
        quoted_price = 'abc'
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        self.assertEqual( result[ 'status' ], 'failed' )
        self.assertIn( 'price must be a number', result[ 'reason' ] )

    def test_validate_quantity_must_be_positive( self ):
        ''' test validate function in case failed proceed
            with quantity must be positive value

            expected result status should be failed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        customer_id = 1
        order_type = ORDER_TYPE_BUY
        quantity = -1
        quoted_price = 72420
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        self.assertEqual( result[ 'status' ], 'failed' )
        self.assertIn( 'quantity must be a positive', result[ 'reason' ] )

    def test_validate_price_must_be_positive( self ):
        ''' test validate function in case failed proceed
            with price must be positive value

            expected result status should be failed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        customer_id = 1
        order_type = ORDER_TYPE_BUY
        quantity = 1
        quoted_price = -72420
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        self.assertEqual( result[ 'status' ], 'failed' )
        self.assertIn( 'price must be a positive', result[ 'reason' ] )

    def test_validate_customer_id_must_be_int( self ):
        ''' test validate function in case failed proceed
            with customer_id must be integer

            expected result status should be failed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        result = self.validator.order_validation(
            customer_id='1',
            order_type=ORDER_TYPE_BUY,
            quantity=1,
            quoted_price=72420,
        )

        self.assertEqual( result[ 'status' ], 'failed' )
        self.assertIn( 'Unsupported customer id type', result[ 'reason' ] )

    def test_validate_customer_not_found( self ):
        ''' test validate function in case failed proceed
            with not found customer in db

            expected result status should be failed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        # mock no customer found
        self.mock_test_db.get_customer_info.return_value = None

        customer_id = 999
        order_type = ORDER_TYPE_BUY
        quantity = 1
        quoted_price = 72420
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        self.assertEqual( result[ 'status' ], 'failed' )
        self.assertIn( 'Not found customer id', result[ 'reason' ] )

    def test_validate_quantity_increment_of_half( self ):
        ''' test validate function in case failed proceed
            with increment of quantity does not be 0.5

            expected result status should be failed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        customer_id = 1
        order_type = ORDER_TYPE_BUY
        quantity = 1.3
        quoted_price = 72420
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        self.assertEqual( result[ 'status' ], 'failed' )
        self.assertIn( '0.5', result[ 'reason' ] )

    def test_validate_buy_price_with_spread_out_of_range( self ):
        ''' test validate function in case failed proceed
            with outside of spread range

            spread amount = 71000 * MARGIN
            so buy range will be ( market + spread ) * ( 1 - TOLERANCE ) and ( market + spread ) * ( 1 + TOLERANCE )

            expected result status should be failed
        '''
        market_price = Decimal( '71000.00' )
        spreaded_market_price = market_price * ( 1 + MARGIN )

        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = market_price

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        # lower bound
        with self.subTest( 'quoted price is spreaded_market_price * ( 1 - TOLERANCE_ORDER_AMOUNT ) (still pass)'):

            customer_id = 1
            order_type = ORDER_TYPE_BUY
            quantity = 1
            quoted_price = float( ( spreaded_market_price * ( 1 - TOLERANCE_ORDER_AMOUNT ) ).quantize( Decimal( '0.01' ) ) )
            result = self.validator.order_validation(
                customer_id,
                order_type,
                quantity,
                quoted_price,
            )

            self.assertEqual( result[ 'status' ], 'passed' )
            spread_amount = Decimal( '71000.00' ) * MARGIN
        self.assertEqual( result[ 'spread_amount' ], spread_amount.quantize( Decimal( '0.01' ) ) )

        # lower bound
        with self.subTest( 'quoted price is spreaded_market_price * ( 1 - TOLERANCE_ORDER_AMOUNT ) - 0.01 (failed exceed)'):

            customer_id = 1
            order_type = ORDER_TYPE_BUY
            quantity = 1
            quoted_price = float( ( spreaded_market_price * ( 1 - TOLERANCE_ORDER_AMOUNT ) ).quantize( Decimal( '0.01' ) ) - Decimal( '0.01' ) )
            result = self.validator.order_validation(
                customer_id,
                order_type,
                quantity,
                quoted_price,
            )

            self.assertEqual( result[ 'status' ], 'failed' )
            self.assertIn( 'Price freshness error', result[ 'reason' ] )
        
        # upper bound
        with self.subTest( 'quoted price is spreaded_market_price * ( 1 + TOLERANCE_ORDER_AMOUNT ) (still pass)'):

            customer_id = 1
            order_type = ORDER_TYPE_BUY
            quantity = 1
            quoted_price = float( ( spreaded_market_price * ( 1 + TOLERANCE_ORDER_AMOUNT ) ).quantize( Decimal( '0.01' ) ) )
            result = self.validator.order_validation(
                customer_id,
                order_type,
                quantity,
                quoted_price,
            )

            self.assertEqual( result[ 'status' ], 'passed' )
            spread_amount = Decimal( '71000.00' ) * MARGIN
        self.assertEqual( result[ 'spread_amount' ], spread_amount.quantize( Decimal( '0.01' ) ) )

        # upper bound
        with self.subTest( 'quoted price is spreaded_market_price * ( 1 + TOLERANCE_ORDER_AMOUNT ) + 0.01 (failed exceed)'):

            customer_id = 1
            order_type = ORDER_TYPE_BUY
            quantity = 1
            quoted_price = float( ( spreaded_market_price * ( 1 + TOLERANCE_ORDER_AMOUNT ) ).quantize( Decimal( '0.01' ) ) + Decimal( '0.01' ) )
            result = self.validator.order_validation(
                customer_id,
                order_type,
                quantity,
                quoted_price,
            )

            self.assertEqual( result[ 'status' ], 'failed' )
            self.assertIn( 'Price freshness error', result[ 'reason' ] )

        # in range
        with self.subTest( 'quoted price is spreaded_market_price * ( 1 + TOLERANCE_ORDER_AMOUNT ) (still pass)'):

            customer_id = 1
            order_type = ORDER_TYPE_BUY
            quantity = 1
            quoted_price = float( ( spreaded_market_price * ( 1 + ( TOLERANCE_ORDER_AMOUNT / Decimal( '2' ) ) ) ).quantize( Decimal( '0.01' ) ) )
            result = self.validator.order_validation(
                customer_id,
                order_type,
                quantity,
                quoted_price,
            )

            self.assertEqual( result[ 'status' ], 'passed' )
            spread_amount = Decimal( '71000.00' ) * MARGIN
        self.assertEqual( result[ 'spread_amount' ], spread_amount.quantize( Decimal( '0.01' ) ) )

    def test_validate_market_price_zero( self ):
        ''' test validate function in case failed proceed
            with market price is 0

            expected result status should be failed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '0' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        customer_id = 1
        order_type = ORDER_TYPE_BUY
        quantity = 1
        quoted_price = 72420
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        self.assertEqual( result[ 'status' ], 'failed' )
        self.assertIn( 'Cannot proceed with market price at 0', result[ 'reason' ] )

    def test_validate_buy_order_insufficient_balance( self ):
        ''' test validate function in case failed proceed
            with order is more than balance

            expected result status should be failed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '100' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        customer_id = 1
        order_type = ORDER_TYPE_BUY
        quantity = 1
        quoted_price = 72420
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        self.assertEqual( result[ 'status' ], 'failed' )
        self.assertIn( 'Insufficient balance', result[ 'reason' ] )

    def test_validate_sell_order_insufficient_holding( self ):
        ''' test validate function in case failed proceed
            with holding quantity is less than order

            expected result status should be failed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '0.5' )

        # list of orders
        self.mock_test_db.get_orders.return_value = []

        customer_id = 1
        order_type = ORDER_TYPE_SELL
        quantity = 1
        quoted_price = 71000
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        self.assertEqual( result[ 'status' ], 'failed' )
        self.assertIn( 'Insufficient holding quantity', result[ 'reason' ] )

    def test_validate_trading_limit_success( self ):
        ''' test validate function in case success proceed
            with does not exceed the trading limit

            expected result status should be passed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = [
            { 'quantity': Decimal( '1.5' ), },
            { 'quantity': Decimal( '2.0' ), },
        ]

        # current daily quantity = 3.5
        # remaining = 1.5
        customer_id = 1
        order_type = ORDER_TYPE_BUY
        quantity = 1.5
        quoted_price = 72420
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        self.assertEqual( result[ 'status' ], 'passed' )
        spread_amount = Decimal( '71000.00' ) * MARGIN
        self.assertEqual( result[ 'spread_amount' ], spread_amount.quantize( Decimal( '0.01' ) ) )

    def test_validate_trading_limit_exceeded( self ):
        ''' test validate function in case failed proceed
            with exceed the trading limit

            expected result status should be failed
        '''
        # mock value of each function
        # market price
        self.mock_test_db.get_market_price.return_value = Decimal( '71000.00' )

        # customer balance
        self.mock_test_db.get_customer_balance.return_value = Decimal( '10000000' )

        # quantity holding
        self.mock_test_db.get_holding_quantity.return_value = Decimal( '10' )

        # list of orders
        self.mock_test_db.get_orders.return_value = [
            { 'quantity': Decimal( '2.0' ), },
            { 'quantity': Decimal( '2.0' ), },
        ]

        # current daily quantity = 4.0
        # remaining = 1.0
        # order quantity = 1.5 -> fail
        customer_id = 1
        order_type = ORDER_TYPE_BUY
        quantity = 1.5
        quoted_price = 72420
        result = self.validator.order_validation(
            customer_id,
            order_type,
            quantity,
            quoted_price,
        )

        self.assertEqual( result[ 'status' ], 'failed' )
        self.assertIn( 'Remaining allowance', result[ 'reason' ] )


if __name__ == '__main__':
    unittest.main()
