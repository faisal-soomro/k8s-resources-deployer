import yaml

def parse_string(yaml_string, logger):
    try:
        yamlbody = yaml.safe_load(yaml_string)
        return yamlbody
    except yaml.parser.ParserError as error:
        logger.error(error)
        return(-1)
    except yaml.scanner.ScannerError as error:
        logger.error(error)
        return(-1)
    except:
        return(-1)
