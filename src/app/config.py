import json
config_file = open("/data/options.json", "r")
config = json.load(config_file)
config_file.close()
