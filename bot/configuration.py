from collections import namedtuple


token = "place_your_token"
yolo_model = "place_your_model"

Config = namedtuple("BotConfiguration", ["token", "model"])

config = Config(token, yolo_model)
