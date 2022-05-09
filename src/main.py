from argparse import ArgumentParser

from resource_path import resource_path


def add_parser() -> ArgumentParser:
    parser = ArgumentParser()

    parser.add_argument(
        "-d", "--data", action="append", help="data", default=[]
    )

    return parser


if __name__ == '__main__':
    parser = add_parser()
    args = parser.parse_args()

    print(args.data)
