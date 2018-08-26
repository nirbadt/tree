from pyfcm import FCMNotification
from pprint import pprint

web_api_key = 'AIzaSyDtV32OGzrhsnGY_yOvPZCyIg_dAFd1iwI'
server_key = 'AAAAI8IgfpU:APA91bEQjQ1UJrwS-eaB8cc24Jay43bZARBdrKy64VXg1-2bL21IMevU7p5tbanmZgCAILPHWG29-7z76FkxqRUytASYO0XotSMHWGLNWV1q5h74EUYHvBESMSnoXABtR677T48idT1N'
web_push_key="BBWy9JSODbwL_AJhgNQ3PpnChJbYZ6kKW9oqSclSH1tXacoZaRnlRrvErMRJnuZQhOd0C-F8uLeSmFDh7xh8I3I"


push_service = FCMNotification(api_key="<server key>")
registration_id="<device registration_id>"
message = "Hope you're having fun this weekend, don't forget to check today's news"
result = push_service.notify_single_device(registration_id=registration_id)
pprint(result)
result = push_service.notify_multiple_devices(registration_ids=[registration_id,registration_id,registration_id])
pprint(result)
result = push_service.notify_topic_subscribers(topic_name="global", message_body=message)
pprint(result)


from pyfcm import FCMNotification
 
push_service = FCMNotification(api_key="<api-key>")
 
# OR initialize with proxies
 
proxy_dict = {
          "http"  : "http://127.0.0.1",
          "https" : "http://127.0.0.1",
        }
push_service = FCMNotification(api_key="<api-key>", proxy_dict=proxy_dict)
 
# Your api-key can be gotten from:  https://console.firebase.google.com/project/<project-name>/settings/cloudmessaging
# https://console.firebase.google.com/project/tree-89cdf/settings/cloudmessaging


registration_id = "<device registration_id>"
message_title = "Uber update"
message_body = "Hi john, your customized news for today is ready"
result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
 
print result
 
# Send to multiple devices by passing a list of ids.
registration_ids = ["<device registration_id 1>", "<device registration_id 2>", ...]
message_title = "Uber update"
message_body = "Hope you're having fun this weekend, don't forget to check today's news"
result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body)
 
print result
