"""Constants used in Erlang code generation."""

__author__ = "Bartosz Walkowicz"
__copyright__ = "Copyright (C) 2024 ACK CYFRONET AGH"
__license__ = "This software is released under the MIT license cited in LICENSE.txt"

import os
from typing import Dict, Final

# Directory paths
ERROR_DEFINITIONS_ROOT_DIR: Final[str] = "definitions"
TEMPLATES_DIR: Final[str] = os.path.join(os.path.dirname(__file__), "templates")

# Output file paths
OUTPUT_DIR: Final[str] = "generated/erlang"
ERRORS_HRL_FILE_PATH: Final[str] = os.path.join(OUTPUT_DIR, "errors.hrl")
ERROR_ATTRS_HRL_FILE_PATH: Final[str] = os.path.join(OUTPUT_DIR, "error_attrs.hrl")
ERRORS_ERL_FILE_PATH: Final[str] = os.path.join(OUTPUT_DIR, "errors.erl")
OD_ERROR_FILE_PATH: Final[str] = os.path.join(OUTPUT_DIR, "od_error.erl")
ERROR_TYPES_DIR: Final[str] = os.path.join(OUTPUT_DIR, "types")

# Formatting
INDENT: Final[str] = 4 * " "
HORIZONTAL_COMMENT_LINE: Final[str] = "%%" + 68 * "-"

# HTTP status code mapping to Erlang macros
HTTP_CODE_TO_MACRO: Final[Dict[int, str]] = {
    400: "?HTTP_400_BAD_REQUEST",
    401: "?HTTP_401_UNAUTHORIZED",
    403: "?HTTP_403_FORBIDDEN",
    404: "?HTTP_404_NOT_FOUND",
    405: "?HTTP_405_METHOD_NOT_ALLOWED",
    409: "?HTTP_409_CONFLICT",
    413: "?HTTP_413_PAYLOAD_TOO_LARGE",
    415: "?HTTP_415_UNSUPPORTED_MEDIA_TYPE",
    416: "?HTTP_416_RANGE_NOT_SATISFIABLE",
    426: "?HTTP_426_UPGRADE_REQUIRED",
    429: "?HTTP_429_TOO_MANY_REQUESTS",
    500: "?HTTP_500_INTERNAL_SERVER_ERROR",
    501: "?HTTP_501_NOT_IMPLEMENTED",
    503: "?HTTP_503_SERVICE_UNAVAILABLE",
}

# All valid POSIX errno values that can be used in error definitions
VALID_ERRNO = {
    "E2BIG",
    "EACCES",
    "EADDRINUSE",
    "EADDRNOTAVAIL",
    "EAFNOSUPPORT",
    "EAGAIN",
    "EALREADY",
    "EBADF",
    "EBADMSG",
    "EBUSY",
    "ECANCELED",
    "ECHILD",
    "ECONNABORTED",
    "ECONNREFUSED",
    "ECONNRESET",
    "EDEADLK",
    "EDESTADDRREQ",
    "EDOM",
    "EEXIST",
    "EFAULT",
    "EFBIG",
    "EHOSTUNREACH",
    "EIDRM",
    "EILSEQ",
    "EINPROGRESS",
    "EINTR",
    "EINVAL",
    "EIO",
    "EISCONN",
    "EISDIR",
    "EKEYEXPIRED",
    "ELOOP",
    "EMFILE",
    "EMLINK",
    "EMSGSIZE",
    "ENAMETOOLONG",
    "ENETDOWN",
    "ENETRESET",
    "ENETUNREACH",
    "ENFILE",
    "ENOBUFS",
    "ENODATA",
    "ENODEV",
    "ENOENT",
    "ENOEXEC",
    "ENOLCK",
    "ENOLINK",
    "ENOMEM",
    "ENOMSG",
    "ENOPROTOOPT",
    "ENOSPC",
    "ENOSR",
    "ENOSTR",
    "ENOSYS",
    "ENOTCONN",
    "ENOTDIR",
    "ENOTEMPTY",
    "ENOTRECOVERABLE",
    "ENOTSOCK",
    "ENOTSUP",
    "ENOTTY",
    "ENXIO",
    "EOPNOTSUPP",
    "EOVERFLOW",
    "EOWNERDEAD",
    "EPERM",
    "EPIPE",
    "EPROTO",
    "EPROTONOSUPPORT",
    "EPROTOTYPE",
    "ERANGE",
    "EROFS",
    "ESPIPE",
    "ESRCH",
    "ETIME",
    "ETIMEDOUT",
    "ETXTBSY",
    "EWOULDBLOCK",
    "EXDEV",
}
