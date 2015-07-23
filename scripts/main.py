# main.py

import client_create
import upload_image
import worker_node_init

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


if __name__ == "__main__":
	file_pointer = open("transburst.conf", 'r')
	credentials = parse_config_file(file_pointer)
	print credentials


	ksclient = client_create.create_keystone_client(credentials)
	glclient = client_create.create_glance_client(ksclient)
	swclient = client_create.create_swift_client(credentials)
	nvclient = client_create.create_nova_client(credentials)

	
	image = upload_image.upload(glclient, ksclient)

	worker_node_init.activate_image(nvclient, image.id, "Transburst Server Group", Flavor=2)

