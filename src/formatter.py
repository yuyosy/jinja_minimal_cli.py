
import csv
import json
from abc import ABCMeta, abstractmethod
from io import TextIOWrapper
from pathlib import Path
from typing import IO, Any, Dict, List, Tuple, Union

from ruamel.yaml import YAML


class BaseFormatter(metaclass=ABCMeta):

    @property
    @abstractmethod
    def extensions(self) -> Tuple[str, ...]:
        pass

    @abstractmethod
    def load(self, fp: IO) -> Any:
        pass

    @abstractmethod
    def dump(self, data: Any, fp: IO) -> Any:
        pass


class CsvFormatter(BaseFormatter):
    @property
    def extensions(self) -> Tuple[str, ...]:
        return ('.csv',)

    def load(self, fp: IO, *, delimiter: str = ',') -> Any:
        reader = csv.DictReader(fp, delimiter=delimiter)
        return reader

    def dump(self, rows: Any, fp: IO, *,
             sort_keys: bool = False, listup: bool = False,
             delimiter: str = ',', lineterminator: str = '\n', quoting: Any = csv.QUOTE_ALL, extrasaction: str = 'ignore') -> Any:
        if not rows:
            return
        if hasattr(rows, 'keys') or hasattr(rows, 'join'):
            rows = [rows]

        itr = iter(rows)
        scanned = [next(itr)]
        fields = list(scanned[0].keys())
        seen = set(fields)

        if listup:
            for row in itr:
                for k in row.keys():
                    if k not in seen:
                        seen.add(k)
                        fields.append(k)
                scanned.append(row)
        if sort_keys:
            fields = sorted(fields)
        fields = list(fields)
        writer = csv.DictWriter(fp, fields, delimiter=delimiter, lineterminator=lineterminator, quoting=quoting, extrasaction=extrasaction)
        writer.writeheader()
        writer.writerows(scanned)
        writer.writerows(itr)


class JsonFomatter(BaseFormatter):
    @property
    def extensions(self) -> Tuple[str, ...]:
        return ('.json', '.js')

    def load(self, fp: IO) -> Any:
        return json.load(fp)

    def dump(self, data: Any, fp: IO, *, ensure_ascii: bool = False, sort_keys: bool = False, indent: int = 2, default: Any = str) -> Any:
        return json.dump(data, fp, ensure_ascii=ensure_ascii, indent=indent, default=default, sort_keys=sort_keys,)


class YamlFomatter(BaseFormatter):
    def __init__(self) -> None:
        self.yaml = YAML(typ='safe')
        super().__init__()

    @property
    def extensions(self) -> Tuple[str, ...]:
        return ('.yaml', '.yml')

    def load(self, fp: IO) -> Any:
        return self.yaml.load(fp)

    def dump(self, data: Any, fp: IO, *, flow_style: bool = False) -> Any:
        self.yaml.default_flow_style = flow_style
        return self.yaml.dump(data, fp)


class RawTextFomatter(BaseFormatter):
    @property
    def extensions(self) -> Tuple[str, ...]:
        return ('.txt',)

    def load(self, fp: IO) -> Any:
        return fp.read()

    def dump(self, data: Any, fp: IO) -> Any:
        return fp.write(data)


class Dispatcher():
    def __init__(self) -> None:
        self._formatters: Dict[str, BaseFormatter] = {
            'yaml': YamlFomatter(),
            'json': JsonFomatter(),
            'csv': CsvFormatter(),
            'raw': RawTextFomatter()
        }
        self.formatter_map: Dict[str, str] = {}
        self.extensions: List[str] = []
        for key, fmtr in self._formatters.items():
            for ext in fmtr.extensions:
                self.extensions.append(ext)
                self.formatter_map[ext] = key

    @property
    def extensions_list(self) -> List[str]:
        return self.extensions

    def has_extension(self, ext: str) -> bool:
        return ext in self.extensions

    def get_format_type(self, ext: str) -> Union[str, None]:
        return self.formatter_map.get(ext, None)

    def get_formatter(self, name: str) -> BaseFormatter:
        return self._formatters[name]

    def get_formatter_from_exts(self, ext: str) -> BaseFormatter:
        name = self.formatter_map.get(ext, 'raw')
        return self.get_formatter(name)

    def loadfile(self, fp: Union[IO, Path, str], *, format: Union[str, None] = None, encoding: str = 'utf-8') -> Any:
        if format is None:
            if isinstance(fp, str):
                format = self.get_format_type(self._suffix(fp)) or 'raw'
            elif isinstance(fp, TextIOWrapper):
                format = self.get_format_type(self._suffix(fp.name)) or 'raw'
            elif isinstance(fp, Path):
                format = self.get_format_type(fp.suffix) or 'raw'
            else:
                format = 'raw'

        formatter = self.get_formatter(format)
        if isinstance(fp, str):
            with open(fp, mode='r', encoding=encoding) as f:
                fp = f
        elif isinstance(fp, Path):
            with fp.open('r', encoding=encoding) as f:
                fp = f
        return formatter.load(fp)

    def _suffix(self, path: str) -> str:
        i = path.rfind('.')
        if 0 < i < len(path) - 1:
            return path[i:]
        else:
            return ''
