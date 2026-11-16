"""
: ! LightCore !
    + Discord: lightcore
    + Community: https://discord.gg/8qe98sAGs9 (LightCore Development )
    + for any queries reach out Community or DM me.
"""
import discord
from discord.ext import commands
import aiohttp
from typing import Optional
from utils.Tools import *
from utils.logger import logger
import time


class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.network_map = {
            "btc": "bitcoin",
            "bitcoin": "bitcoin",
            "ltc": "litecoin",
            "litecoin": "litecoin",
            "eth": "ethereum",
            "ethereum": "ethereum"
        }
        
        self.network_display = {
            "bitcoin": "Bitcoin (BTC)",
            "litecoin": "Litecoin (LTC)",
            "ethereum": "Ethereum (ETH)"
        }


    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if hasattr(self, "session") and not self.session.closed:
            await self.session.close()

    @commands.hybrid_group(
        name="crypto",
        help="Cryptocurrency related commands",
        invoke_without_command=True
    )
    @blacklist_check()
    @ignore_check()
    async def crypto(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.reply(f"Please use a subcommand. Example: `{ctx.prefix}crypto balance btc <address>`")

    async def fetch_balance_blockchair(self, network_name: str, address: str):
        api_url = f"https://api.blockchair.com/{network_name}/dashboards/address/{address}"
        async with self.session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                if 'data' in data and address in data['data']:
                    address_data = data['data'][address]['address']
                    balance_raw = address_data.get('balance', 0)
                    
                    if network_name in ["bitcoin", "litecoin"]:
                        balance = balance_raw / 100000000
                        received = address_data.get('received', 0) / 100000000
                        spent = address_data.get('spent', 0) / 100000000
                    else:
                        balance = balance_raw / 1000000000000000000
                        received = address_data.get('received', 0) / 1000000000000000000
                        spent = address_data.get('spent', 0) / 1000000000000000000
                    
                    return {
                        'balance': balance,
                        'received': received,
                        'spent': spent,
                        'transactions': address_data.get('transaction_count', 0),
                        'source': 'Blockchair'
                    }
        return None

    async def fetch_balance_blockcypher(self, network_name: str, address: str):
        network_map = {"bitcoin": "btc", "litecoin": "ltc", "ethereum": "eth"}
        if network_name not in network_map:
            return None
        
        coin = network_map[network_name]
        api_url = f"https://api.blockcypher.com/v1/{coin}/main/addrs/{address}/balance"
        
        async with self.session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                balance_raw = data.get('balance', 0)
                
                if network_name in ["bitcoin", "litecoin"]:
                    balance = balance_raw / 100000000
                    received = data.get('total_received', 0) / 100000000
                    spent = data.get('total_sent', 0) / 100000000
                else:
                    balance = balance_raw / 1000000000000000000
                    received = data.get('total_received', 0) / 1000000000000000000
                    spent = data.get('total_sent', 0) / 1000000000000000000
                
                return {
                    'balance': balance,
                    'received': received,
                    'spent': spent,
                    'transactions': data.get('n_tx', 0),
                    'source': 'BlockCypher'
                }
        return None

    async def fetch_balance_blockchain_info(self, address: str):
        api_url = f"https://blockchain.info/balance?active={address}"
        async with self.session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                if address in data:
                    addr_data = data[address]
                    balance = addr_data.get('final_balance', 0) / 100000000
                    received = addr_data.get('total_received', 0) / 100000000
                    spent = addr_data.get('total_sent', 0) / 100000000
                    
                    return {
                        'balance': balance,
                        'received': received,
                        'spent': spent,
                        'transactions': addr_data.get('n_tx', 0),
                        'source': 'Blockchain.info'
                    }
        return None

    @crypto.command(
        name="balance",
        help="Check cryptocurrency balance for a wallet address",
        usage="crypto balance <network> <address>"
    )
    @discord.app_commands.describe(
        network="Choose cryptocurrency network: BTC, LTC, or ETH",
        address="The wallet address to check balance for"
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def balance(self, ctx: commands.Context, network: str, address: str):
        network_lower = network.lower()
        
        if network_lower not in self.network_map:
            await ctx.reply("❌ Invalid network. Please use: **BTC**, **LTC**, or **ETH**")
            return
        
        network_name = self.network_map[network_lower]
        symbol = network.upper()
        
        loading_view = discord.ui.LayoutView()
        loading_container = discord.ui.Container(
            discord.ui.TextDisplay(f"🔍 **Checking balance...**\n\nFetching {self.network_display[network_name]} balance..."),
            accent_color=None
        )
        loading_view.add_item(loading_container)
        processing_msg = await ctx.send(view=loading_view)

        try:
            result = None
            
            result = await self.fetch_balance_blockchair(network_name, address)
            
            if not result:
                result = await self.fetch_balance_blockcypher(network_name, address)
            
            if not result and network_name == "bitcoin":
                result = await self.fetch_balance_blockchain_info(address)
            
            if result:
                view = discord.ui.LayoutView()
                container = discord.ui.Container(accent_color=None)
                
                container.add_item(discord.ui.TextDisplay(f"# 💰 Crypto Balance"))
                container.add_item(discord.ui.Separator())
                
                balance_info = f"**Network:** {self.network_display[network_name]}\n**Address:** `{address[:10]}...{address[-10:]}`\n**Current Balance:** `{result['balance']:.8f} {symbol}`"
                container.add_item(discord.ui.TextDisplay(balance_info))
                
                container.add_item(discord.ui.Separator())
                
                stats_info = f"**Total Received:** `{result['received']:.8f} {symbol}`\n**Total Spent:** `{result['spent']:.8f} {symbol}`\n**Transactions:** `{result['transactions']}`"
                container.add_item(discord.ui.TextDisplay(stats_info))
                
                view.add_item(container)
                await processing_msg.edit(view=view)
            else:
                error_view = discord.ui.LayoutView()
                error_container = discord.ui.Container(
                    discord.ui.TextDisplay(f"❌ **Error**\n\nCould not fetch balance from any API. The address may be invalid or all APIs are currently unavailable."),
                    accent_color=None
                )
                error_view.add_item(error_container)
                await processing_msg.edit(view=error_view)
                    
        except Exception as e:
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay(f"❌ **Error**\n\nAn error occurred: {str(e)}"),
                accent_color=None
            )
            error_view.add_item(error_container)
            await processing_msg.edit(view=error_view)

    async def fetch_conversion_coingecko(self, from_id: str, to_id: str):
        api_url = f"https://api.coingecko.com/api/v3/simple/price?ids={from_id}&vs_currencies={to_id}"
        try:
            async with self.session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if from_id in data and to_id in data[from_id]:
                        return data[from_id][to_id]
        except Exception as e:
            logger.error("CRYPTO", f"CoinGecko error: {e}")
        return None

    async def fetch_conversion_coincap(self, from_id: str, to_id: str, fiat_currencies: dict):
        try:
            if to_id in fiat_currencies:
                from_url = f"https://api.coincap.io/v2/assets/{from_id}"
                async with self.session.get(from_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'data' in data and 'priceUsd' in data['data']:
                            price_usd = float(data['data']['priceUsd'])
                            return price_usd
            
            elif from_id in fiat_currencies and to_id not in fiat_currencies:
                to_url = f"https://api.coincap.io/v2/assets/{to_id}"
                async with self.session.get(to_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'data' in data and 'priceUsd' in data['data']:
                            price_usd = float(data['data']['priceUsd'])
                            return 1 / price_usd
            
            else:
                from_url = f"https://api.coincap.io/v2/assets/{from_id}"
                to_url = f"https://api.coincap.io/v2/assets/{to_id}"
                
                async with self.session.get(from_url, timeout=10) as from_response:
                    if from_response.status == 200:
                        from_data = await from_response.json()
                        if 'data' in from_data and 'priceUsd' in from_data['data']:
                            from_price_usd = float(from_data['data']['priceUsd'])
                            
                            async with self.session.get(to_url, timeout=10) as to_response:
                                if to_response.status == 200:
                                    to_data = await to_response.json()
                                    if 'data' in to_data and 'priceUsd' in to_data['data']:
                                        to_price_usd = float(to_data['data']['priceUsd'])
                                        rate = from_price_usd / to_price_usd
                                        return rate
        except Exception as e:
            logger.error("CRYPTO", f"CoinCap error: {e}")
        return None

    async def fetch_conversion_cryptocompare(self, from_curr: str, to_curr: str):
        try:
            api_url = f"https://min-api.cryptocompare.com/data/price?fsym={from_curr.upper()}&tsyms={to_curr.upper()}"
            async with self.session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if to_curr.upper() in data:
                        return float(data[to_curr.upper()])
        except Exception as e:
            logger.error("CRYPTO", f"CryptoCompare error: {e}")
        return None

    async def fetch_conversion_binance(self, from_curr: str, to_curr: str):
        try:
            symbol = f"{from_curr.upper()}{to_curr.upper()}"
            api_url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            async with self.session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'price' in data:
                        return float(data['price'])
            
            symbol_reversed = f"{to_curr.upper()}{from_curr.upper()}"
            api_url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol_reversed}"
            async with self.session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'price' in data:
                        return 1 / float(data['price'])
        except Exception as e:
            logger.error("CRYPTO", f"Binance error: {e}")
        return None

    async def fetch_conversion_kraken(self, from_curr: str, to_curr: str):
        try:
            pair_map = {
                ("btc", "usd"): "XXBTZUSD",
                ("eth", "usd"): "XETHZUSD",
                ("ltc", "usd"): "XLTCZUSD",
                ("btc", "eur"): "XXBTZEUR",
                ("eth", "eur"): "XETHZEUR",
            }
            
            pair_key = (from_curr.lower(), to_curr.lower())
            if pair_key in pair_map:
                pair = pair_map[pair_key]
                api_url = f"https://api.kraken.com/0/public/Ticker?pair={pair}"
                async with self.session.get(api_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'result' in data and pair in data['result']:
                            price = float(data['result'][pair]['c'][0])
                            return price
        except Exception as e:
            logger.error("CRYPTO", f"Kraken error: {e}")
        return None

    @crypto.command(
        name="convert",
        help="Convert cryptocurrency from one to another",
        usage="crypto convert <from> <to> <amount>"
    )
    @discord.app_commands.describe(
        from_currency="Cryptocurrency to convert from (e.g., BTC, ETH, LTC)",
        to_currency="Cryptocurrency/currency to convert to (e.g., BTC, ETH, USD)",
        amount="Amount to convert"
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def convert(self, ctx: commands.Context, from_currency: str, to_currency: str, amount: float):
        if amount <= 0:
            await ctx.reply("❌ Amount must be greater than 0")
            return
        
        loading_view = discord.ui.LayoutView()
        loading_container = discord.ui.Container(
            discord.ui.TextDisplay(f"🔄 **Converting...**\n\nCalculating conversion rate..."),
            accent_color=None
        )
        loading_view.add_item(loading_container)
        processing_msg = await ctx.send(view=loading_view)

        try:
            from_curr = from_currency.lower()
            to_curr = to_currency.lower()
            
            crypto_id_map = {
                "btc": "bitcoin",
                "bitcoin": "bitcoin",
                "eth": "ethereum",
                "ethereum": "ethereum",
                "ltc": "litecoin",
                "litecoin": "litecoin",
                "doge": "dogecoin",
                "dogecoin": "dogecoin",
                "xrp": "ripple",
                "ripple": "ripple",
                "ada": "cardano",
                "cardano": "cardano",
                "dot": "polkadot",
                "polkadot": "polkadot",
                "bnb": "binancecoin",
                "binancecoin": "binancecoin",
                "sol": "solana",
                "solana": "solana",
                "matic": "matic-network",
                "polygon": "matic-network",
                "link": "chainlink",
                "chainlink": "chainlink",
                "avax": "avalanche-2",
                "avalanche": "avalanche-2"
            }
            
            from_id = crypto_id_map.get(from_curr, from_curr)
            to_id = crypto_id_map.get(to_curr, to_curr)
            
            fiat_currencies = {"usd": True, "eur": True, "gbp": True, "jpy": True, "cad": True, "aud": True}
            
            rate = None
            
            rate = await self.fetch_conversion_coingecko(from_id, to_id)
            
            if not rate:
                rate = await self.fetch_conversion_cryptocompare(from_curr, to_curr)
            
            if not rate:
                rate = await self.fetch_conversion_binance(from_curr, to_curr)
            
            if not rate:
                rate = await self.fetch_conversion_kraken(from_curr, to_curr)
            
            if rate:
                converted_amount = amount * rate
                
                view = discord.ui.LayoutView()
                container = discord.ui.Container(accent_color=None)
                
                container.add_item(discord.ui.TextDisplay(f"# 🔄 Crypto Conversion"))
                container.add_item(discord.ui.Separator())
                
                conversion_info = f"**From:** `{amount:,.8f} {from_currency.upper()}`\n**To:** `{converted_amount:,.8f} {to_currency.upper()}`"
                container.add_item(discord.ui.TextDisplay(conversion_info))
                
                container.add_item(discord.ui.Separator())
                
                rate_info = f"**Exchange Rate:** `1 {from_currency.upper()} = {rate:,.8f} {to_currency.upper()}`"
                container.add_item(discord.ui.TextDisplay(rate_info))
                
                view.add_item(container)
                await processing_msg.edit(view=view)
            else:
                error_view = discord.ui.LayoutView()
                error_container = discord.ui.Container(
                    discord.ui.TextDisplay(f"❌ **Invalid Currency**\n\nCould not find conversion rate from any API. Please check the currency codes.\n\nSupported: BTC, ETH, LTC, DOGE, XRP, ADA, DOT, BNB, SOL, MATIC, LINK, AVAX, USD, EUR, etc."),
                    accent_color=None
                )
                error_view.add_item(error_container)
                await processing_msg.edit(view=error_view)
                    
        except Exception as e:
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay(f"❌ **Error**\n\nAn error occurred: {str(e)}"),
                accent_color=None
            )
            error_view.add_item(error_container)
            await processing_msg.edit(view=error_view)

    @crypto.command(
        name="transaction",
        help="Get transaction details by hash",
        usage="crypto transaction <network> <hash>"
    )
    @discord.app_commands.describe(
        network="Cryptocurrency network: BTC, LTC, or ETH",
        hash="Transaction hash/ID"
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def transaction(self, ctx: commands.Context, network: str, hash: str):
        network_lower = network.lower()
        
        if network_lower not in self.network_map:
            await ctx.reply("❌ Invalid network. Please use: **BTC**, **LTC**, or **ETH**")
            return
        
        network_name = self.network_map[network_lower]
        
        loading_view = discord.ui.LayoutView()
        loading_container = discord.ui.Container(
            discord.ui.TextDisplay(f"🔍 **Fetching transaction...**\n\nLooking up transaction details..."),
            accent_color=None
        )
        loading_view.add_item(loading_container)
        processing_msg = await ctx.send(view=loading_view)

        try:
            api_url = f"https://api.blockchair.com/{network_name}/dashboards/transaction/{hash}"
            
            async with self.session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'data' in data and hash in data['data']:
                        tx_data = data['data'][hash]['transaction']
                        
                        if network_name in ["bitcoin", "litecoin"]:
                            value = tx_data.get('output_total', 0) / 100000000
                            fee = tx_data.get('fee', 0) / 100000000
                        else:
                            value = tx_data.get('value', 0) / 1000000000000000000
                            fee = tx_data.get('fee', 0) / 1000000000000000000
                        
                        confirmations = tx_data.get('block_id', 0)
                        time_stamp = tx_data.get('time', None)
                        
                        view = discord.ui.LayoutView()
                        container = discord.ui.Container(accent_color=None)
                        
                        container.add_item(discord.ui.TextDisplay(f"# 🔗 Transaction Details"))
                        container.add_item(discord.ui.Separator())
                        
                        tx_info = f"**Network:** {self.network_display[network_name]}\n**Hash:** `{hash[:16]}...{hash[-16:]}`"
                        container.add_item(discord.ui.TextDisplay(tx_info))
                        
                        container.add_item(discord.ui.Separator())
                        
                        details = f"**Value:** `{value:.8f} {network.upper()}`\n**Fee:** `{fee:.8f} {network.upper()}`\n**Confirmations:** `{confirmations if confirmations > 0 else 'Pending'}`"
                        if time_stamp:
                            details += f"\n**Time:** <t:{time_stamp}:F>"
                        container.add_item(discord.ui.TextDisplay(details))
                        
                        view.add_item(container)
                        await processing_msg.edit(view=view)
                    else:
                        error_view = discord.ui.LayoutView()
                        error_container = discord.ui.Container(
                            discord.ui.TextDisplay(f"❌ **Transaction Not Found**\n\nCould not find transaction with this hash."),
                            accent_color=None
                        )
                        error_view.add_item(error_container)
                        await processing_msg.edit(view=error_view)
                else:
                    error_view = discord.ui.LayoutView()
                    error_container = discord.ui.Container(
                        discord.ui.TextDisplay(f"❌ **API Error**\n\nFailed to fetch transaction. Please try again later."),
                        accent_color=None
                    )
                    error_view.add_item(error_container)
                    await processing_msg.edit(view=error_view)
                    
        except Exception as e:
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay(f"❌ **Error**\n\nAn error occurred: {str(e)}"),
                accent_color=None
            )
            error_view.add_item(error_container)
            await processing_msg.edit(view=error_view)

    async def fetch_news_cryptopanic(self):
        """Fetch news from CryptoPanic API"""
        try:
            api_url = "https://cryptopanic.com/api/v1/posts/?auth_token=free&public=true&kind=news"
            async with self.session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'results' in data:
                        news_items = []
                        for item in data['results'][:5]:
                            news_items.append({
                                'title': item.get('title', 'No title'),
                                'url': item.get('url', ''),
                                'source': item.get('source', {}).get('title', 'Unknown'),
                                'published_at': item.get('published_at', ''),
                                'currencies': ', '.join([c.get('code', '') for c in item.get('currencies', [])[:3]])
                            })
                        return news_items
        except Exception as e:
            logger.error("CRYPTO", f"CryptoPanic error: {e}")
        return None

    async def fetch_news_cryptocompare(self):
        """Fetch news from CryptoCompare API"""
        try:
            api_url = "https://min-api.cryptocompare.com/data/v2/news/?lang=EN"
            async with self.session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'Data' in data:
                        news_items = []
                        for item in data['Data'][:5]:
                            news_items.append({
                                'title': item.get('title', 'No title'),
                                'url': item.get('url', ''),
                                'source': item.get('source', 'Unknown'),
                                'published_at': item.get('published_on', ''),
                                'body': item.get('body', '')[:200] + '...'
                            })
                        return news_items
        except Exception as e:
            logger.error("CRYPTO", f"CryptoCompare error: {e}")
        return None

    async def fetch_news_coingecko(self):
        """Fetch news from CoinGecko API"""
        try:
            api_url = "https://api.coingecko.com/api/v3/news"
            async with self.session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data:
                        news_items = []
                        for item in data['data'][:5]:
                            news_items.append({
                                'title': item.get('title', 'No title'),
                                'url': item.get('url', ''),
                                'source': item.get('author', 'Unknown'),
                                'published_at': item.get('updated_at', ''),
                                'description': item.get('description', '')[:200] + '...'
                            })
                        return news_items
        except Exception as e:
            logger.error("CRYPTO", f"CoinGecko error: {e}")
        return None

    async def fetch_news_newsapi(self):
        """Fetch news from NewsAPI (crypto related)"""
        try:
            api_url = "https://newsapi.org/v2/everything?q=cryptocurrency&sortBy=publishedAt&pageSize=5&language=en&apiKey=demo"
            async with self.session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'articles' in data:
                        news_items = []
                        for item in data['articles'][:5]:
                            news_items.append({
                                'title': item.get('title', 'No title'),
                                'url': item.get('url', ''),
                                'source': item.get('source', {}).get('name', 'Unknown'),
                                'published_at': item.get('publishedAt', ''),
                                'description': item.get('description', '')[:200] + '...'
                            })
                        return news_items
        except Exception as e:
            logger.error("CRYPTO", f"NewsAPI error: {e}")
        return None

    @crypto.command(
        name="news",
        help="Get top 5 cryptocurrency news from the last 24 hours",
        usage="crypto news"
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def news(self, ctx: commands.Context):
        loading_view = discord.ui.LayoutView()
        loading_container = discord.ui.Container(
            discord.ui.TextDisplay(f"📰 **Fetching crypto news...**\n\nGathering the latest cryptocurrency news..."),
            accent_color=None
        )
        loading_view.add_item(loading_container)
        processing_msg = await ctx.send(view=loading_view)

        try:
            news_items = None
            
            news_items = await self.fetch_news_cryptocompare()
            
            if not news_items:
                news_items = await self.fetch_news_cryptopanic()
            
            if not news_items:
                news_items = await self.fetch_news_coingecko()
            
            if not news_items:
                news_items = await self.fetch_news_newsapi()
            
            if news_items and len(news_items) > 0:
                current_index = 0
                
                async def create_news_view(index: int):
                    layout_view = discord.ui.LayoutView(timeout=300.0)
                    container = discord.ui.Container(accent_color=None)
                    
                    container.add_item(discord.ui.TextDisplay(f"# 📰 Crypto News ({index + 1}/{len(news_items)})"))
                    container.add_item(discord.ui.Separator())
                    
                    item = news_items[index]
                    title = item.get('title', 'No title')
                    url = item.get('url', '')
                    source = item.get('source', 'Unknown')
                    
                    description = item.get('description', item.get('body', ''))
                    if not description:
                        description = "No description available."
                    
                    news_text = f"**{title}**\n\n{description}\n\n**Source:** {source}"
                    
                    if url:
                        news_text += f"\n[Read More]({url})"
                    
                    if 'currencies' in item and item['currencies']:
                        news_text += f"\n**Related:** {item['currencies']}"
                    
                    container.add_item(discord.ui.TextDisplay(news_text))
                    
                    container.add_item(discord.ui.Separator())
                    
                    button_row = discord.ui.ActionRow(
                        discord.ui.Button(
                            label="",
                            emoji="<:SageDoubleArrowLeft:1385846432535412758>",
                            custom_id="news_first",
                            style=discord.ButtonStyle.secondary
                        ),
                        discord.ui.Button(
                            label="",
                            emoji="<:arrow_left:1385846548625363117>",
                            custom_id="news_prev",
                            style=discord.ButtonStyle.secondary
                        ),
                        discord.ui.Button(
                            label="",
                            emoji="<:arrow_right:1385846525204103252>",
                            custom_id="news_next",
                            style=discord.ButtonStyle.secondary
                        ),
                        discord.ui.Button(
                            label="",
                            emoji="<:SageDoubleArrowRight:1385846409902948362>",
                            custom_id="news_last",
                            style=discord.ButtonStyle.secondary
                        )
                    )
                    container.add_item(button_row)
                    
                    layout_view.add_item(container)
                    return layout_view
                
                initial_view = await create_news_view(current_index)
                await processing_msg.edit(view=initial_view)
                
                def check(interaction: discord.Interaction):
                    return interaction.user.id == ctx.author.id and interaction.message.id == processing_msg.id
                
                while True:
                    try:
                        interaction = await self.bot.wait_for('interaction', timeout=300.0, check=check)
                        
                        custom_id = interaction.data.get('custom_id')
                        
                        if custom_id == 'news_first':
                            current_index = 0
                        elif custom_id == 'news_prev':
                            current_index = (current_index - 1) % len(news_items)
                        elif custom_id == 'news_next':
                            current_index = (current_index + 1) % len(news_items)
                        elif custom_id == 'news_last':
                            current_index = len(news_items) - 1
                        
                        updated_view = await create_news_view(current_index)
                        await interaction.response.edit_message(view=updated_view)
                        
                    except:
                        try:
                            expired_view = discord.ui.LayoutView()
                            expired_container = discord.ui.Container(accent_color=None)
                            expired_container.add_item(discord.ui.TextDisplay("# Container Expired\nPlease use the command again"))
                            expired_view.add_item(expired_container)
                            await processing_msg.edit(view=expired_view)
                        except:
                            pass
                        break
            else:
                error_view = discord.ui.LayoutView()
                error_container = discord.ui.Container(
                    discord.ui.TextDisplay(f"❌ **No News Available**\n\nCould not fetch crypto news at this time. All APIs are currently unavailable. Please try again later."),
                    accent_color=None
                )
                error_view.add_item(error_container)
                await processing_msg.edit(view=error_view)
                    
        except Exception as e:
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay(f"❌ **Error**\n\nAn error occurred: {str(e)}"),
                accent_color=None
            )
            error_view.add_item(error_container)
            await processing_msg.edit(view=error_view)

    @crypto.command(
        name="gainers",
        help="Get top 10 cryptocurrencies with highest gains in last 24 hours",
        usage="crypto gainers"
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def gainers(self, ctx: commands.Context):
        loading_view = discord.ui.LayoutView()
        loading_container = discord.ui.Container(
            discord.ui.TextDisplay(f"📈 **Fetching top gainers...**\n\nGathering the biggest winners from the last 24 hours..."),
            accent_color=None
        )
        loading_view.add_item(loading_container)
        processing_msg = await ctx.send(view=loading_view)

        try:
            api_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=24h"
            
            async with self.session.get(api_url, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    gainers_data = [coin for coin in data if coin.get('price_change_percentage_24h') and coin.get('price_change_percentage_24h') > 0]
                    gainers_data.sort(key=lambda x: x.get('price_change_percentage_24h', 0), reverse=True)
                    top_gainers = gainers_data[:10]
                    
                    if top_gainers:
                        view = discord.ui.LayoutView()
                        container = discord.ui.Container(accent_color=None)
                        
                        container.add_item(discord.ui.TextDisplay(f"# 📈 Top 10 Crypto Gainers (24h)"))
                        container.add_item(discord.ui.Separator())
                        
                        gainers_text = ""
                        for idx, coin in enumerate(top_gainers, 1):
                            name = coin.get('name', 'Unknown')
                            symbol = coin.get('symbol', '').upper()
                            price = coin.get('current_price', 0)
                            change = coin.get('price_change_percentage_24h', 0)
                            
                            gainers_text += f"**{idx}. {name} ({symbol})**\n"
                            gainers_text += f"   Price: `${price:,.4f}` | Change: `+{change:.2f}%`\n\n"
                        
                        container.add_item(discord.ui.TextDisplay(gainers_text.strip()))
                        
                        view.add_item(container)
                        await processing_msg.edit(view=view)
                    else:
                        error_view = discord.ui.LayoutView()
                        error_container = discord.ui.Container(
                            discord.ui.TextDisplay(f"❌ **No Data**\n\nCould not find any gainers data."),
                            accent_color=None
                        )
                        error_view.add_item(error_container)
                        await processing_msg.edit(view=error_view)
                else:
                    error_view = discord.ui.LayoutView()
                    error_container = discord.ui.Container(
                        discord.ui.TextDisplay(f"❌ **API Error**\n\nFailed to fetch gainers. Please try again later."),
                        accent_color=None
                    )
                    error_view.add_item(error_container)
                    await processing_msg.edit(view=error_view)
                    
        except Exception as e:
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay(f"❌ **Error**\n\nAn error occurred: {str(e)}"),
                accent_color=None
            )
            error_view.add_item(error_container)
            await processing_msg.edit(view=error_view)

    @crypto.command(
        name="losers",
        help="Get top 10 cryptocurrencies with highest losses in last 24 hours",
        usage="crypto losers"
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def losers(self, ctx: commands.Context):
        loading_view = discord.ui.LayoutView()
        loading_container = discord.ui.Container(
            discord.ui.TextDisplay(f"📉 **Fetching top losers...**\n\nGathering the biggest losers from the last 24 hours..."),
            accent_color=None
        )
        loading_view.add_item(loading_container)
        processing_msg = await ctx.send(view=loading_view)

        try:
            api_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=24h"
            
            async with self.session.get(api_url, timeout=15) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    losers_data = [coin for coin in data if coin.get('price_change_percentage_24h') and coin.get('price_change_percentage_24h') < 0]
                    losers_data.sort(key=lambda x: x.get('price_change_percentage_24h', 0))
                    top_losers = losers_data[:10]
                    
                    if top_losers:
                        view = discord.ui.LayoutView()
                        container = discord.ui.Container(accent_color=None)
                        
                        container.add_item(discord.ui.TextDisplay(f"# 📉 Top 10 Crypto Losers (24h)"))
                        container.add_item(discord.ui.Separator())
                        
                        losers_text = ""
                        for idx, coin in enumerate(top_losers, 1):
                            name = coin.get('name', 'Unknown')
                            symbol = coin.get('symbol', '').upper()
                            price = coin.get('current_price', 0)
                            change = coin.get('price_change_percentage_24h', 0)
                            
                            losers_text += f"**{idx}. {name} ({symbol})**\n"
                            losers_text += f"   Price: `${price:,.4f}` | Change: `{change:.2f}%`\n\n"
                        
                        container.add_item(discord.ui.TextDisplay(losers_text.strip()))
                        
                        view.add_item(container)
                        await processing_msg.edit(view=view)
                    else:
                        error_view = discord.ui.LayoutView()
                        error_container = discord.ui.Container(
                            discord.ui.TextDisplay(f"❌ **No Data**\n\nCould not find any losers data."),
                            accent_color=None
                        )
                        error_view.add_item(error_container)
                        await processing_msg.edit(view=error_view)
                else:
                    error_view = discord.ui.LayoutView()
                    error_container = discord.ui.Container(
                        discord.ui.TextDisplay(f"❌ **API Error**\n\nFailed to fetch losers. Please try again later."),
                        accent_color=None
                    )
                    error_view.add_item(error_container)
                    await processing_msg.edit(view=error_view)
                    
        except Exception as e:
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay(f"❌ **Error**\n\nAn error occurred: {str(e)}"),
                accent_color=None
            )
            error_view.add_item(error_container)
            await processing_msg.edit(view=error_view)

    @crypto.command(
        name="price",
        help="Get current price of a cryptocurrency",
        usage="crypto price <network>"
    )
    @discord.app_commands.describe(
        network="Cryptocurrency to check price for (BTC, ETH, LTC, DOGE, etc.)"
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def price(self, ctx: commands.Context, network: str):
        loading_view = discord.ui.LayoutView()
        loading_container = discord.ui.Container(
            discord.ui.TextDisplay(f"📊 **Fetching price...**\n\nGetting current market price..."),
            accent_color=None
        )
        loading_view.add_item(loading_container)
        processing_msg = await ctx.send(view=loading_view)

        try:
            network_lower = network.lower()
            
            crypto_id_map = {
                "btc": "bitcoin",
                "bitcoin": "bitcoin",
                "eth": "ethereum",
                "ethereum": "ethereum",
                "ltc": "litecoin",
                "litecoin": "litecoin",
                "doge": "dogecoin",
                "dogecoin": "dogecoin",
                "xrp": "ripple",
                "ripple": "ripple",
                "ada": "cardano",
                "cardano": "cardano",
                "dot": "polkadot",
                "polkadot": "polkadot",
                "bnb": "binancecoin",
                "binancecoin": "binancecoin",
                "sol": "solana",
                "solana": "solana",
                "matic": "matic-network",
                "polygon": "matic-network",
                "link": "chainlink",
                "chainlink": "chainlink",
                "avax": "avalanche-2",
                "avalanche": "avalanche-2"
            }
            
            crypto_id = crypto_id_map.get(network_lower, network_lower)
            
            api_url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd,eur,gbp&include_24hr_change=true&include_market_cap=true"
            
            async with self.session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if crypto_id in data:
                        price_data = data[crypto_id]
                        usd_price = price_data.get('usd', 0)
                        eur_price = price_data.get('eur', 0)
                        gbp_price = price_data.get('gbp', 0)
                        change_24h = price_data.get('usd_24h_change', 0)
                        market_cap = price_data.get('usd_market_cap', 0)
                        
                        change_emoji = "📈" if change_24h > 0 else "📉"
                        change_sign = "+" if change_24h > 0 else ""
                        
                        view = discord.ui.LayoutView()
                        container = discord.ui.Container(accent_color=None)
                        
                        container.add_item(discord.ui.TextDisplay(f"# 💰 {network.upper()} Price"))
                        container.add_item(discord.ui.Separator())
                        
                        price_info = f"**USD:** `${usd_price:,.2f}`\n**EUR:** `€{eur_price:,.2f}`\n**GBP:** `£{gbp_price:,.2f}`"
                        container.add_item(discord.ui.TextDisplay(price_info))
                        
                        container.add_item(discord.ui.Separator())
                        
                        stats = f"{change_emoji} **24h Change:** `{change_sign}{change_24h:.2f}%`\n**Market Cap:** `${market_cap:,.0f}`"
                        container.add_item(discord.ui.TextDisplay(stats))
                        
                        view.add_item(container)
                        await processing_msg.edit(view=view)
                    else:
                        error_view = discord.ui.LayoutView()
                        error_container = discord.ui.Container(
                            discord.ui.TextDisplay(f"❌ **Invalid Cryptocurrency**\n\nCould not find price data.\n\nSupported: BTC, ETH, LTC, DOGE, XRP, ADA, DOT, BNB, SOL, MATIC, LINK, AVAX"),
                            accent_color=None
                        )
                        error_view.add_item(error_container)
                        await processing_msg.edit(view=error_view)
                else:
                    error_view = discord.ui.LayoutView()
                    error_container = discord.ui.Container(
                        discord.ui.TextDisplay(f"❌ **API Error**\n\nFailed to fetch price. Please try again later."),
                        accent_color=None
                    )
                    error_view.add_item(error_container)
                    await processing_msg.edit(view=error_view)
                    
        except Exception as e:
            error_view = discord.ui.LayoutView()
            error_container = discord.ui.Container(
                discord.ui.TextDisplay(f"❌ **Error**\n\nAn error occurred: {str(e)}"),
                accent_color=None
            )
            error_view.add_item(error_container)
            await processing_msg.edit(view=error_view)


async def setup(bot):
    await bot.add_cog(Crypto(bot))
