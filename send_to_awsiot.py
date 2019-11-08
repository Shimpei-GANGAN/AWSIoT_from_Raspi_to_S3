# standard
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import click
import base64

# local
import settings


MQTTClient = None
"""
    AWS IoT に接続するための各種初期化を行う
"""
def init_awsiot_client():
    device_id = settings.MQTT_DEVICE_ID
    endpoint = settings.AWS_IOT_ENDPOINT

    my_mqtt_client = AWSIoTMQTTClient(device_id)
    my_mqtt_client.configureEndpoint(endpoint, 8883)
    my_mqtt_client.configureCredentials(
        settings.AWS_CERTS_PATH_ROOTCA,
        settings.AWS_CERTS_PATH_PRIVATEKEY,
        settings.AWS_CERTS_PATH_CERTIFICATE
    )
    my_mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
    my_mqtt_client.configureOfflinePublishQueueing(-1)
    my_mqtt_client.configureDrainingFrequency(2)
    my_mqtt_client.configureConnectDisconnectTimeout(10)
    my_mqtt_client.configureMQTTOperationTimeout(5)
    return my_mqtt_client

"""
    画像を取得し、AWS S3へ画像を転送する
"""
def get_image_and_send_to_aws(my_mqtt_client, path):
    #click.echo("path={}".format(path))

    binary = open(path, "rb").read()
    binary_base64 = base64.b64encode(binary)
    payload = bytearray(binary_base64)
    print(type(payload))

    # AWS IoT に Publish
    result = my_mqtt_client.publish(
        settings.MQTT_TOPIC,
        payload,
        settings.MQTT_QOS
    )
    if result:
        print('Publish result: OK')
    else:
        print('Publish result: NG')


@click.command()
@click.option("--path",
    type=click.Path(exists=True), default="test.jpg")
def main(path):
    my_mqtt_client = init_awsiot_client()
    my_mqtt_client.connect()
    print('MQTT connect.')
    print("-----------------------------------")
    get_image_and_send_to_aws(my_mqtt_client, path=path)
#    time.sleep(settings.SEND_DATA_INTERVAL_SEC)
    print("-----------------------------------")
    """
    while True:
        get_image_and_send_to_aws(my_mqtt_client)
        time.sleep(settings.SEND_DATA_INTERVAL_SEC)
    """
if __name__ == '__main__':
    main()
