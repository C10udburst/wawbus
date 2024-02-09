from os import environ

from .main import WawBus


def __main__():
    import argparse

    parser = argparse.ArgumentParser(description="Collect bus positions from api.um.warszawa.pl")
    parser.add_argument("--apikey", help="api.um.warszawa.pl API key. If set to 'env', will use WAWBUS_APIKEY."
                                         "environment variable")
    parser.add_argument("--type", help="What to collect",
                        default="positions", choices=["positions", "timetable", "stops"])
    parser.add_argument("--count", help="number of collections", type=int, default=25)
    parser.add_argument("--retry", help="number of retries", type=int, default=3)
    parser.add_argument("--sleep", help="sleep between collections", type=int, default=10)
    parser.add_argument("--workers", help="number of workers when collecting timetables", type=int, default=5)
    parser.add_argument("--output", help="output file")

    args = parser.parse_args()

    if not args.apikey:
        raise ValueError("API key is required.")
    if not args.output:
        raise ValueError("Output file is required.")

    if args.apikey == "env":
        args.apikey = environ.get("WAWBUS_APIKEY")

    wb = WawBus(apikey=args.apikey, retry_count=args.retry)
    wb.tt_worker_count = args.workers

    if args.type == "positions":
        wb.collect_positions(args.count, args.sleep)
        df = wb.dataset
    elif args.type == "timetable":
        wb.collect_timetables()
        df = wb.tt
    elif args.type == "stops":
        wb.collect_stops()
        df = wb.stops
    else:
        raise ValueError(f"Unsupported type: {args.type}")

    print(f"Collected {len(df)} records")

    filetype = args.output.split(".")[-1]
    if filetype == "csv":
        df.to_csv(args.output, index=False)
    elif filetype == "parquet":
        df.to_parquet(args.output, index=False)
    elif filetype == "gzip":
        df.to_parquet(args.output, index=False, compression="gzip")
    else:
        raise ValueError("Unsupported file type")


if __name__ == "__main__":
    __main__()
