import time 
import aiohttp 
import logging
import hashlib 
from typing import Optional
import asyncio


logger = logging.getLogger(__name__)


class AlphaESSAPI:
    def __init__(self) -> None:
        self.BASEURL = "https://openapi.alphaess.com/api" # change to actual api address
        self.APPID = "alphaXXXXXXXXXXXX" # change to your personal app id on the developer page
        self.APPSECRET = "7d71d896XXXXXXXXXXXXXXXXXXXXXXXX" # change to your peronal app secret on the developer page
        self.sys_sn_list = None   # a list of SNs registered to the APPID, initialized with get_ess_list


    # private funciton, generate signature based on timestamp
    def __get_signature(self, timestamp) -> str:
        return str(hashlib.sha512((self.APPID + self.APPSECRET + timestamp).encode("ascii")).hexdigest())
    

    # private function, send a get request
    async def __get_request(self, path, params) -> Optional[dict]:
        timestamp = str(int(time.time()))
        url = f"{self.BASEURL}/{path}"
        sign = self.__get_signature(timestamp)
        headers = {"appId": self.APPID, "timeStamp": timestamp, "sign": sign}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                data = await resp.json()
                if resp.status == 200:
                    return data
                else:
                    logger.error(f"Get request error: {resp.status} {data}")


    # private function, send a post request
    async def __post_request(self, path, params) -> Optional[dict]:
        timestamp = str(int(time.time()))
        url = f"{self.BASEURL}/{path}"
        sign = self.__get_signature(timestamp)
        headers = {"appId": self.APPID, "timeStamp": timestamp, "sign": sign}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=params) as resp:
                data = await resp.json()
                if resp.status == 200:
                    return data
                else:
                    logger.error(f"Post request error {resp.status} {data}")


    # get the list of ESS registered to the APPID and the relevant info
    # cobat, emsStatus, mbat, minv, poinv, popv, surplusCobat, sysSn, usCapacity
    async def get_ess_list(self) -> Optional[list]:
        path = "getEssList"
        params = {}
        r = await self.__get_request(path, params)
        # get ssn_list using r.data
        if r is not None:
            if r['code'] == 200:
                if type(r['data']) == list:
                    self.sys_sn_list = [item['sysSn'] for item in r['data']]
                    return r['data']
                else:
                    self.sys_sn_list = r['data']['sysSn']
                    return [r['data']]
            else:
                logger.error(f"Get ess list error: {r['code']} {r['msg']}")
        
    # get the latest power data for the specific ESS
    # returns a dict of pbat, pev, pgrid, pload, ppv, soc
    async def get_last_power_data(self, sn) -> Optional[dict]:
        path = "getLastPowerData"
        params = {"sysSn": sn}
        r = await self.__get_request(path, params)
        if r is not None:
            if r['code'] == 200:
                return r['data']
            else:
                logger.error(f"Get last power data error: {r['code']} {r['msg']}")
            

    # get one day of energy eata for the specific ESS
    # return a list of dicts of energy data (probably, untested)
    async def get_one_date_energy_by_sn(self, sn, date):
        path = "getOneDateEnergyBySn"
        params = {"sysSn": sn, "queryDate": date}
        r = await self.__get_request(path, params)
        if r is not None:
            if r['code'] == 200:
                return r['data']
            else:
                logger.error(f"Get one date energy by SN error: {r['code']} {r['msg']}")
        

    # get one day of power data for the specific ESS
    # return a list of dicts of power data (probably, untested)
    async def get_one_date_power_by_sn(self, sn, date):
        path = "getOneDayPowerBySn"
        params = {"sysSn": sn, "queryDate": date}
        r = await self.__get_request(path, params)
        if r is not None:
            if r['code'] == 200:
                return r['data']
            else:
                logger.error(f"Get one date power by SN error: {r['code']} {r['msg']}")
    

    # get the current charging settings for the specific ESS
    # returns a list of batHighCap, gridCharge, timeChae1, timeChae2, timeChaf1, timeChaf2, the relevant settings
    async def get_in_charge_config_info(self, sn) -> Optional[dict]:
        path = "getInChargeConfigInfo"
        params = {"sysSn": sn}
        r = await self.__get_request(path, params)
        if r is not None:
            if r['code'] == 200:
                return r['data']
            else:
                logger.error(f"Get in charge config info error: {r['code']} {r['msg']}")


    # get the current discharging settings for the specific ESS
    # return a list of batUseCap, ctrDis, timeDise1, timeDise2, timeDisf1, timeDisf2, the settings
    async def get_out_charge_config_info(self, sn) -> Optional[dict]:
        path = "getOutChargeConfigInfo"
        params = {"sysSn": sn}
        r = await self.__get_request(path, params)
        if r is not None:
            if r['code'] == 200:
                return r['data']
            else:
                logger.error(f"Get out charge config info error: {r['code']} {r['msg']}")


    # update the charging settings for the specific ESS
    async def update_in_charge_config_info(self, sn, bat_high_cap, grid_charge, time_chae1, time_chae2, time_chaf1, time_chaf2) -> Optional[int]:
        path = "updateInChargeConfigInfo"
        params = {"sysSn": sn, "batHighCap": bat_high_cap, "gridCharge": grid_charge, "timeChae1": time_chae1, 
                  "timeChae2": time_chae2, "timeChaf1": time_chaf1, "timeChaf2": time_chaf2}
        r = await self.__post_request(path, params)
        if r is not None:
            if r['code'] != 200 and r['code'] != 201:
                logger.error(f"Bind SN error: {r['code']} {r['msg']}")
            else:
                print('Updating charge config success')
            return r['code']


    # update the discharging settings for the specific ESS
    async def update_out_charge_config_info(self, sn, bat_use_cap, ctr_dis, time_dise1, time_dise2, time_disf1, time_disf2) -> Optional[int]:
        path = "updateOutChargeConfigInfo"
        params = {"sysSn": sn, "batUseCap": bat_use_cap, "ctrDis": ctr_dis, "timeDise1": time_dise1, 
                  "timeDise2": time_dise2, "timeDisf1": time_disf1, "timeDisf2": time_disf2}
        r = await self.__post_request(path, params)
        if r is not None:
            if r['code'] != 200 and r['code'] != 201:
                logger.error(f"Bind SN error: {r['code']} {r['msg']}")
            else:
                print('Updating discharge config success')
            return r['code']


async def example_code() -> None:
    alpha = AlphaESSAPI()

    # adminitrative related
    bound_systems_info = await alpha.get_ess_list()
    print(bound_systems_info)
    #sys_sn = 'ALB011020015002'  # as an example, can acquire from bound_system_info

    
    # data related
    #last_power_data = await alpha.get_last_power_data(sys_sn)
    #one_date_power = await alpha.get_one_date_power_by_sn(sys_sn, "2023-01-01")
    #one_date_energy = await alpha.get_one_date_energy_by_sn(sys_sn, "2023-01-01")
    #in_charge_config = await alpha.get_in_charge_config_info(sys_sn)
    #out_charge_config = await alpha.get_out_charge_config_info(sys_sn)
    #print(await alpha.update_in_charge_config_info(sys_sn, 100, 1, "00:00", "00:00", "00:00", "00:00"))
    #print(await alpha.update_out_charge_config_info(sys_sn, 100, 1, "00:00", "00:00", "00:00", "00:00"))


if __name__ == "__main__":
    asyncio.run(example_code())



    
