def analysis_ops_transaction_type(data):
    transaction_class_list = ['altcoinx.RfsOffPlatformTradeTransaction', 'altcoinx.RfsFloatTransaction',
                              'altcoinx.RfsHedgedOffPlatformTradeTransaction', 'altcoinx.RfsTradeTransaction']
    for transaction_type in data:
        if transaction_type in transaction_class_list:
            transaction_class_list.remove(transaction_type)
    return transaction_class_list

