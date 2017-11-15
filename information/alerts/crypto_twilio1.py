from twilio.rest import Client

# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = "AC822d03400a3abeb205e2ec520eb3dbd7"
auth_token = "753814d986ef6b3fa83302afd83dc324"
client = Client(account_sid, auth_token)

message = client.messages.create(
    "+12026316400",
    body="Jenny please?! I love you <3",
    from_="+12028888138")

def alert_duncan(message):
    m = client.messages.create(
        "+12026316400",
        body=message,
        from_="+12028888138")

    print(m)
