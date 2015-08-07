def parse_config_file(fp):
    file_data = fp.read().split('\n')
    required_credentials = ["STORAGE_URL",
                            "DEADLINE",
                            "OS_AUTH_URL",
                            "OS_USERNAME",
                            "OS_PASSWORD",
                            "OS_TENANT_NAME",
                            "OS_REGION_NAME"]

    usr_credentials = dict()

    try: 
        for line in file_data:
            line = line.split("=")
            if line[0] not in required_credentials:
                raise Exception("Malformed config file: %s is not a variable" %line[0] )
            else:
                required_credentials.remove(line[0])
                usr_credentials[line[0]] = line[1]

        if len(required_credentials) > 0:
            raise Exception("Credentials missing from config file: ", required_credentials)
    except Exception as e:
        print e.args
    except IndexError:
        print "Malformed config file: Each credential must be in the form VARIABLE=VALUE"
    
    else:
        return usr_credentials