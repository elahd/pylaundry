"""pylaundry constants."""

from enum import IntEnum

#
# Requests
#

API_ENDPOINT_URL = "https://mapp.mylaundrylink.com/AppRequestHandler.aspx"
AUTH_TOKEN_KEY = "CP_AUTH_TOKEN"  # nosec
RESULT_CODE_KEY = "ResultCode"
RESULT_TEXT_KEY = "ResultText"
REFRESH_REQUEST_PREHASH_SUFFIX = (  # Appended to user ID, then MD5 hashed. Used in body data refresh requests.
    "b1c/B?D(G+1bPeSh"
)
EMPTY_AUTH_TOKEN = "00000000-0000-0000-0000-000000000000"  # nosec
APPKEY = "$#!@ES(*#D3$!318z"


class ServerResponseCodes(IntEnum):
    """Enum of known server response codes."""

    INPUT_MALFORMED = -1
    PARENT_OBJ_ERROR = 0
    SUCCESS = 1
    INVALID_CREDENTIALS = 105
    INVALID_REQUEST = 122


#
# Encryption
#

AES_IV = bytearray(
    [83, 71, 26, 58, 54, 35, 22, 11, 83, 71, 26, 58, 54, 35, 22, 11]
)  # Used an initialization vector for all AES operations. As hex: ['53', '47', '1A', '3A', '36', '23', '16', '0B', '53', '47', '1A', '3A', '36', '23', '16', '0B']
AES_SUFFIX_PREAUTH = (  # Appended to random request UUID before further processing into AES key. Used for authentication requests only.
    "R&%76mhK"
)

LOG_LEVEL_TRACE = 5
