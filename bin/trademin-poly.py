#!/usr/bin/env python

import argparse
import datetime
import os
import sys

try:
    # Poly is already in the system path, import as usual
    import poly
except ImportError:
    # This script is being run from the repository directly probably, just
    # check the parent directory for the packages instead
    PACKAGE_PARENT = '..'
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(
            os.path.join(os.getcwd(), os.path.expanduser(__file__))))
    sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
    import poly


def run_marketstatus(args):
    '''
    '''
    api_key = poly.load_api_key_from_path(args.config)
    poly.get_marketstatus(api_key)


def run_configure(args):
    '''
    '''
    if args.api_key:
        if args.api_key is not None:
            # We have a new key to save to our config file
            poly.save_api_key_to_path(args.api_key, args.overwrite, args.config)
        else:
            # Try to display the key found in the config
            api_key = poly.load_api_key_from_path(args.config)
            if api_key:
                print (f"API KEY found in {args.config}:\n\t {api_key}")
            else:
                print (f"API KEY not found in {args.config}")
    else:
        print ("How may a help you? Try `trademin-poly configure --help`")


def run_dividends(args):
    '''
    Display some basic information about a ticker's dividend events.
    '''
    api_key = poly.load_api_key_from_path(args.config)
    dividends = poly.get_dividends(api_key, args.tickers)
    for ticker, data in dividends.items():
        print (
        f'Summary: {ticker.upper()} as of {datetime.date.today()}\n'
        f'  Total:  {data.get("count", 0)}'
        )
        if data.get('count', 0) > 0:
            print (
            f'  Last:   ${data["last"]["amount"]} on {data["last"]["exDate"]}'
            )
            if data["next"].get("guess"):
                print (f'  Next:   {data["next"]["exDate"]} (ESTIMATE)')
            else:
                print (f'  Next:   {data["next"]["exDate"]}')
        print('---')


def run_aggregates(args):
    '''
    Display ticker data as JSON
    '''

    # FIXME: make CONVERTING timetamps to isoformat OPTIONAL
    api_key = poly.load_api_key_from_path(args.config)
    aggregates = poly.get_ticker_aggregates(
        api_key,
        ticker=args.ticker,
        from_=args.from_,
        to=args.to,
        multiplier=args.multiplier,
        timespan=args.timespan,
        unadjusted=args.unadjusted,
        sort=args.sort,
        limit=args.limit
        )

    if aggregates['resultsCount'] == 0:
        print ("No results returned!")
        return aggregates

    if not args.keep_epochs:
        modified_results = []
        for result in aggregates['results']:
            result['t'] = poly.timestamp_to_isoformat(result['t'])
            modified_results.append(result)
        aggregates['results'] = modified_results

    if args.save_as:
        poly.json_dump(args.save_as, aggregates['results'], True)
    return aggregates


# This runs the script when executed from the commandline
if __name__ == '__main__':
    '''
    ```$> trademin-poly COMMAND```
    Available commmands
    * configure    : interacts with the script's configure file
    * marketstatus : displays summary of current market status (open/closed)
    * dividends    : displays summary of dividends info for requested tickers
    * aggregates   : displays summary of ticker candle / bar data
    '''
    # Set-up the CLI parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default=poly.DEFAULT_CONFIG_PATH, help="")

    subparser = parser.add_subparsers(dest="command")

    # command: `configure`
    c_configure = subparser.add_parser("configure")
    c_configure.add_argument('--overwrite', action='store_true', default=False)
    c_configure.add_argument('--api-key', nargs="?", type=str, default=None)

    # commmand: `marketstatus`
    c_marketstatus = subparser.add_parser("marketstatus")

    # commmand: `dividends`
    c_dividends = subparser.add_parser("dividends")
    c_dividends.add_argument('tickers', nargs='+', type=str, default=None)

    # commmand: `aggregates`
    c_aggregates = subparser.add_parser("aggregates")
    c_aggregates.add_argument('ticker', type=str, default=None)
    c_aggregates.add_argument('--from_', type=str, default='yesterday')
    c_aggregates.add_argument('--to', type=str, default='yesterday')
    c_aggregates.add_argument('--unadjusted', type=str, default='yesterday')  # FIXME BOOLEAN
    c_aggregates.add_argument('--multiplier', type=int, default=1)
    c_aggregates.add_argument('--timespan', type=str, default='minute')
    c_aggregates.add_argument('--limit', type=int, default=5000)
    c_aggregates.add_argument('--sort', type=str, default='asc')
    c_aggregates.add_argument('--save-as', type=str)
    c_aggregates.add_argument('--keep-epochs', default=False, action='store_true')


    args = parser.parse_args()

    if args.command == 'marketstatus':
        run_marketstatus(args)
    elif args.command == 'configure':
        run_configure(args)
    elif args.command == 'dividends':
        run_dividends(args)
    elif args.command == 'aggregates':
        run_aggregates(args)
    else:
        print ("How may a help you? Try `trademin-poly --help`")
