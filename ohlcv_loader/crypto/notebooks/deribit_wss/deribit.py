class DeribitAPIAccessScope:
    def __init__(self, scope):
        self.scope = scope
        self.main()

    def main(self):
        if self.scope == 'read-only':
            self.account_scope = "read"
            self.trade_scope = "read"
            self.wallet_scope = "read"
            self.block_scope = "read"
            self.custody = "read_write"  # Must be 'read_write' for the moment given the present API implementation           # noqa: E501
            self.designated_scope = "account:{} trade:{} wallet:{} block_trade:{} custody:{}".format(
                self.account_scope,  # noqa: E501
                self.trade_scope,  # noqa: E501
                self.wallet_scope,  # noqa: E501
                self.block_scope,  # noqa: E501
                self.custody  # noqa: E501
            )  # noqa: E501
            print('Scope Definition: You are using "{}" access'.format(self.scope))  # noqa: E501
        elif self.scope == 'read-write':
            self.account_scope = "read_write"
            self.trade_scope = "read_write"
            self.wallet_scope = "read_write"
            self.block_scope = "read_write"
            self.custody = "read_write"
            self.designated_scope = "account:{} trade:{} wallet:{} block_trade:{} custody:{}".format(  # noqa: E501
                self.account_scope,  # noqa: E501
                self.trade_scope,  # noqa: E501
                self.wallet_scope,  # noqa: E501
                self.block_scope,  # noqa: E501
                self.custody  # noqa: E501
            )  # noqa: E501
            print('Scope Definition: You are using "{}" access'.format(self.scope))  # noqa: E501
        else:
            self.designated_scope = self.scope
            print(
                'Invalid Scope Definition: "{}" is not an accepted scope definition. Please try "read-only" or "read-write".'.format(
                    self.scope))  # noqa: E501
            print('You will receive inconsistent scope definitions.')

        return self.designated_scope


class DeribitExchangeVersion:
    def __init__(self, exchange_version):
        self.exchange_version = exchange_version
        self.main()

    def main(self):
        if self.exchange_version == 'live':
            self.exchange_version = 'wss://www.deribit.com/ws/api/v2/'
        elif self.exchange_version == 'testnet':
            self.exchange_version = 'wss://test.deribit.com/ws/api/v2/'
        else:
            print('Invalid Exchange Version, please try "live" or "testnet"')

        return self.exchange_version
