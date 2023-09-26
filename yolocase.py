from ultralytics import YOLO
import supervision as sv
from PIL import Image



confidence_threshold = 0.3
iou_threshold = 0.7
model = YOLO('yolov8n.pt')
def image_predict(npframe):
	results = model.predict(
		source=npframe,
		verbose=True,## 打印额外信息
		show_labels=True,#在图中显示对象标签
		show_conf=True,#在图中显示对象置信度分数
		# classes=[0,2,3] ,#按照类别过滤	
		stream=False,##输入数据将以流的形式连续地传递给模型进行预测。这通常用于处理视频流，其中模型会在连续的帧上进行实时预测。并返回预测结果。 当此参数为True 则 show参数不生效
		# show=True,## 实时显示检测过程
		conf=confidence_threshold,##这个参数表示置信度阈值（confidence threshold）用于对象检测。它确定被检测到的对象被视为有效的最低置信度分数。置信度得分低于此阈值的对象将被过滤掉
		 iou=iou_threshold,##这个参数代表交并比（Intersection over Union，IoU）阈值。它确定预测的边界框和实际边界框之间所需的最小重叠程度，以将它们视为匹配。交并比得分低于此阈值的边界框将被视为不同的对象。iou_threshold的值被用作此参数的值。
		 save=False
		)
	return results


if __name__ == '__main__':

	results = image_predict("./dist/bus.jpg")
	# results[0].save_crop("./dist/",file_name="xx.jpg")
	images = results[0].cpu().numpy()
	print(images.orig_img)
	img = Image.fromarray(images.orig_img)
	img.save(f"output_1.jpg")

	# print(images)
	# for i, image in enumerate(images):
	#     img = Image.fromarray(image)
	#     img.save(f"output_{i}.jpg")

	pass