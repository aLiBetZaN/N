from aiohttp import request
from re import match, compile



iran_number = compile(r"^(\+?98|0?9)\d{9}$")
search = "https://api.divar.ir/v8/web-search/{}?page={}"
user_phone = "https://api.divar.ir/v8/postcontact/web/contact_info/{}"
url_check_city = 'https://api.divar.ir/v8/web-search/{}'

class Divar:
    def __init__(self, phone_number: str) -> None:
        self.phone_number = phone_number

    async def send_code(self):
        if match(iran_number, self.phone_number):
            async with request("POST", "https://api.divar.ir/v5/auth/authenticate", json={"phone": self.phone_number}) as req:
                json = await req.json()
                return json
        return False

    async def login(self, code):
        async with request("POST", "https://api.divar.ir/v5/auth/confirm", json={"phone": self.phone_number, "code": code}) as req:
            json = await req.json()
            try:
                self.token = json["token"]
                return True
            except KeyError:
                return False

    async def get_users_token(self, city: str, page: int):
        users = []
        async with request("GET", search.format(city, page)) as req:
            if req.status == 200:
                json = await req.json()
                widgets = json["web_widgets"]["post_list"]
                for widget in widgets:
                    users.append(widget["data"]["token"])
            else: return False
        return users
    
    async def get_users_phone(self, users: list[str], token=None):
        phones = []
        token = token or self.token
        for user in users:
            async with request("GET", user_phone.format(user), headers={"cookie": f"token={token}"}) as req:
                json = await req.json()
                try:
                    for widget in json["widget_list"]:
                        if widget["widget_type"] == "UNEXPANDABLE_ROW":
                            try:
                                phones.append(widget["data"]["action"]["payload"]["phone_number"])
                            except KeyError: pass
                            continue
                except KeyError:
                    break
        return phones

    async def get_info(self):
        async with request("POST", "https://chat.divar.ir/api/init", data={"device_type":"web","token":self.token,"version":"2.33.0"}) as req:
            print(await req.json())
    
# from asyncio import get_event_loop
# 
# loop = get_event_loop().run_until_complete
# async def main(): 
#     d = Divar("09380044400")
#     await d.send_code()
#     await d.login(input(": "))
#     print(await d.get_users_phone(await d.get_users_token(0)))
# 
# loop(main())