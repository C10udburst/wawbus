from .main import WawBus


def __main__():
    import argparse

    parser = argparse.ArgumentParser(description="Collect bus positions from api.um.warszawa.pl")
    parser.add_argument("--apikey", help="api.um.warszawa.pl API key")
    parser.add_argument("--count", help="number of collections", type=int, default=25)
    parser.add_argument("--retry", help="number of retries", type=int, default=3)
    parser.add_argument("--sleep", help="sleep between collections", type=int, default=10)
    parser.add_argument("--output", help="output file")

    args = parser.parse_args()

    if not args.apikey:
        raise ValueError("API key is required.")
    if not args.output:
        raise ValueError("Output file is required.")
    wb = WawBus(apikey=args.apikey, retry_count=args.retry)

    df = wb.collect_positions(args.count, args.sleep)
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
