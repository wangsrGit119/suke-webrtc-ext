
from aiortc import RTCPeerConnection,RTCIceCandidate, RTCSessionDescription,MediaStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender
from aiortc.contrib.signaling import BYE, add_signaling_arguments, create_signaling
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender
import os,uuid,time
ROOT = os.path.dirname(__file__)
pcs = set()
import logging
import cv2
from av import VideoFrame

logging.basicConfig(level=logging.INFO)

relay = MediaRelay()


class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from another track.
    """

    kind = "video"

    def __init__(self, track, transform, fps=10):
        super().__init__()  # don't forget this!
        self.track = track
        self.transform = transform
        self.fps = fps

    async def recv(self):
        frame = await self.track.recv()

        if self.transform == "cartoon":
            img = frame.to_ndarray(format="bgr24")

            # prepare color
            img_color = cv2.pyrDown(cv2.pyrDown(img))
            for _ in range(6):
                img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
            img_color = cv2.pyrUp(cv2.pyrUp(img_color))

            # prepare edges
            img_edges = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img_edges = cv2.adaptiveThreshold(
                cv2.medianBlur(img_edges, 7),
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                9,
                2,
            )
            img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)

            # Resize the images to have the same dimensions
            img_color_resized = cv2.resize(img_color, (img_edges.shape[1], img_edges.shape[0]))
            # combine color and edges
            img = cv2.bitwise_and(img_color_resized, img_edges)

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            # new_frame.time_base += 1.0 / self.fps  # Update time_base based on custom fps
            return new_frame
        elif self.transform == "edges":
            # perform edge detection
            img = frame.to_ndarray(format="bgr24")
            img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            # new_frame.time_base += 1.0 / self.fps  # Update time_base based on custom fps
            return new_frame
        # 视频旋转
        elif self.transform == "rotate":
            # rotate image
            img = frame.to_ndarray(format="bgr24")
            rows, cols, _ = img.shape
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), frame.time * 45, 1)
            img = cv2.warpAffine(img, M, (cols, rows))
            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            # new_frame.time_base += 1.0 / self.fps  # Update time_base based on custom fps
            return new_frame
        else:
            return frame


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
		if c_state == "connected":
			senders = pc.getSenders()
			# for sender in senders:
			# 	if sender.kind == "video":
			# 		print("send params =>",await sender.getStats())



	# open media source
	player = MediaPlayer(os.path.join(ROOT, "./media/"+fileName))
	audio_sender = pc.addTrack(player.audio)
	# video_sender = pc.addTrack(player.video)
	video_sender = pc.addTrack(VideoTransformTrack(relay.subscribe(player.video),transform="cartoon"))
	 
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



