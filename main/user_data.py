# ridiculously incomplete

swift = Connection(user="admin",
                   key="1ightriseR!",
                   authurl="http://10.131.69.112:35357/v2.0",
                   tenant_name="admin",
                   auth_version="2.0")

for clip in local_video_container:
	swift.get_object("clip")