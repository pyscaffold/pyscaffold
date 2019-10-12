"""Configuration file updater.

A configuration file consists of sections, lead by a "[section]" header,
and followed by "name: value" entries, with continuations and such in
the style of RFC 822.

The basic idea of ConfigUpdater is that a configuration file consists of
three kinds of building blocks: sections, comments and spaces for separation.
A section itself consists of three kinds of blocks: options, comments and
spaces. This gives us the corresponding data structures to describe a
configuration file.

A general block object contains the lines which were parsed and make up
the block. If a block object was not changed then during writing the same
lines that were parsed will be used to express the block. In case a block,
e.g. an option, was changed, it is marked as `updated` and its values will
be transformed into a corresponding string during an update of a
configuration file.


.. note::

   ConfigUpdater was created by starting from Python's ConfigParser source
   code and changing it according to my needs. Thus this source code
   is subject to the PSF License in a way but I am not a lawyer.
"""

import io
import os
import re
import sys
from abc import ABC
from collections import OrderedDict as _default_dict
from collections.abc import MutableMapping
from configparser import (ConfigParser, DuplicateOptionError,
                          DuplicateSectionError, Error,
                          MissingSectionHeaderError, NoOptionError,
                          NoSectionError, ParsingError)

__all__ = ["NoSectionError", "DuplicateOptionError", "DuplicateSectionError",
           "NoOptionError", "NoConfigFileReadError", "ParsingError",
           "MissingSectionHeaderError", "ConfigUpdater"]


class NoConfigFileReadError(Error):
    """Raised when no configuration file was read but update requested."""
    def __init__(self):
        super().__init__(
            "No configuration file was yet read! Use .read(...) first.")


# Used in parser getters to indicate the default behaviour when a specific
# option is not found it to raise an exception. Created to enable 'None' as
# a valid fallback value.
_UNSET = object()


class Container(ABC):
    """Abstract Mixin Class
    """
    def __init__(self, **kwargs):
        self._structure = list()
        super().__init__(**kwargs)

    @property
    def structure(self):
        return self._structure

    @property
    def last_item(self):
        if self._structure:
            return self._structure[-1]
        else:
            return None


class Block(ABC):
    """Abstract Block type holding lines

    Block objects hold original lines from the configuration file and hold
    a reference to a container wherein the object resides.
    """
    def __init__(self, container=None, **kwargs):
        self._container = container
        self.lines = []
        self._updated = False
        super().__init__(**kwargs)

    def __str__(self):
        return ''.join(self.lines)

    def __len__(self):
        return len(self.lines)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.lines == other.lines
        else:
            return False

    def add_line(self, line):
        """Add a line to the current block

        Args:
            line (str): one line to add
        """
        self.lines.append(line)
        return self

    @property
    def container(self):
        return self._container

    @property
    def add_before(self):
        """Returns a builder inserting a new block before the current block"""
        idx = self._container.structure.index(self)
        return BlockBuilder(self._container, idx)

    @property
    def add_after(self):
        """Returns a builder inserting a new block after the current block"""
        idx = self._container.structure.index(self)
        return BlockBuilder(self._container, idx+1)


