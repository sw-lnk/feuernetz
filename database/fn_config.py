from configparser import ConfigParser

CONFIG_FILE_NAME = "config.ini"

config_object = ConfigParser()
config_object.read(CONFIG_FILE_NAME)
