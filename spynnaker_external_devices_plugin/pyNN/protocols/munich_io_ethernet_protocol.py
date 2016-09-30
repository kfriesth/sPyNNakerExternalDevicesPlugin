ENABLE_RETINA = "E+"
DISABLE_RETINA = "E-"
ENABLE_RETINA_SD_CARD_RECORDING = "!ER+"
DISABLE_RETINA_SD_CARD_RECORDING = "!ER-"
EVENT_DATA_FORMAT_PREFIX = "!Ex"



class MunichIoEthernetProtocol(object):

    def __init__(self, connection):
        self._connection = connection


    def enable_retina(self):
        self._connection.send()