class BlockBuilder(object):
    """Builder that injects blocks at a given index position."""
    def __init__(self, container, idx):
        self._container = container
        self._idx = idx

    def comment(self, text, comment_prefix='#'):
        """Creates a comment block

        Args:
            text (str): content of comment without #
            comment_prefix (str): character indicating start of comment

        Returns:
            self for chaining
        """
        comment = Comment(self._container)
        if not text.startswith(comment_prefix):
            text = "{} {}".format(comment_prefix, text)
        if not text.endswith('\n'):
            text = "{}{}".format(text, '\n')
        comment.add_line(text)
        self._container.structure.insert(self._idx, comment)
        self._idx += 1
        return self

    def section(self, section):
        """Creates a section block

        Args:
            section (str or :class:`Section`): name of section or object

        Returns:
            self for chaining
        """
        if not isinstance(self._container, ConfigUpdater):
            raise ValueError("Sections can only be added at section level!")
        if isinstance(section, str):
            # create a new section
            section = Section(section, container=self._container)
        elif not isinstance(section, Section):
            raise ValueError("Parameter must be a string or Section type!")
        if section.name in [block.name for block in self._container
                            if isinstance(block, Section)]:
            raise DuplicateSectionError(section.name)
        self._container.structure.insert(self._idx, section)
        self._idx += 1
        return self

    def space(self, newlines=1):
        """Creates a vertical space of newlines

        Args:
            newlines (int): number of empty lines

        Returns:
            self for chaining
        """
        space = Space()
        for line in range(newlines):
            space.add_line('\n')
        self._container.structure.insert(self._idx, space)
        self._idx += 1
        return self

    def option(self, key, value=None, **kwargs):
        """Creates a new option inside a section

        Args:
            key (str): key of the option
            value (str or None): value of the option
            **kwargs: are passed to the constructor of :class:`Option`

        Returns:
            self for chaining
        """
        if not isinstance(self._container, Section):
            raise ValueError("Options can only be added inside a section!")
        option = Option(key, value, container=self._container, **kwargs)
        option.value = value
        self._container.structure.insert(self._idx, option)
        self._idx += 1
        return self


class Comment(Block):
    """Comment block"""
    def __init__(self, container=None):
        super().__init__(container=container)

    def __repr__(self):
        return '<Comment>'


class Space(Block):
    """Vertical space block of new lines"""
    def __init__(self, container=None):
        super().__init__(container=container)

    def __repr__(self):
        return '<Space>'


class Section(Block, Container, MutableMapping):
    """Section block holding options

    Attributes:
        name (str): name of the section
        updated (bool): indicates name change or a new section
    """
    def __init__(self, name, container, **kwargs):
        self._name = name
        self._structure = list()
        self._updated = False
        super().__init__(container=container, **kwargs)

    def add_option(self, entry):
        """Add an Option object to the section

        Used during initial parsing mainly

        Args:
            entry (Option): key value pair as Option object
        """
        self._structure.append(entry)
        return self

    def add_comment(self, line):
        """Add a Comment object to the section

        Used during initial parsing mainly

        Args:
            line (str): one line in the comment
        """
        if not isinstance(self.last_item, Comment):
            comment = Comment(self._structure)
            self._structure.append(comment)
        self.last_item.add_line(line)
        return self

    def add_space(self, line):
        """Add a Space object to the section

        Used during initial parsing mainly

        Args:
            line (str): one line that defines the space, maybe whitespaces
        """
        if not isinstance(self.last_item, Space):
            space = Space(self._structure)
            self._structure.append(space)
        self.last_item.add_line(line)
        return self

    def _get_option_idx(self, key):
        idx = [i for i, entry in enumerate(self._structure)
               if isinstance(entry, Option) and entry.key == key]
        if idx:
            return idx[0]
        else:
            raise ValueError

    def __str__(self):
        if not self.updated:
            s = super().__str__()
        else:
            s = "[{}]\n".format(self._name)
        for entry in self._structure:
            s += str(entry)
        return s

    def __repr__(self):
        return '<Section: {}>'.format(self.name)

    def __getitem__(self, key):
        if key not in self.options():
            raise KeyError(key)
        return self._structure[self._get_option_idx(key=key)]

    def __setitem__(self, key, value):
        if key in self:
            option = self.__getitem__(key)
            option.value = value
        else:
            option = Option(key, value, container=self)
            option.value = value
            self._structure.append(option)

    def __delitem__(self, key):
        if key not in self.options():
            raise KeyError(key)
        idx = self._get_option_idx(key=key)
        del self._structure[idx]

    def __contains__(self, key):
        return key in self.options()

    def __len__(self):
        return len(self._structure)

    def __iter__(self):
        """Return all entries, not just options"""
        return self._structure.__iter__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.name == other.name and
                    self._structure == other._structure)
        else:
            return False

    def option_blocks(self):
        """Returns option blocks

        Returns:
            list: list of :class:`Option` blocks
        """
        return [entry for entry in self._structure
                if isinstance(entry, Option)]

    def options(self):
        """Returns option names

        Returns:
            list: list of option names as strings
        """
        return [option.key for option in self.option_blocks()]

    def to_dict(self):
        """Transform to dictionary

        Returns:
            dict: dictionary with same content
        """
        return {key: self.__getitem__(key).value for key in self.options()}

    @property
    def updated(self):
        """Returns if the option was changed/updated"""
        # if no lines were added, treat it as updated since we added it
        return self._updated or not self.lines

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)
        self._updated = True

    def set(self, option, value=None):
        """Set an option for chaining.

        Args:
            option (str): option name
            value (str): value, default None
        """
        option = self._container.optionxform(option)
        if option in self.options():
            self.__getitem__(option).value = value
        else:
            self.__setitem__(option, value)
        return self

    def insert_at(self, idx):
        """Returns a builder inserting a new block at the given index

        Args:
            idx (int): index where to insert
        """
        return BlockBuilder(self, idx)


