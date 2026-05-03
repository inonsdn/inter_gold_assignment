##############################
#
# Standart Import
#
import argparse
import datetime
from decimal import Decimal

##############################
#
# Global Variable
#

ORDER_TYPE_BUY = 'buy'
ORDER_TYPE_SELL = 'sell'
QUANTITY_INCREMENT_STEP = Decimal( '0.5' )
TOLERANCE_ORDER_AMOUNT = Decimal( '0.02' )
TRADING_LIMIT_QUANTITY = Decimal( '5' )
MARGIN = Decimal( '0.02' )

##############################
#
# Class
#
class DbMock:
    def __init__( self ):
        '''
        '''
        self.table_to_data_info_dict = {
            'customers': [
                {
                    'id': 1,
                    'name': 'Alice',
                    'balance': 10000000,
                },
                {
                    'id': 2,
                    'name': 'Bob',
                    'balance': 20000000,
                },
            ],
            'orders': [
                {
                    'id': 1,
                    'customer_id': 1,
                    'type': 'buy',
                    'quantity': 1.5,
                    'price': 20000,
                    'timestamp': 1777788000.0,
                },
                {
                    'id': 2,
                    'customer_id': 1,
                    'type': 'buy',
                    'quantity': 2.5,
                    'price': 10000,
                    'timestamp': 1777791600.0,
                },
                {
                    'id': 3,
                    'customer_id': 1,
                    'type': 'sell',
                    'quantity': 0.5,
                    'price': 10000,
                    'timestamp': 1777795200.0,
                },
            ],
        }

    def get_customer_info( self, customer_id: int ):
        customer_info_dict_list = list(
            filter(
                lambda customer: customer[ 'id' ] == customer_id,
                self.table_to_data_info_dict[ 'customers' ]
            )
        )
        if not customer_info_dict_list:
            return None
        return customer_info_dict_list[ 0 ]

    def get_market_price( self ) -> Decimal:
        return Decimal( '70000.00' )

    def get_customer_balance( self, customer_id: int ):
        customer = self.get_customer_info( customer_id )
        return Decimal( str( customer[ 'balance' ] ) )

    def get_holding_quantity( self, customer_id: int ) -> Decimal:
        return sum(
            map(
                lambda order: Decimal( str( order[ 'quantity' ] ) ),
                filter(
                    lambda order: order[ 'customer_id' ] == customer_id,
                    self.table_to_data_info_dict[ 'orders' ]
                )
            )
        )

    def get_orders( self, customer_id: int, start_datetime: datetime.datetime, end_datetime: datetime.datetime ):
        return list(
            filter(
                lambda order: order[ 'customer_id' ] == customer_id and 
                    start_datetime.timestamp() <= order[ 'timestamp' ] < end_datetime.timestamp(),
                self.table_to_data_info_dict[ 'orders' ]
            )
        )


