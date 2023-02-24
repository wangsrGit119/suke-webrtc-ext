from fastapi import FastAPI,Body,UploadFile
from fastapi.responses import JSONResponse,StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from rtcAb import *

import os
ROOT = os.path.dirname(__file__)
MediaDir = os.path.join(ROOT, "./media/")


def getDirFiles():
	return os.listdir(MediaDir)
	


# 参数验证Model
from pydantic import BaseModel
from typing import Union
app = FastAPI(docs_url="/documentation", redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True, #如果为True则allow_origins不能为*
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['*']
)

app.mount("/front", StaticFiles(directory="dist",html=True), name="static")
def getResData(code,data,msg):
	return {'code':code,'data':data,'msg':msg}
def getResErrData(msg):
	return {'code':400,'data':None,'msg':msg}
def getResSuccessData(data):
	return {'code':200,'data':data,'msg':'success'}


class OfferSdpModel(BaseModel):
	sdp:str
	stype: Union[str, None] = None
	fileName: Union[str, None] = None



@app.post("/playVideosSdp")
async def playVideosSdp(offerSdpModel:OfferSdpModel):
	res = await receiveOfferSdpPlayVideo(offerSdpModel.sdp,offerSdpModel.fileName)
	return getResSuccessData(res)

@app.post("/playCameraSdp")
async def playCameraSdp(offerSdpModel:OfferSdpModel):
	res = await receiveOfferSdpCamera(offerSdpModel.sdp)
	return getResSuccessData(res)


@app.get("/getAllFiles")
async def getAllFiles():
	return getResSuccessData(getDirFiles())


if __name__ == '__main__':

	print(getDirFiles())
	uvicorn.run(app='main:app',host='0.0.0.0',port=18090,reload=True)
	pass
	