class Option(Block):
    """Option block holding a key/value pair.

    Attributes:
        key (str): name of the key
        value (str): stored value
        updated (bool): indicates name change or a new section
    """
    def __init__(self, key, value, container, delimiter='=',
                 space_around_delimiters=True, line=None):
        super().__init__(container=container)
        self._key = key
        self._values = [value]
        self._value_is_none = value is None
        self._delimiter = delimiter
        self._value = None  # will be filled after join_multiline_value
        self._updated = False
        self._multiline_value_joined = False
        self._space_around_delimiters = space_around_delimiters
        if line:
            self.lines.append(line)

    def add_line(self, line):
        super().add_line(line)
        self._values.append(line.strip())

    def _join_multiline_value(self):
        if not self._multiline_value_joined and not self._value_is_none:
            # do what `_join_multiline_value` in ConfigParser would do
            self._value = '\n'.join(self._values).rstrip()
            self._multiline_value_joined = True

    def __str__(self):
        if not self.updated:
            return super().__str__()
        if self._value is None:
            return "{}{}".format(self._key, '\n')
        if self._space_around_delimiters:
            # no space is needed if we use multi-line arguments
            suffix = '' if str(self._value).startswith('\n') else ' '
            delim = " {}{}".format(self._delimiter, suffix)
        else:
            delim = self._delimiter
        return "{}{}{}{}".format(self._key, delim, self._value, '\n')

    def __repr__(self):
        return '<Option: {} = {}>'.format(self.key, self.value)

    @property
    def updated(self):
        """Returns if the option was changed/updated"""
        # if no lines were added, treat it as updated since we added it
        return self._updated or not self.lines

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._join_multiline_value()
        self._key = value
        self._updated = True

    @property
    def value(self):
        self._join_multiline_value()
        return self._value

    @value.setter
    def value(self, value):
        self._updated = True
        self._multiline_value_joined = True
        self._value = value
        self._values = [value]

    def set_values(self, values, separator='\n', indent=4*' '):
        """Sets the value to a given list of options, e.g. multi-line values

        Args:
            values (list): list of values
            separator (str): separator for values, default: line separator
            indent (str): indentation depth in case of line separator
        """
        self._updated = True
        self._multiline_value_joined = True
        self._values = values
        if separator == '\n':
            values.insert(0, '')
            separator = separator + indent
        self._value = separator.join(values)


