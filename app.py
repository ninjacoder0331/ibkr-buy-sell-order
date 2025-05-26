from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import asyncio
from ib_insync import IB, Stock, MarketOrder
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# IBKR connection settings for paper trading
IB_HOST = os.getenv('IB_HOST', '127.0.0.1')
IB_PORT = int(os.getenv('IB_PORT', 7497))  # 7497 for TWS paper trading
CLIENT_ID = int(os.getenv('CLIENT_ID', 1))

class IBKRTrader:
    def __init__(self):
        self.connected = False
    
    async def connect(self):
        """Connect to IBKR for paper trading"""
        try:
            # Create a new IB instance for each connection (serverless friendly)
            ib = IB()
            await ib.connectAsync(IB_HOST, IB_PORT, clientId=CLIENT_ID)
            
            # Verify connection is actually established
            if ib.isConnected():
                self.connected = True
                return ib
            else:
                self.connected = False
                return None
                
        except Exception as e:
            logger.error(f"Failed to connect to IBKR: {str(e)}")
            self.connected = False
            return None
    
    async def test_connection(self):
        """Test connection to IBKR and return detailed status"""
        ib = None
        try:
            ib = await self.connect()
            if not ib:
                return {
                    "success": False,
                    "error": "Failed to establish connection",
                    "host": IB_HOST,
                    "port": IB_PORT,
                    "client_id": CLIENT_ID
                }
            
            # Test if we can get account summary
            accounts = ib.managedAccounts()
            
            return {
                "success": True,
                "connected": True,
                "accounts": accounts,
                "host": IB_HOST,
                "port": IB_PORT,
                "client_id": CLIENT_ID
            }
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            self.connected = False
            return {
                "success": False,
                "error": str(e),
                "host": IB_HOST,
                "port": IB_PORT,
                "client_id": CLIENT_ID
            }
        finally:
            if ib and ib.isConnected():
                ib.disconnect()
    
    async def disconnect(self):
        """Disconnect from IBKR - Not needed in serverless environment"""
        self.connected = False
    
    async def place_market_order(self, symbol, action, quantity):
        """Place a market order (BUY or SELL)"""
        ib = None
        try:
            # Create new connection for this request
            ib = await self.connect()
            if not ib:
                return {"error": "Failed to connect to IBKR"}
            
            # Create stock contract
            contract = Stock(symbol, 'SMART', 'USD')
            
            # Qualify the contract
            qualified_contracts = await ib.qualifyContractsAsync(contract)
            if not qualified_contracts:
                return {"error": f"Could not qualify contract for symbol {symbol}"}
            
            contract = qualified_contracts[0]
            
            # Create market order
            order = MarketOrder(action.upper(), quantity)
            
            # Place the order
            trade = ib.placeOrder(contract, order)
            
            # Wait a moment for order to be processed
            await asyncio.sleep(0.1)
            
            return {
                "success": True,
                "order_id": trade.order.orderId,
                "symbol": symbol,
                "action": action,
                "quantity": quantity,
                "order_type": "MARKET",
                "status": trade.orderStatus.status
            }
            
        except Exception as e:
            logger.error(f"Error placing market order: {str(e)}")
            self.connected = False
            return {"error": str(e)}
        finally:
            if ib and ib.isConnected():
                ib.disconnect()

# Initialize trader
trader = IBKRTrader()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Simple IBKR Paper Trading API",
        "version": "1.0.0",
        "environment": "vercel" if os.getenv('VERCEL') else "local",
        "endpoints": {
            "/": "GET - API information",
            "/health": "GET - Health check",
            "/status": "GET - Service status",
            "/test-connection": "GET - Test IBKR connection",
            "/buy": "POST - Place market buy order",
            "/sell": "POST - Place market sell order"
        }
    })

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        "status": "online",
        "environment": "serverless" if os.getenv('VERCEL') else "local",
        "trading_mode": "paper",
        "config": {
            "host": IB_HOST,
            "port": IB_PORT,
            "client_id": CLIENT_ID
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": str(asyncio.get_event_loop().time()),
        "environment": "vercel" if os.getenv('VERCEL') else "local"
    })

@app.route('/test-connection', methods=['GET'])
def test_connection():
    """Test connection endpoint with detailed troubleshooting info"""
    try:
        result = asyncio.run(trader.test_connection())
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in test-connection endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/buy', methods=['POST'])
def buy_stock():
    """Buy stock with market order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'symbol' not in data or 'quantity' not in data:
            return jsonify({"error": "Missing required fields: symbol and quantity"}), 400
        
        symbol = data['symbol'].upper()
        quantity = int(data['quantity'])
        
        # Place market buy order
        result = asyncio.run(trader.place_market_order(symbol, 'BUY', quantity))
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in buy endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/sell', methods=['POST'])
def sell_stock():
    """Sell stock with market order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'symbol' not in data or 'quantity' not in data:
            return jsonify({"error": "Missing required fields: symbol and quantity"}), 400
        
        symbol = data['symbol'].upper()
        quantity = int(data['quantity'])
        
        # Place market sell order
        result = asyncio.run(trader.place_market_order(symbol, 'SELL', quantity))
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in sell endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

# For Vercel deployment
application = app

if __name__ == '__main__':
    app.run(debug=True, port=5000) 