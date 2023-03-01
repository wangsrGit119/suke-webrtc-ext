
from aiortc import RTCPeerConnection,RTCIceCandidate, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender
from aiortc.contrib.signaling import BYE, add_signaling_arguments, create_signaling
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender
import os,uuid,time
ROOT = os.path.dirname(__file__)
pcs = set()
import logging
logging.basicConfig(level=logging.INFO)
async def on_ice_candidate(candidate:RTCIceCandidate):

	logging.info(f"ICE candidate:======================\n{candidate.to_sdp()}")

async def receiveOfferSdpPlayVideo(sdp,fileName):
	offer = RTCSessionDescription(sdp=sdp, type='offer')
	pc = RTCPeerConnection()

	# sendonly/recvonly/sendrecv
	pc.addTransceiver("audio", direction='sendonly')
	pc.addTransceiver("video", direction='sendonly')
	pcs.add(pc)

	channel = pc.createDataChannel("server-chat")
	logging.info("服务端消息通道开始创建 %s",channel.label)

	@channel.on("open")
	def on_open():
		logging.info("服务端消息通道创建成功 %s",channel.label)
		channel.send("server-chat-info")


	@channel.on("close")
	def on_open():
		logging.info("服务端消息通道关闭 %s",channel.label)

	@channel.on("message")
	def on_message(message):
		logging.info("来自于远端消息 %s",message)




	pc.onicecandidate = on_ice_candidate
	@pc.on("icegatheringstatechange")
	async def on_icegatheringstatechange():
		print(f"ICE gathering state =========== {pc.iceGatheringState}")

	@pc.on("iceconnectionstatechange")
	async def on_iceconnectionstatechange():
		print(f"ICE connection state ========= {pc.iceConnectionState}")


	@pc.on("connectionstatechange")
	async def on_connectionstatechange():
		c_state = pc.connectionState
		print("Connection state is =========", c_state)
		if c_state == "failed":
			await pc.close()
			pcs.discard(pc)
		if c_state == "closed":
			pcs.discard(pc)


	# open media source
	player = MediaPlayer(os.path.join(ROOT, "./media/"+fileName))
	audio_sender = pc.addTrack(player.audio)
	video_sender = pc.addTrack(player.video)
	# remote desc
	await pc.setRemoteDescription(offer)
	answer = await pc.createAnswer()
	await pc.setLocalDescription(answer)
	return {"sdp": answer.sdp, "type": answer.type}

def getVideoMeta():
	return {'node'}

async def receiveOfferSdpCamera(sdp):
	offer = RTCSessionDescription(sdp=sdp, type='offer')
	pc = RTCPeerConnection()

	# sendonly/recvonly/sendrecv
	pc.addTransceiver("audio", direction='sendrecv')
	pc.addTransceiver("video", direction='sendrecv')
	pcs.add(pc)



	pc.onicecandidate = on_ice_candidate
	@pc.on("icegatheringstatechange")
	async def on_icegatheringstatechange():
		print(f"ICE gathering state =========== {pc.iceGatheringState}")

	@pc.on("iceconnectionstatechange")
	async def on_iceconnectionstatechange():
		print(f"ICE connection state ========= {pc.iceConnectionState}")


	@pc.on("connectionstatechange")
	async def on_connectionstatechange():
		print("Connection state is =========", pc.connectionState)
		if pc.connectionState == "failed":
			await pc.close()
			pcs.discard(pc)

	@pc.on("datachannel")
	def on_datachannel(channel):
		print("data channel info  =========", channel)
		@channel.on("message")
		def on_message(message):
			print("远程客户端消息 =========",message)
			channel.send(str({"data":"随机响应"+str(uuid.uuid1())+message,"type":"random"}))

	@pc.on("track")
	def on_track(track):
		print("received track: =========", track)
		pc.addTrack(track)

	# remote desc
	await pc.setRemoteDescription(offer)
	answer = await pc.createAnswer()
	await pc.setLocalDescription(answer)
	return {"sdp": answer.sdp, "type": answer.type}



