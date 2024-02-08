from requests import get, post
from re import match, compile



iran_number = compile(r"^(\+?98|0?9)\d{9}$")
search = "https://api.divar.ir/v8/web-search/{}?page={}"
user_phone = "https://api.divar.ir/v8/postcontact/web/contact_info/{}"
url_check_city = 'https://api.divar.ir/v8/web-search/{}'

class Divar:
    def __init__(self, phone_number: str) -> None:
        self.phone_number = phone_number

    def send_code(self):
        if match(iran_number, self.phone_number):
            post("https://api.divar.ir/v5/auth/authenticate", json={"phone": self.phone_number})
            return True
        return False

    def login(self, code):
        req = post("https://api.divar.ir/v5/auth/confirm", json={"phone": self.phone_number, "code": code}).json()
        try:
            self.token = req["token"]
            return True
        except KeyError:
            return False

    def get_users_token(self, city: str, page: int):
        users = []
        req = get(search.format(city, page))
        if req.status_code == 200:
            json = req.json()
            widgets = json["web_widgets"]["post_list"]
            for widget in widgets:
                users.append(widget["data"]["token"])
            return users    
        else: return False
    
    def get_users_phone(self, users: list[str], token=None):
        phones = []
        token = token or self.token
        for user in users:
            req = get(user_phone.format(user), headers={"cookie": f"token={token}"}).json()
            try:
                for widget in req["widget_list"]:
                    if widget["widget_type"] == "UNEXPANDABLE_ROW":
                        try:
                            phones.append(widget["data"]["action"]["payload"]["phone_number"])
                        except KeyError: pass
                        continue
            except KeyError:
                break
        return phones

    def get_info(self):
        req = post("https://chat.divar.ir/api/init", data={"device_type":"web","token":self.token,"version":"2.33.0"})
        print(req.json())
    
# from asyncio import get_event_loop
# 
# loop = get_event_loop().run_until_complete
# def main(): 
#     d = Divar("09380044400")
#     await d.send_code()
#     await d.login(input(": "))
#     print(await d.get_users_phone(await d.get_users_token(0)))
# 
# loop(main())