class ConfigUpdater(Container, MutableMapping):
    """Parser for updating configuration files.

    ConfigUpdater follows the API of ConfigParser with some differences:
      * inline comments are treated as part of a key's value,
      * only a single config file can be updated at a time,
      * empty lines in values are not valid,
      * the original case of sections and keys are kept,
      * control over the position of a new section/key.

    Following features are **deliberately not** implemented:

      * interpolation of values,
      * propagation of parameters from the default section,
      * conversions of values,
      * passing key/value-pairs with ``default`` argument,
      * non-strict mode allowing duplicate sections and keys.
    """
    # Regular expressions for parsing section headers and options
    _SECT_TMPL = r"""
        \[                                 # [
        (?P<header>[^]]+)                  # very permissive!
        \]                                 # ]
        """
    _OPT_TMPL = r"""
        (?P<option>.*?)                    # very permissive!
        \s*(?P<vi>{delim})\s*              # any number of space/tab,
                                           # followed by any of the
                                           # allowed delimiters,
                                           # followed by any space/tab
        (?P<value>.*)$                     # everything up to eol
        """
    _OPT_NV_TMPL = r"""
        (?P<option>.*?)                    # very permissive!
        \s*(?:                             # any number of space/tab,
        (?P<vi>{delim})\s*                 # optionally followed by
                                           # any of the allowed
                                           # delimiters, followed by any
                                           # space/tab
        (?P<value>.*))?$                   # everything up to eol
        """
    # Compiled regular expression for matching sections
    SECTCRE = re.compile(_SECT_TMPL, re.VERBOSE)
    # Compiled regular expression for matching options with typical separators
    OPTCRE = re.compile(_OPT_TMPL.format(delim="=|:"), re.VERBOSE)
    # Compiled regular expression for matching options with optional values
    # delimited using typical separators
    OPTCRE_NV = re.compile(_OPT_NV_TMPL.format(delim="=|:"), re.VERBOSE)
    # Compiled regular expression for matching leading whitespace in a line
    NONSPACECRE = re.compile(r"\S")

    def __init__(self, allow_no_value=False, *, delimiters=('=', ':'),
                 comment_prefixes=('#', ';'), inline_comment_prefixes=None,
                 strict=True, space_around_delimiters=True):
        """Constructor of ConfigUpdater

        Args:
            allow_no_value (bool): allow keys without a value, default False
            delimiters (tuple): delimiters for key/value pairs, default =, :
            comment_prefixes (tuple): prefix of comments, default # and ;
            inline_comment_prefixes (tuple): prefix of inline comment,
                default None
            strict (bool): each section must be unique as well as every key
                within a section, default True
            space_around_delimiters (bool): add a space before and after the
                delimiter, default True
        """
        self._filename = None
        self._space_around_delimiters = space_around_delimiters

        self._dict = _default_dict  # no reason to let the user change this
        # keeping _sections to keep code aligned with ConfigParser but
        # _structure takes the actual role instead. Only use self._structure!
        self._sections = self._dict()
        self._structure = []
        self._delimiters = tuple(delimiters)
        if delimiters == ('=', ':'):
            self._optcre = self.OPTCRE_NV if allow_no_value else self.OPTCRE
        else:
            d = "|".join(re.escape(d) for d in delimiters)
            if allow_no_value:
                self._optcre = re.compile(self._OPT_NV_TMPL.format(delim=d),
                                          re.VERBOSE)
            else:
                self._optcre = re.compile(self._OPT_TMPL.format(delim=d),
                                          re.VERBOSE)
        self._comment_prefixes = tuple(comment_prefixes or ())
        self._inline_comment_prefixes = tuple(inline_comment_prefixes or ())
        self._strict = strict
        self._allow_no_value = allow_no_value
        # Options from ConfigParser that we need to set constantly
        self._empty_lines_in_values = False
        super().__init__()

    def _get_section_idx(self, name):
        idx = [i for i, entry in enumerate(self._structure)
               if isinstance(entry, Section) and entry.name == name]
        if idx:
            return idx[0]
        else:
            raise ValueError

    def read(self, filename, encoding=None):
        """Read and parse a filename.

        Args:
            filename (str): path to file
            encoding (str): encoding of file, default None
        """
        with open(filename, encoding=encoding) as fp:
            self._read(fp, filename)
        self._filename = os.path.abspath(filename)

    def read_file(self, f, source=None):
        """Like read() but the argument must be a file-like object.

        The ``f`` argument must be iterable, returning one line at a time.
        Optional second argument is the ``source`` specifying the name of the
        file being read. If not given, it is taken from f.name. If ``f`` has no
        ``name`` attribute, ``<???>`` is used.

        Args:
            f: file like object
            source (str): reference name for file object, default None
        """
        if isinstance(f, str):
            raise RuntimeError("f must be a file-like object, not string!")
        if source is None:
            try:
                source = f.name
            except AttributeError:
                source = '<???>'
        self._read(f, source)

    def read_string(self, string, source='<string>'):
        """Read configuration from a given string.

        Args:
            string (str): string containing a configuration
            source (str): reference name for file object, default '<string>'
        """
        sfile = io.StringIO(string)
        self.read_file(sfile, source)

    def optionxform(self, optionstr):
        """Converts an option key to lower case for unification

        Args:
             optionstr (str): key name

        Returns:
            str: unified option name
        """
        return optionstr.lower()

    def _update_curr_block(self, block_type):
        if not isinstance(self.last_item, block_type):
            new_block = block_type(container=self)
            self._structure.append(new_block)

    def _add_comment(self, line):
        if isinstance(self.last_item, Section):
            self.last_item.add_comment(line)
        else:
            self._update_curr_block(Comment)
            self.last_item.add_line(line)

    def _add_section(self, sectname, line):
        new_section = Section(sectname, container=self)
        new_section.add_line(line)
        self._structure.append(new_section)

    def _add_option(self, key, vi, value, line):
        entry = Option(
            key, value,
            delimiter=vi,
            container=self.last_item,
            space_around_delimiters=self._space_around_delimiters,
            line=line)
        self.last_item.add_option(entry)

    def _add_space(self, line):
        if isinstance(self.last_item, Section):
            self.last_item.add_space(line)
        else:
            self._update_curr_block(Space)
            self.last_item.add_line(line)

    def _read(self, fp, fpname):
        """Parse a sectioned configuration file.

        Each section in a configuration file contains a header, indicated by
        a name in square brackets (`[]`), plus key/value options, indicated by
        `name` and `value` delimited with a specific substring (`=` or `:` by
        default).

        Values can span multiple lines, as long as they are indented deeper
        than the first line of the value. Depending on the parser's mode, blank
        lines may be treated as parts of multiline values or ignored.

        Configuration files may include comments, prefixed by specific
        characters (`#` and `;` by default). Comments may appear on their own
        in an otherwise empty line or may be entered in lines holding values or
        section names.

        Note: This method was borrowed from ConfigParser and we keep this
        mess here as close as possible to the original messod (pardon
        this german pun) for consistency reasons and later upgrades.
        """
        self._structure = []
        elements_added = set()
        cursect = None                        # None, or a dictionary
        sectname = None
        optname = None
        lineno = 0
        indent_level = 0
        e = None                              # None, or an exception
        for lineno, line in enumerate(fp, start=1):
            comment_start = sys.maxsize
            # strip inline comments
            inline_prefixes = {p: -1 for p in self._inline_comment_prefixes}
            while comment_start == sys.maxsize and inline_prefixes:
                next_prefixes = {}
                for prefix, index in inline_prefixes.items():
                    index = line.find(prefix, index+1)
                    if index == -1:
                        continue
                    next_prefixes[prefix] = index
                    if index == 0 or (index > 0 and line[index-1].isspace()):
                        comment_start = min(comment_start, index)
                inline_prefixes = next_prefixes
            # strip full line comments
            for prefix in self._comment_prefixes:
                if line.strip().startswith(prefix):
                    comment_start = 0
                    self._add_comment(line)  # HOOK
                    break
            if comment_start == sys.maxsize:
                comment_start = None
            value = line[:comment_start].strip()
            if not value:
                if self._empty_lines_in_values:
                    # add empty line to the value, but only if there was no
                    # comment on the line
                    if (comment_start is None and
                            cursect is not None and
                            optname and
                            cursect[optname] is not None):
                        cursect[optname].append('')  # newlines added at join
                        self.last_item.last_item.add_line(line)  # HOOK
                else:
                    # empty line marks end of value
                    indent_level = sys.maxsize
                if comment_start is None:
                    self._add_space(line)
                continue
            # continuation line?
            first_nonspace = self.NONSPACECRE.search(line)
            cur_indent_level = first_nonspace.start() if first_nonspace else 0
            if (cursect is not None and optname and
                    cur_indent_level > indent_level):
                cursect[optname].append(value)
                self.last_item.last_item.add_line(line)  # HOOK
            # a section header or option header?
            else:
                indent_level = cur_indent_level
                # is it a section header?
                mo = self.SECTCRE.match(value)
                if mo:
                    sectname = mo.group('header')
                    if sectname in self._sections:
                        if self._strict and sectname in elements_added:
                            raise DuplicateSectionError(sectname, fpname,
                                                        lineno)
                        cursect = self._sections[sectname]
                        elements_added.add(sectname)
                    else:
                        cursect = self._dict()
                        self._sections[sectname] = cursect
                        elements_added.add(sectname)
                    # So sections can't start with a continuation line
                    optname = None
                    self._add_section(sectname, line)  # HOOK
                # no section header in the file?
                elif cursect is None:
                    raise MissingSectionHeaderError(fpname, lineno, line)
                # an option line?
                else:
                    mo = self._optcre.match(value)
                    if mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        if not optname:
                            e = self._handle_error(e, fpname, lineno, line)
                        optname = self.optionxform(optname.rstrip())
                        if (self._strict and
                                (sectname, optname) in elements_added):
                            raise DuplicateOptionError(sectname, optname,
                                                       fpname, lineno)
                        elements_added.add((sectname, optname))
                        # This check is fine because the OPTCRE cannot
                        # match if it would set optval to None
                        if optval is not None:
                            optval = optval.strip()
                            cursect[optname] = [optval]
                        else:
                            # valueless option handling
                            cursect[optname] = None
                        self._add_option(optname, vi, optval, line)  # HOOK
                    else:
                        # a non-fatal parsing error occurred. set up the
                        # exception but keep going. the exception will be
                        # raised at the end of the file and will contain a
                        # list of all bogus lines
                        e = self._handle_error(e, fpname, lineno, line)
        # if any parsing errors occurred, raise an exception
        if e:
            raise e

    def _handle_error(self, exc, fpname, lineno, line):
        if not exc:
            exc = ParsingError(fpname)
        exc.append(lineno, repr(line))
        return exc

    def write(self, fp):
        """Write an .ini-format representation of the configuration state.

        Args:
            fp (file-like object): open file handle
        """
        fp.write(str(self))

    def update_file(self):
        """Update the read-in configuration file.
        """
        if self._filename is None:
            raise NoConfigFileReadError()
        with open(self._filename, 'w') as fb:
            self.write(fb)

    def validate_format(self, **kwargs):
        """Call ConfigParser to validate config

        Args:
            kwargs: are passed to :class:`configparser.ConfigParser`
        """
        args = dict(
            dict_type=self._dict,
            allow_no_value=self._allow_no_value,
            inline_comment_prefixes=self._inline_comment_prefixes,
            strict=self._strict,
            empty_lines_in_values=self._empty_lines_in_values
        )
        args.update(kwargs)
        parser = ConfigParser(**args)
        updated_cfg = str(self)
        parser.read_string(updated_cfg)

    def sections_blocks(self):
        """Returns all section blocks

        Returns:
            list: list of :class:`Section` blocks
        """
        return [block for block in self._structure
                if isinstance(block, Section)]

    def sections(self):
        """Return a list of section names

        Returns:
            list: list of section names
        """
        return [section.name for section in self.sections_blocks()]

    def __str__(self):
        return ''.join(str(block) for block in self._structure)

    def __getitem__(self, key):
        for section in self.sections_blocks():
            if section.name == key:
                return section
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if not isinstance(value, Section):
            raise ValueError("Value must be of type Section!")
        if isinstance(key, str) and key in self:
            idx = self._get_section_idx(key)
            del self._structure[idx]
            self._structure.insert(idx, value)
        else:
            # name the section by the key
            value.name = key
            self.add_section(value)

    def __delitem__(self, section):
        if not self.has_section(section):
            raise KeyError(section)
        self.remove_section(section)

    def __contains__(self, key):
        return self.has_section(key)

    def __len__(self):
        """Number of all blocks, not just sections"""
        return len(self._structure)

    def __iter__(self):
        """Iterate over all blocks, not just sections"""
        return self._structure.__iter__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._structure == other._structure
        else:
            return False

    def add_section(self, section):
        """Create a new section in the configuration.

        Raise DuplicateSectionError if a section by the specified name
        already exists. Raise ValueError if name is DEFAULT.

        Args:
            section (str or :class:`Section`): name or Section type
        """
        if section in self.sections():
            raise DuplicateSectionError(section)
        if isinstance(section, str):
            # create a new section
            section = Section(section, container=self)
        elif not isinstance(section, Section):
            raise ValueError("Parameter must be a string or Section type!")
        self._structure.append(section)

    def has_section(self, section):
        """Returns whether the given section exists.

        Args:
            section (str): name of section

        Returns:
            bool: wether the section exists
        """
        return section in self.sections()

    def options(self, section):
        """Returns list of configuration options for the named section.

        Args:
            section (str): name of section

        Returns:
            list: list of option names
        """
        if not self.has_section(section):
            raise NoSectionError(section) from None
        return self.__getitem__(section).options()

    def get(self, section, option):
        """Gets an option value for a given section.

        Args:
            section (str): section name
            option (str): option name

        Returns:
            :class:`Option`: Option object holding key/value pair
        """
        if not self.has_section(section):
            raise NoSectionError(section) from None

        section = self.__getitem__(section)
        option = self.optionxform(option)
        try:
            value = section[option]
        except KeyError:
            raise NoOptionError(option, section)

        return value

    def items(self, section=_UNSET):
        """Return a list of (name, value) tuples for options or sections.

        If section is given, return a list of tuples with (name, value) for
        each option in the section. Otherwise, return a list of tuples with
        (section_name, section_type) for each section.

        Args:
            section (str): optional section name, default UNSET

        Returns:
            list: list of :class:`Section` or :class:`Option` objects
        """
        if section is _UNSET:
            return [(sect.name, sect) for sect in self.sections_blocks()]

        section = self.__getitem__(section)
        return [(opt.key, opt) for opt in section.option_blocks()]

    def has_option(self, section, option):
        """Checks for the existence of a given option in a given section.

        Args:
            section (str): name of section
            option (str): name of option

        Returns:
            bool: whether the option exists in the given section
        """
        if section not in self.sections():
            return False
        else:
            option = self.optionxform(option)
            return option in self[section]

    def set(self, section, option, value=None):
        """Set an option.

        Args:
            section (str): section name
            option (str): option name
            value (str): value, default None
        """
        try:
            section = self.__getitem__(section)
        except KeyError:
            raise NoSectionError(section) from None
        option = self.optionxform(option)
        if option in section:
            section[option].value = value
        else:
            section[option] = value
        return self

    def remove_option(self, section, option):
        """Remove an option.

        Args:
            section (str): section name
            option (str): option name

        Returns:
            bool: whether the option was actually removed
        """
        try:
            section = self.__getitem__(section)
        except KeyError:
            raise NoSectionError(section) from None
        option = self.optionxform(option)
        existed = option in section.options()
        if existed:
            del section[option]
        return existed

    def remove_section(self, name):
        """Remove a file section.

        Args:
            name: name of the section

        Returns:
            bool: whether the section was actually removed
        """
        existed = self.has_section(name)
        if existed:
            idx = self._get_section_idx(name)
            del self._structure[idx]
        return existed

    def to_dict(self):
        """Transform to dictionary

        Returns:
            dict: dictionary with same content
        """
        return {sect: self.__getitem__(sect).to_dict()
                for sect in self.sections()}
