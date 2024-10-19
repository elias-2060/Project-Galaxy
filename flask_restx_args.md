### `RequestParser.add_argument()       (Argument)`
- `name`: Either a name or a list of option strings, e.g. foo or -f, --foo.
- `default`: The value produced if the argument is absent from the request.
- `dest`: The name of the attribute to be added to the object returned by :meth:`~reqparse.RequestParser.parse_args()`.
- `bool required`: Whether or not the argument may be omitted (optionals only).
- `string action`: The basic type of action to be taken when this argument is encountered in the request.
                   Valid options are "store" and "append".
- `bool ignore`: Whether to ignore cases where the argument fails type conversion
- `type`: The type to which the request argument should be converted.
          If a type raises an exception, the message in the error will be returned in the response.
          Defaults to  :class:`str`.
- `location`: The attributes of the :class:`flask.Request` object to source the arguments from (ex: headers, args, etc.), can be an iterator.
              The last item listed takes precedence in the result set.
- `choices`: A container of the allowable values for the argument.
- `help`: A brief description of the argument, returned in the response when the argument is invalid.
          May optionally contain an "{error_msg}" interpolation token, which will be replaced with the text of the error raised by the type converter.
- `bool case_sensitive`: Whether argument values in the request are case sensitive or not (this will convert all values to lowercase)
- `bool store_missing`: Whether the arguments default value should be stored if the argument is missing from the request.
- `bool trim`: If enabled, trims whitespace around the argument.
- `bool nullable`: If enabled, allows null value in argument.


### `fields.Raw`
- `default`: The default value for the field, if no value is specified.
- `attribute`: If the public facing value differs from the internal value, use this to retrieve a different attribute from the response than the publicly named value.
- `str title`: The field title (for documentation purpose)
- `str description`: The field description (for documentation purpose)
- `bool required`: Is the field required ?
- `bool readonly`: Is the field read only ? (for documentation purpose)
- `example`: An optional data example (for documentation purpose)
- `callable mask`: An optional mask function to be applied to output