class OrderValidator:

    def __init__( self, db: DbMock, margin: Decimal ):
        assert Decimal( '-1' ) <= margin <= Decimal( '1' )

        self.db = db
        self.margin = margin

    def _construct_failed_response( self, *messages: str ) -> dict:
        ''' wrap all message to be a response object by concat it

            Args:
                messages (*args str): list of str with spread of error
            
            Returns:
                dict map key of response which is status failed and reason
        '''
        msg = '\n'.join( messages )
        return {
            'status': 'failed',
            'reason': msg,
        }

    def _validate_quantity( self, quantity: Decimal ) -> str | None:
        ''' check the quantity must be increase step of QUANTITY_INCREMENT_STEP value
            it must able to divided by QUANTITY_INCREMENT_STEP
            currently QUANTITY_INCREMENT_STEP set to 0.5

            Args:
                quantity (decimal): number of quantity
            
            Return
                error str. None if pass validation
        '''
        # check the increment must increase QUANTITY_INCREMENT_STEP (now set to 0.5)
        # that means quantity must divided by QUANTITY_INCREMENT_STEP
        if quantity % QUANTITY_INCREMENT_STEP != 0:
            return f'quantity must be a increment of {QUANTITY_INCREMENT_STEP}'

    def _validate_quoted_price( self, quoted_price: Decimal, market_price: Decimal ) -> str | None:
        ''' check quoted price that must be freshness
            by the diff of market price and quoted prices must not over 2%

            Args:
                quoted_price (decimal): number of quoted price which is from customer
                market_price (decimal): number of current market price

            Return
                error str. None if pass validation
        '''
        # no market price valid, failed order
        if market_price == 0:
            return 'Cannot proceed with market price at 0'

        # quotedPrice must not over 2% of market price
        quoted_price_diff = ( abs( quoted_price - market_price ) / market_price ).quantize( Decimal( '0.0001' ) )
        if quoted_price_diff > TOLERANCE_ORDER_AMOUNT:
            return 'Price freshness error: order does not in valid range'

    def _validate_buy_order_type( self, customer_id: int, quantity: Decimal, quoted_price: Decimal ) -> str | None:
        ''' check a balance of account of given customer with buying price
            that must sufficient

            Args:
                customer_id (int): id of customer who take action
                quantity (decimal): number of gold quantity to buy
                market_price (decimal): number of current market price

            Return
                error str. None if pass validation
        '''
        # get balance of customer
        current_balance = self.db.get_customer_balance( customer_id )

        # compute a total price that customer order
        total_price = ( quantity * quoted_price ).quantize( Decimal( '0.01' ) )

        # check that balance of customer is sufficient
        if current_balance < total_price:
            return 'Insufficient balance for making order'

    def _validate_sell_order_type( self, customer_id: int, quantity: Decimal ) -> str | None:
        ''' check the quantity of sell order must not over the customer holding

            Args:
                customer_id (int): id of customer who take action
                quantity (decimal): number of gold quantity to sell

            Return
                error str. None if pass validation
        '''
        # get all customer order
        current_quantity = self.db.get_holding_quantity( customer_id )

        # error if order quantity is more than current quantity
        if quantity > current_quantity:
            return f'Insufficient holding quantity for making sell order'

    def _validate_trading_limit( self, customer_id: int, quantity: Decimal ):
        ''' validate the trading limit that must over limited
            even buy or sell

            Args:
                customer_id (int): id of customer who take action
                quantity (decimal): number of gold quantity to sell

            Return
                error str. None if pass validation
        '''
        # get date range of today to find order in a day
        #   start time will be today at 00:00
        #   end time will be tomorrow at 00:00
        #   so range will be [ start, end )
        now_datetime = datetime.datetime.now()
        next_day_datetime = now_datetime + datetime.timedelta( days = 1 )
        start_datetime = datetime.datetime( now_datetime.year, now_datetime.month, now_datetime.day, 0 )
        end_datetime = datetime.datetime( next_day_datetime.year, next_day_datetime.month, next_day_datetime.day, 0 )

        # get orders in date range
        orders = self.db.get_orders( customer_id, start_datetime, end_datetime )

        # sum quantity of transaction
        current_daily_quantity = sum( map( lambda order: Decimal( str( order[ 'quantity' ] ) ), orders ) )

        # compute remaining quantity quota in this day
        remaining_quantity = TRADING_LIMIT_QUANTITY - current_daily_quantity

        # check if the order exceed the remaining
        if quantity > remaining_quantity:
            date_str = now_datetime.strftime( '%Y-%m-%d' )
            return f'Remaining allowance of date {date_str} is {remaining_quantity}. You cannot proceed over remaining quota. (Quota limited is {TRADING_LIMIT_QUANTITY})'

    def order_validation( self, customer_id: int, order_type: str, quantity: float, quoted_price: float ) -> dict:
        ''' validate order that must be exist and valid with condition
            1. Order type must be either "buy" or "sell"
            2. Quantity must be positive and in valid increments (multiples of 0.5 baht-weight)
            3. Quoted price must be positive
            4. For buy orders: the customer's available balance must be suﬀicient to cover quantity * quoted_price
            5. Price freshness: the quoted price must be within 2% of the current market price (to prevent stale quotes from being executed)

            eg. buy 1.5 baht-weight at 71,000 baht, balance must cover 1.5 * 71,000 = 106,500 
                and 71,000 must be within 2% of current market price

            Args:
                customer_id (int): id of customer
                order_type (str): type of order that must be "buy" or "sell"
                quantity (float): number of baht-weight of this transaction, must be a multiple of 0.5
                quoted_price (float): price at this transaction take an action
            
            Returns:
                dict map response key status that pass or failed
                    and reason of failed response
        '''
        # type validation first
        # check order type must be buy or sell only
        if order_type not in ( ORDER_TYPE_BUY, ORDER_TYPE_SELL ):
            return self._construct_failed_response( f'Unsupported order type {order_type}' )

        # validate type of quantity must be integer or float
        if not isinstance( quantity, ( int, float ) ):
            return self._construct_failed_response( 'quantity must be a number' )

        # validate type of quotedPrice must be integer or float
        if not isinstance( quoted_price, ( int, float ) ):
            return self._construct_failed_response( 'price must be a number' )
        
        # quantity must be a positive value
        if quantity <= 0:
            return self._construct_failed_response( 'quantity must be a positive' )

        # quotedPrice must be a positive value
        if quoted_price <= 0:
            return self._construct_failed_response( 'price must be a positive' )

        # check type of customer id
        if not isinstance( customer_id, int ):
            return self._construct_failed_response( f'Unsupported customer id type {type( customer_id )}' )

        # check customer must valid in db
        customer_info = self.db.get_customer_info( customer_id )
        if customer_info is None:
            return self._construct_failed_response( f'Not found customer id {customer_id}' )

        # convert all currency value to decimal type for compute
        quantity_dec = Decimal( str( quantity ) )
        quoted_price_dec = Decimal( str( quoted_price ) )

        # validate trading limit of customer
        error = self._validate_trading_limit( customer_id, quantity_dec )
        if error is not None:
            return self._construct_failed_response( error )

        # store error of business logic
        errors = list()

        # get market price from db
        market_price_dec = self.db.get_market_price()

        # validate quantity
        error = self._validate_quantity( quantity_dec )
        if error is not None:
            errors.append( error )

        # validate buy order type
        if order_type == ORDER_TYPE_BUY:

            # compute market price with spread including margin
            market_price_with_spread_dec = market_price_dec * ( 1 + self.margin )

            error = self._validate_buy_order_type( customer_id, quantity_dec, quoted_price_dec )
            if error is not None:
                errors.append( error )

        # validate sell order type
        elif order_type == ORDER_TYPE_SELL:

            # sell prices
            market_price_with_spread_dec = market_price_dec

            error = self._validate_sell_order_type( customer_id, quantity_dec )
            if error is not None:
                errors.append( error )

        # validate quoted price
        error = self._validate_quoted_price( quoted_price_dec, market_price_with_spread_dec )
        if error is not None:
            errors.append( error )

        # construct error response if there are errors from business logic validation
        if len( errors ) > 0:
            return self._construct_failed_response( *errors )

        return { 'status': 'passed', }

##############################
#
# Functions
#

if __name__ == '__main__':
    parser = argparse.ArgumentParser( description = 'Order validation' )
    parser.add_argument( 'customer_id', type=int, help='id of customer (eg. 1, 2, 3,..)' )
    parser.add_argument( 'order_type', type=str, help='type of order, should be buy or sell' )
    parser.add_argument( 'quantity', type=float, help='quantity of making order, must be increment of 0.5' )
    parser.add_argument( 'quoted_price', type=float, help='price when make order' )
    args = parser.parse_args()

    # customer_id = 1
    # order_type = ORDER_TYPE_BUY
    # quantity = 3
    # quoted_price = 70500.5

    customer_id = args.customer_id
    order_type = args.order_type
    quantity = args.quantity
    quoted_price = args.quoted_price

    db = DbMock()
    validator = OrderValidator( db, MARGIN )
    result = validator.order_validation( customer_id, order_type, quantity, quoted_price )
    print( result )