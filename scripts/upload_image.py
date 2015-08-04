import keystoneclient.v2_0.client as ksclient
import glanceclient.v2.client as glclient


def upload(glance_client, keystone_client):
    glance_endpoint = keystone_client.service_catalog.url_for(
        service_type='image')
    image = glance.images.create(name="raw_convert", disk_format='raw',
                                 container_format='bare')

    print 'Beginning upload of image'
    glance.images.upload(image.id, open('/home/joe/convert.raw', 'rb'))
    print 'Finished uploading of image'
    return image


if __name__ == "__main__":
    OS_AUTH_URL = 'https://us-internal-1.cloud.cisco.com:5000/v2.0'
    OS_TENANT_ID = '0bcdc2b0a4274578a95b780f954b69cf'
    OS_TENANT_NAME = 'BXBInternBox'
    OS_USERNAME = 'josephor'
    OS_REGION_NAME = 'us-internal-1'

    keystone = ksclient.Client(auth_url=OS_AUTH_URL,
                               username=OS_USERNAME,
                               password=OS_PASSWORD,
                               tenant_name=OS_TENANT_NAME,
                               region_name=OS_REGION_NAME)

    glance_endpoint = keystone.service_catalog.url_for(service_type='image')
    glance = glclient.Client(endpoint=glance_endpoint,
                             token=keystone.auth_token)

    image = glance.images.create(name="raw_convert", disk_format='raw',
                                 container_format='bare')

    print 'Beginning upload of image'
    glance.images.upload(image.id, open('/home/joe/convert.raw', 'rb'))
    print 'Finished uploading of image'
