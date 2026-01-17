#!/usr/bin/env python3
"""
Funding Rate Arbitrage Scanner
Scans multiple CEX and DEX exchanges for funding rate arbitrage opportunities.
Calculates APR and suggests long/short positions for maximum profit.
"""

import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime
import sys

# Try to import ccxt, provide helpful error if not available
try:
    import ccxt.async_support as ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    print("Warning: ccxt not installed. Run: pip install ccxt aiohttp")


@dataclass
class FundingRate:
    """Funding rate data for a symbol on an exchange"""
    exchange: str
    symbol: str
    funding_rate: float  # Current funding rate (as decimal, e.g., 0.0001 = 0.01%)
    next_funding_time: Optional[datetime] = None
    funding_interval_hours: int = 8  # Most exchanges use 8h intervals
    mark_price: Optional[float] = None


@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity between two exchanges"""
    symbol: str
    long_exchange: str  # Exchange to go long (receives funding if rate is positive)
    short_exchange: str  # Exchange to go short (pays funding if rate is positive)
    long_funding_rate: float
    short_funding_rate: float
    rate_difference: float  # Absolute difference in funding rates
    estimated_apr: float  # Annualized percentage return
    long_mark_price: Optional[float] = None
    short_mark_price: Optional[float] = None


class FundingRateFetcher:
    """Fetches funding rates from multiple exchanges"""

    def __init__(self):
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self):
        """Initialize exchange connections"""
        if not CCXT_AVAILABLE:
            return

        # CEX exchanges via CCXT
        self.exchanges = {
            'binance': ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'swap'}}),
            'bybit': ccxt.bybit({'enableRateLimit': True, 'options': {'defaultType': 'swap'}}),
            'okx': ccxt.okx({'enableRateLimit': True, 'options': {'defaultType': 'swap'}}),
            'gate': ccxt.gate({'enableRateLimit': True, 'options': {'defaultType': 'swap'}}),
        }
        self.session = aiohttp.ClientSession()

    async def close(self):
        """Close all connections"""
        for exchange in self.exchanges.values():
            try:
                await exchange.close()
            except:
                pass
        if self.session:
            try:
                await self.session.close()
            except:
                pass

    async def fetch_binance_funding_rates(self) -> List[FundingRate]:
        """Fetch funding rates from Binance Futures"""
        rates = []
        try:
            exchange = self.exchanges['binance']
            await exchange.load_markets()
            funding_data = await exchange.fetch_funding_rates()

            for symbol, data in funding_data.items():
                if '/USDT:USDT' in symbol:
                    clean_symbol = symbol.replace(':USDT', '')
                    rates.append(FundingRate(
                        exchange='Binance',
                        symbol=clean_symbol,
                        funding_rate=data.get('fundingRate', 0) or 0,
                        next_funding_time=datetime.fromtimestamp(data['fundingTimestamp'] / 1000) if data.get('fundingTimestamp') else None,
                        funding_interval_hours=8,
                        mark_price=data.get('markPrice')
                    ))
        except Exception as e:
            print(f"Error fetching Binance funding rates: {e}")
        return rates

    async def fetch_bybit_funding_rates(self) -> List[FundingRate]:
        """Fetch funding rates from Bybit"""
        rates = []
        try:
            exchange = self.exchanges['bybit']
            await exchange.load_markets()
            funding_data = await exchange.fetch_funding_rates()

            for symbol, data in funding_data.items():
                if '/USDT:USDT' in symbol:
                    clean_symbol = symbol.replace(':USDT', '')
                    rates.append(FundingRate(
                        exchange='Bybit',
                        symbol=clean_symbol,
                        funding_rate=data.get('fundingRate', 0) or 0,
                        next_funding_time=datetime.fromtimestamp(data['fundingTimestamp'] / 1000) if data.get('fundingTimestamp') else None,
                        funding_interval_hours=8,
                        mark_price=data.get('markPrice')
                    ))
        except Exception as e:
            print(f"Error fetching Bybit funding rates: {e}")
        return rates

    async def fetch_okx_funding_rates(self) -> List[FundingRate]:
        """Fetch funding rates from OKX"""
        rates = []
        try:
            exchange = self.exchanges['okx']
            await exchange.load_markets()
            funding_data = await exchange.fetch_funding_rates()

            for symbol, data in funding_data.items():
                if '/USDT:USDT' in symbol:
                    clean_symbol = symbol.replace(':USDT', '')
                    rates.append(FundingRate(
                        exchange='OKX',
                        symbol=clean_symbol,
                        funding_rate=data.get('fundingRate', 0) or 0,
                        next_funding_time=datetime.fromtimestamp(data['fundingTimestamp'] / 1000) if data.get('fundingTimestamp') else None,
                        funding_interval_hours=8,
                        mark_price=data.get('markPrice')
                    ))
        except Exception as e:
            print(f"Error fetching OKX funding rates: {e}")
        return rates

    async def fetch_gate_funding_rates(self) -> List[FundingRate]:
        """Fetch funding rates from Gate.io"""
        rates = []
        try:
            exchange = self.exchanges['gate']
            await exchange.load_markets()
            funding_data = await exchange.fetch_funding_rates()

            for symbol, data in funding_data.items():
                if '/USDT:USDT' in symbol:
                    clean_symbol = symbol.replace(':USDT', '')
                    rates.append(FundingRate(
                        exchange='Gate.io',
                        symbol=clean_symbol,
                        funding_rate=data.get('fundingRate', 0) or 0,
                        next_funding_time=datetime.fromtimestamp(data['fundingTimestamp'] / 1000) if data.get('fundingTimestamp') else None,
                        funding_interval_hours=8,
                        mark_price=data.get('markPrice')
                    ))
        except Exception as e:
            print(f"Error fetching Gate.io funding rates: {e}")
        return rates

    async def fetch_hyperliquid_funding_rates(self) -> List[FundingRate]:
        """Fetch funding rates from Hyperliquid DEX"""
        rates = []
        try:
            url = "https://api.hyperliquid.xyz/info"
            payload = {"type": "metaAndAssetCtxs"}

            async with self.session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if len(data) >= 2:
                        meta = data[0]
                        asset_ctxs = data[1]

                        for i, asset in enumerate(meta.get('universe', [])):
                            if i < len(asset_ctxs):
                                ctx = asset_ctxs[i]
                                symbol = asset.get('name', '')
                                funding_rate = float(ctx.get('funding', 0))
                                mark_price = float(ctx.get('markPx', 0))

                                rates.append(FundingRate(
                                    exchange='Hyperliquid',
                                    symbol=f"{symbol}/USDT",
                                    funding_rate=funding_rate,
                                    funding_interval_hours=1,  # Hyperliquid has hourly funding
                                    mark_price=mark_price
                                ))
        except Exception as e:
            print(f"Error fetching Hyperliquid funding rates: {e}")
        return rates

    async def fetch_dydx_funding_rates(self) -> List[FundingRate]:
        """Fetch funding rates from dYdX v4"""
        rates = []
        try:
            url = "https://indexer.dydx.trade/v4/perpetualMarkets"

            async with self.session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    markets = data.get('markets', {})

                    for symbol, market_data in markets.items():
                        funding_rate = float(market_data.get('nextFundingRate', 0))
                        oracle_price = float(market_data.get('oraclePrice', 0))
                        clean_symbol = symbol.replace('-USD', '/USDT')

                        rates.append(FundingRate(
                            exchange='dYdX',
                            symbol=clean_symbol,
                            funding_rate=funding_rate,
                            funding_interval_hours=1,  # dYdX has hourly funding
                            mark_price=oracle_price
                        ))
        except Exception as e:
            print(f"Error fetching dYdX funding rates: {e}")
        return rates

    async def fetch_all_funding_rates(self) -> Dict[str, List[FundingRate]]:
        """Fetch funding rates from all exchanges"""
        if not CCXT_AVAILABLE:
            return {}

        tasks = [
            self.fetch_binance_funding_rates(),
            self.fetch_bybit_funding_rates(),
            self.fetch_okx_funding_rates(),
            self.fetch_gate_funding_rates(),
            self.fetch_hyperliquid_funding_rates(),
            self.fetch_dydx_funding_rates(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_rates = {}
        exchange_names = ['Binance', 'Bybit', 'OKX', 'Gate.io', 'Hyperliquid', 'dYdX']

        for name, result in zip(exchange_names, results):
            if isinstance(result, Exception):
                print(f"Error fetching from {name}: {result}")
                all_rates[name] = []
            else:
                all_rates[name] = result

        return all_rates


class ArbitrageCalculator:
    """Calculates arbitrage opportunities from funding rates"""

    @staticmethod
    def normalize_symbol(symbol: str) -> str:
        """Normalize symbol format for comparison"""
        return symbol.upper().replace(' ', '').replace('-', '/').split(':')[0]

    @staticmethod
    def calculate_apr(rate_difference: float, funding_interval_hours: int) -> float:
        """Calculate annualized percentage return from funding rate difference."""
        periods_per_year = (24 / funding_interval_hours) * 365
        apr = rate_difference * periods_per_year * 100
        return apr

    def find_arbitrage_opportunities(
        self,
        all_rates: Dict[str, List[FundingRate]],
        min_apr: float = 5.0,
        top_symbols: Optional[List[str]] = None
    ) -> List[ArbitrageOpportunity]:
        """Find arbitrage opportunities across exchanges."""
        symbol_rates: Dict[str, List[FundingRate]] = {}

        for exchange, rates in all_rates.items():
            for rate in rates:
                normalized = self.normalize_symbol(rate.symbol)
                if top_symbols and normalized not in [self.normalize_symbol(s) for s in top_symbols]:
                    continue
                if normalized not in symbol_rates:
                    symbol_rates[normalized] = []
                symbol_rates[normalized].append(rate)

        opportunities = []

        for symbol, rates in symbol_rates.items():
            if len(rates) < 2:
                continue

            rates.sort(key=lambda x: x.funding_rate)
            best_long = rates[0]
            best_short = rates[-1]

            if best_long.exchange == best_short.exchange:
                continue

            rate_difference = best_short.funding_rate - best_long.funding_rate

            if rate_difference <= 0:
                continue

            min_interval = min(best_long.funding_interval_hours, best_short.funding_interval_hours)
            apr = self.calculate_apr(rate_difference, min_interval)

            if apr >= min_apr:
                opportunities.append(ArbitrageOpportunity(
                    symbol=symbol,
                    long_exchange=best_long.exchange,
                    short_exchange=best_short.exchange,
                    long_funding_rate=best_long.funding_rate,
                    short_funding_rate=best_short.funding_rate,
                    rate_difference=rate_difference,
                    estimated_apr=apr,
                    long_mark_price=best_long.mark_price,
                    short_mark_price=best_short.mark_price
                ))

        opportunities.sort(key=lambda x: x.estimated_apr, reverse=True)
        return opportunities


def format_funding_rate(rate: float) -> str:
    """Format funding rate as percentage"""
    return f"{rate * 100:+.4f}%"


def format_apr(apr: float) -> str:
    """Format APR with color coding for terminal"""
    if apr >= 100:
        return f"\033[92m{apr:,.1f}%\033[0m"  # Bright green
    elif apr >= 50:
        return f"\033[32m{apr:,.1f}%\033[0m"  # Green
    elif apr >= 20:
        return f"\033[33m{apr:,.1f}%\033[0m"  # Yellow
    else:
        return f"{apr:,.1f}%"


def get_sample_data() -> Dict[str, List[FundingRate]]:
    """Generate sample data for demonstration"""
    return {
        'Binance': [
            FundingRate('Binance', 'BTC/USDT', 0.0001, None, 8, 97500.0),
            FundingRate('Binance', 'ETH/USDT', 0.00015, None, 8, 3450.0),
            FundingRate('Binance', 'SOL/USDT', 0.0003, None, 8, 215.0),
            FundingRate('Binance', 'XRP/USDT', 0.00025, None, 8, 2.35),
            FundingRate('Binance', 'DOGE/USDT', 0.0004, None, 8, 0.42),
            FundingRate('Binance', 'AVAX/USDT', 0.00018, None, 8, 42.5),
            FundingRate('Binance', 'ARB/USDT', 0.00055, None, 8, 0.95),
            FundingRate('Binance', 'OP/USDT', 0.0006, None, 8, 2.15),
            FundingRate('Binance', 'LINK/USDT', 0.00022, None, 8, 24.5),
            FundingRate('Binance', 'WIF/USDT', 0.0012, None, 8, 2.85),
            FundingRate('Binance', 'PEPE/USDT', 0.0015, None, 8, 0.000021),
            FundingRate('Binance', 'SUI/USDT', 0.00045, None, 8, 4.25),
            FundingRate('Binance', 'NEAR/USDT', 0.00028, None, 8, 5.45),
            FundingRate('Binance', 'APT/USDT', 0.00035, None, 8, 9.85),
            FundingRate('Binance', 'INJ/USDT', 0.00042, None, 8, 28.5),
        ],
        'Bybit': [
            FundingRate('Bybit', 'BTC/USDT', 0.00008, None, 8, 97480.0),
            FundingRate('Bybit', 'ETH/USDT', 0.00012, None, 8, 3448.0),
            FundingRate('Bybit', 'SOL/USDT', 0.00025, None, 8, 214.5),
            FundingRate('Bybit', 'XRP/USDT', 0.00022, None, 8, 2.34),
            FundingRate('Bybit', 'DOGE/USDT', 0.00035, None, 8, 0.418),
            FundingRate('Bybit', 'AVAX/USDT', 0.00015, None, 8, 42.3),
            FundingRate('Bybit', 'ARB/USDT', 0.00048, None, 8, 0.948),
            FundingRate('Bybit', 'OP/USDT', 0.00052, None, 8, 2.13),
            FundingRate('Bybit', 'LINK/USDT', 0.00019, None, 8, 24.4),
            FundingRate('Bybit', 'WIF/USDT', 0.001, None, 8, 2.82),
            FundingRate('Bybit', 'PEPE/USDT', 0.0013, None, 8, 0.0000208),
            FundingRate('Bybit', 'SUI/USDT', 0.0004, None, 8, 4.22),
            FundingRate('Bybit', 'NEAR/USDT', 0.00024, None, 8, 5.42),
            FundingRate('Bybit', 'APT/USDT', 0.0003, None, 8, 9.82),
            FundingRate('Bybit', 'INJ/USDT', 0.00038, None, 8, 28.3),
        ],
        'OKX': [
            FundingRate('OKX', 'BTC/USDT', 0.00012, None, 8, 97510.0),
            FundingRate('OKX', 'ETH/USDT', 0.00018, None, 8, 3452.0),
            FundingRate('OKX', 'SOL/USDT', 0.00028, None, 8, 215.2),
            FundingRate('OKX', 'XRP/USDT', 0.0002, None, 8, 2.355),
            FundingRate('OKX', 'DOGE/USDT', 0.00032, None, 8, 0.421),
            FundingRate('OKX', 'AVAX/USDT', 0.00022, None, 8, 42.6),
            FundingRate('OKX', 'ARB/USDT', 0.0005, None, 8, 0.952),
            FundingRate('OKX', 'OP/USDT', 0.00055, None, 8, 2.16),
            FundingRate('OKX', 'LINK/USDT', 0.00025, None, 8, 24.55),
            FundingRate('OKX', 'WIF/USDT', 0.0011, None, 8, 2.84),
            FundingRate('OKX', 'PEPE/USDT', 0.0014, None, 8, 0.0000209),
            FundingRate('OKX', 'SUI/USDT', 0.00042, None, 8, 4.24),
            FundingRate('OKX', 'NEAR/USDT', 0.00026, None, 8, 5.44),
            FundingRate('OKX', 'APT/USDT', 0.00032, None, 8, 9.84),
            FundingRate('OKX', 'INJ/USDT', 0.0004, None, 8, 28.4),
        ],
        'Gate.io': [
            FundingRate('Gate.io', 'BTC/USDT', 0.00015, None, 8, 97520.0),
            FundingRate('Gate.io', 'ETH/USDT', 0.0002, None, 8, 3455.0),
            FundingRate('Gate.io', 'SOL/USDT', 0.00035, None, 8, 215.5),
            FundingRate('Gate.io', 'XRP/USDT', 0.0003, None, 8, 2.36),
            FundingRate('Gate.io', 'DOGE/USDT', 0.00045, None, 8, 0.422),
            FundingRate('Gate.io', 'AVAX/USDT', 0.00025, None, 8, 42.7),
            FundingRate('Gate.io', 'ARB/USDT', 0.0006, None, 8, 0.955),
            FundingRate('Gate.io', 'OP/USDT', 0.00065, None, 8, 2.17),
            FundingRate('Gate.io', 'LINK/USDT', 0.0003, None, 8, 24.6),
            FundingRate('Gate.io', 'WIF/USDT', 0.0014, None, 8, 2.86),
            FundingRate('Gate.io', 'PEPE/USDT', 0.0018, None, 8, 0.000021),
            FundingRate('Gate.io', 'SUI/USDT', 0.0005, None, 8, 4.26),
            FundingRate('Gate.io', 'NEAR/USDT', 0.00032, None, 8, 5.46),
            FundingRate('Gate.io', 'APT/USDT', 0.0004, None, 8, 9.86),
            FundingRate('Gate.io', 'INJ/USDT', 0.00048, None, 8, 28.5),
        ],
        'Hyperliquid': [
            FundingRate('Hyperliquid', 'BTC/USDT', 0.000015, None, 1, 97495.0),  # Hourly rate
            FundingRate('Hyperliquid', 'ETH/USDT', 0.000018, None, 1, 3449.0),
            FundingRate('Hyperliquid', 'SOL/USDT', 0.00004, None, 1, 214.8),
            FundingRate('Hyperliquid', 'XRP/USDT', 0.000025, None, 1, 2.345),
            FundingRate('Hyperliquid', 'DOGE/USDT', 0.00005, None, 1, 0.419),
            FundingRate('Hyperliquid', 'AVAX/USDT', 0.000022, None, 1, 42.4),
            FundingRate('Hyperliquid', 'ARB/USDT', 0.00006, None, 1, 0.95),
            FundingRate('Hyperliquid', 'OP/USDT', 0.000065, None, 1, 2.14),
            FundingRate('Hyperliquid', 'LINK/USDT', 0.000028, None, 1, 24.45),
            FundingRate('Hyperliquid', 'WIF/USDT', 0.00012, None, 1, 2.83),
            FundingRate('Hyperliquid', 'PEPE/USDT', 0.00015, None, 1, 0.0000207),
            FundingRate('Hyperliquid', 'SUI/USDT', 0.00005, None, 1, 4.23),
            FundingRate('Hyperliquid', 'NEAR/USDT', 0.00003, None, 1, 5.43),
            FundingRate('Hyperliquid', 'APT/USDT', 0.000038, None, 1, 9.83),
            FundingRate('Hyperliquid', 'INJ/USDT', 0.000045, None, 1, 28.35),
        ],
        'dYdX': [
            FundingRate('dYdX', 'BTC/USDT', 0.000012, None, 1, 97490.0),  # Hourly rate
            FundingRate('dYdX', 'ETH/USDT', 0.000016, None, 1, 3447.0),
            FundingRate('dYdX', 'SOL/USDT', 0.000035, None, 1, 214.6),
            FundingRate('dYdX', 'XRP/USDT', 0.000022, None, 1, 2.34),
            FundingRate('dYdX', 'DOGE/USDT', 0.000045, None, 1, 0.417),
            FundingRate('dYdX', 'AVAX/USDT', 0.00002, None, 1, 42.35),
            FundingRate('dYdX', 'ARB/USDT', 0.000055, None, 1, 0.948),
            FundingRate('dYdX', 'OP/USDT', 0.00006, None, 1, 2.12),
            FundingRate('dYdX', 'LINK/USDT', 0.000025, None, 1, 24.42),
            FundingRate('dYdX', 'WIF/USDT', 0.0001, None, 1, 2.81),
            FundingRate('dYdX', 'NEAR/USDT', 0.000028, None, 1, 5.41),
            FundingRate('dYdX', 'APT/USDT', 0.000035, None, 1, 9.81),
            FundingRate('dYdX', 'INJ/USDT', 0.00004, None, 1, 28.3),
        ],
    }


def print_header():
    """Print scanner header"""
    print("\033[1m" + "=" * 110 + "\033[0m")
    print("\033[1m                           FUNDING RATE ARBITRAGE SCANNER\033[0m")
    print("\033[1m                 CEX: Binance, Bybit, OKX, Gate.io\033[0m")
    print("\033[1m                 DEX: Hyperliquid, dYdX\033[0m")
    print("\033[1m" + "=" * 110 + "\033[0m")
    print(f"\nScan time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")


def print_opportunities(opportunities: List[ArbitrageOpportunity], calculator: ArbitrageCalculator, all_rates: Dict[str, List[FundingRate]]):
    """Print arbitrage opportunities"""
    print("\033[1m" + "=" * 110 + "\033[0m")
    print("\033[1m                              ARBITRAGE OPPORTUNITIES (Sorted by APR)\033[0m")
    print("\033[1m" + "=" * 110 + "\033[0m")
    print(f"\n{'Rank':<5} {'Symbol':<12} {'LONG @':<14} {'SHORT @':<14} {'Long Rate':<12} {'Short Rate':<12} {'Est. APR':<15}")
    print("-" * 110)

    for i, opp in enumerate(opportunities[:30], 1):
        print(f"{i:<5} {opp.symbol:<12} \033[92m{opp.long_exchange:<14}\033[0m \033[91m{opp.short_exchange:<14}\033[0m "
              f"{format_funding_rate(opp.long_funding_rate):<12} "
              f"{format_funding_rate(opp.short_funding_rate):<12} "
              f"{format_apr(opp.estimated_apr):<15}")

    print("-" * 110)
    print(f"\n\033[1mTotal opportunities found: {len(opportunities)}\033[0m")

    # Detailed analysis
    print("\n" + "\033[1m" + "=" * 110 + "\033[0m")
    print("\033[1m                              TOP 10 DETAILED ANALYSIS\033[0m")
    print("\033[1m" + "=" * 110 + "\033[0m")

    for i, opp in enumerate(opportunities[:10], 1):
        print(f"\n\033[1m#{i} {opp.symbol}\033[0m")
        print(f"   \033[96mStrategy:\033[0m \033[92mLONG\033[0m on {opp.long_exchange} + \033[91mSHORT\033[0m on {opp.short_exchange}")
        print(f"   Long Funding Rate:  {format_funding_rate(opp.long_funding_rate)} (8h)")
        print(f"   Short Funding Rate: {format_funding_rate(opp.short_funding_rate)} (8h)")
        print(f"   Rate Difference:    {format_funding_rate(opp.rate_difference)} per period")
        print(f"   \033[93mEstimated APR:\033[0m      \033[1m{opp.estimated_apr:.1f}%\033[0m")
        if opp.long_mark_price and opp.short_mark_price:
            price_diff = abs(opp.long_mark_price - opp.short_mark_price) / opp.long_mark_price * 100
            print(f"   Price Difference:   {price_diff:.3f}%")
            print(f"   Long Price:         ${opp.long_mark_price:,.4f}")
            print(f"   Short Price:        ${opp.short_mark_price:,.4f}")
        print("-" * 55)

    # Funding rate matrix
    print("\n" + "\033[1m" + "=" * 110 + "\033[0m")
    print("\033[1m                              FUNDING RATE MATRIX (Major Coins)\033[0m")
    print("\033[1m" + "=" * 110 + "\033[0m")

    top_coins = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'DOGE/USDT', 'AVAX/USDT', 'ARB/USDT', 'OP/USDT']
    exchanges = ['Binance', 'Bybit', 'OKX', 'Gate.io', 'Hyperliquid', 'dYdX']

    rate_lookup = {}
    for exchange, rates in all_rates.items():
        for rate in rates:
            normalized = calculator.normalize_symbol(rate.symbol)
            key = (normalized, exchange)
            rate_lookup[key] = rate.funding_rate

    print(f"\n{'Coin':<12}", end="")
    for ex in exchanges:
        print(f"{ex:<14}", end="")
    print()
    print("-" * (12 + 14 * len(exchanges)))

    for coin in top_coins:
        normalized_coin = calculator.normalize_symbol(coin)
        print(f"{normalized_coin:<12}", end="")
        for ex in exchanges:
            rate = rate_lookup.get((normalized_coin, ex))
            if rate is not None:
                # Color code: green for negative (good for long), red for high positive
                if rate < 0:
                    color = "\033[92m"  # Green
                elif rate > 0.0005:
                    color = "\033[91m"  # Red
                else:
                    color = ""
                end_color = "\033[0m" if color else ""
                print(f"{color}{format_funding_rate(rate):<14}{end_color}", end="")
            else:
                print(f"{'N/A':<14}", end="")
        print()


def print_strategy_guide():
    """Print strategy explanation"""
    print("\n" + "\033[1m" + "=" * 110 + "\033[0m")
    print("\033[1m                              FUNDING RATE ARBITRAGE GUIDE\033[0m")
    print("\033[1m" + "=" * 110 + "\033[0m")
    print("""
    \033[96m[전략 설명]\033[0m

    펀딩비 아비트라지는 델타 중립 전략입니다:

    1. \033[92mLONG (매수)\033[0m - 펀딩비가 가장 낮은(또는 음수인) 거래소에서
       • 펀딩비가 음수면 → 롱 포지션이 펀딩비를 \033[92m받습니다\033[0m
       • 펀딩비가 양수면 → 롱 포지션이 펀딩비를 지불합니다 (하지만 가장 적게)

    2. \033[91mSHORT (매도)\033[0m - 펀딩비가 가장 높은 거래소에서
       • 펀딩비가 양수면 → 숏 포지션이 펀딩비를 \033[92m받습니다\033[0m
       • 펀딩비가 음수면 → 숏 포지션이 펀딩비를 지불합니다

    \033[93m[수익 계산]\033[0m

    • 펀딩비 차이 = Short 거래소 펀딩비 - Long 거래소 펀딩비
    • 예상 APR = 펀딩비 차이 × (24h ÷ 펀딩 주기) × 365 × 100

    \033[91m[주의사항]\033[0m

    • 양쪽 거래소에 동일 금액의 증거금 필요
    • 청산 위험 관리 필수 (낮은 레버리지 권장)
    • 거래소 간 가격 차이로 인한 일시적 손실 가능
    • 출금/입금 수수료 및 트레이딩 수수료 고려 필요
    • DEX(Hyperliquid, dYdX)는 1시간 펀딩, CEX는 8시간 펀딩
    """)


async def main_async():
    """Async main function"""
    print_header()

    fetcher = FundingRateFetcher()
    calculator = ArbitrageCalculator()

    try:
        print("Initializing exchange connections...")
        await fetcher.initialize()

        print("Fetching funding rates from all exchanges...\n")
        all_rates = await fetcher.fetch_all_funding_rates()

        # Check if we got any data
        total_pairs = sum(len(rates) for rates in all_rates.values())

        if total_pairs == 0:
            print("\n\033[93mNo data received from exchanges. Using sample data for demonstration...\033[0m\n")
            all_rates = get_sample_data()

        # Print summary
        print("-" * 60)
        print("DATA SUMMARY")
        print("-" * 60)
        for exchange, rates in all_rates.items():
            count = len(rates)
            print(f"  {exchange:15} : {count:4} pairs")
        print(f"  {'TOTAL':15} : {sum(len(r) for r in all_rates.values()):4} pairs")
        print("-" * 60)

        # Find opportunities
        print("\nCalculating arbitrage opportunities...\n")
        opportunities = calculator.find_arbitrage_opportunities(all_rates, min_apr=5.0)

        if opportunities:
            print_opportunities(opportunities, calculator, all_rates)
        else:
            print("No arbitrage opportunities found with APR >= 5%")

        print_strategy_guide()

    finally:
        await fetcher.close()


def main():
    """Main entry point"""
    if '--demo' in sys.argv or '--sample' in sys.argv:
        # Demo mode with sample data
        print_header()
        print("\033[93mRunning in DEMO mode with sample data...\033[0m\n")

        all_rates = get_sample_data()
        calculator = ArbitrageCalculator()

        print("-" * 60)
        print("DATA SUMMARY")
        print("-" * 60)
        for exchange, rates in all_rates.items():
            count = len(rates)
            print(f"  {exchange:15} : {count:4} pairs")
        print(f"  {'TOTAL':15} : {sum(len(r) for r in all_rates.values()):4} pairs")
        print("-" * 60)

        opportunities = calculator.find_arbitrage_opportunities(all_rates, min_apr=5.0)

        if opportunities:
            print_opportunities(opportunities, calculator, all_rates)

        print_strategy_guide()
    else:
        asyncio.run(main_async())


if __name__ == "__main__":
    main()
