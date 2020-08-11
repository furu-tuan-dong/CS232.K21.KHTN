import cv2
import numpy as np
import copy
import datetime


class encoder():
  def __init__(self, path):
    self.img = cv2.imread(path)
    self.path = path
    self.originImage = copy.deepcopy(self.img)
    self.height, self.width = self.img.shape[0], self.img.shape[1]
    self.supHeight = (16 - self.height % 16) if (self.height % 16 != 0) else 0
    self.supWidth = (16 - self.width % 16) if (self.width % 16 != 0) else 0
    self.height += self.supHeight
    self.width += self.supWidth

    if self.supHeight != 0 or self.supWidth != 0:
      self.img = np.pad(self.img, [(0, self.supHeight), (0, self.supWidth), (0, 0)], mode='constant')

  def subsampling(self):
    imgY, imgCb, imgCr = [], [], []
    for i in range(self.img.shape[0]):
      for j in range(self.img.shape[1]):
        imgY.append(self.img[i, j, 0])
        if i % 2 == 0 and j % 2 == 0:
          imgCb.append(self.img[i, j, 1])
        elif j % 2 == 0:
          imgCr.append(self.img[i, j, 2])
    imgY = np.array(imgY).reshape([self.img.shape[0], self.img.shape[1]])
    imgCb = np.array(imgCb).reshape([self.img.shape[0] // 2, self.img.shape[1] // 2])
    imgCr = np.array(imgCr).reshape([self.img.shape[0] // 2, self.img.shape[1] // 2])

    return imgY, imgCb, imgCr

  def DCT(self, imgY, imgCb, imgCr):
    dctKernel = np.zeros([8, 8])
    dctKernel[0, :] = 1 / np.sqrt(8)
    for i in range(1, 8):
      for j in range(8):
        dctKernel[i, j] = np.cos(np.pi * i * (2 * j + 1) / 16) * np.sqrt(2 / 8)
    
    def Convert(img):
      newImg = np.zeros(img.shape)
      for i in range(0, img.shape[0], 8):
        for j in range(0, img.shape[1], 8):
          temp = img[i:i+8, j:j+8]
          t1 = np.dot(dctKernel, temp)
          newImg[i:i+8, j:j+8] = np.dot(t1, np.transpose(dctKernel))
      return newImg
    
    imgY = Convert(imgY)
    imgCb = Convert(imgCb)
    imgCr = Convert(imgCr)

    return imgY, imgCb, imgCr
  
  def quantization(self, img, q):
    newImg = np.zeros(img.shape, dtype=int)
    for i in range(0, img.shape[0], 8):
      for j in range(0, img.shape[1], 8):
        temp = img[i:i+8, j:j+8]
        newImg[i:i+8, j:j+8] = np.round(temp / q)
    return newImg

  def RLE(self, img):
    img = np.array(img).T
    # dc = []
    rle = []
    tmp = img[0,0]
    rle.append((0,tmp))
    #DMCP
    for i in img[0][1:]:
      rle.append((0,i - tmp))
      tmp = i 
    #RLE
    (h,w) = img.shape
    key =img[1,0]
    fre =0
    for j in range(w):
      for i in range(1,h):
          if key == img[i,j]:
            fre =fre+1
          else:
            rle.append((fre,key))
            key = img[i,j]
            fre =1
    rle.append((fre,key))
    return rle
  
  def scan(self, img, z):
    imgSeq = []
    for i in range(0, img.shape[0], 8):
      for j in range(0, img.shape[1], 8):
        temp = img[i:i+8, j:j+8]
        temp = temp.reshape([1, -1])
        new_zone = []
        for k in range(temp.shape[1]):
          new_zone.append(temp[0][z[k]])
        imgSeq.append(new_zone)

    return imgSeq

  def tupleToString(self, tu):
    # print(tu[0])
    # print(b''.join(('a','b')))
    return ' '.join([' '.join(map(str, t)) for t in tu])

  def getTime(self):
    now = datetime.datetime.now()
    return "[{}:{}:{}] - ".format(now.hour, now.minute, now.second)

  def encode(self):
    qy = [16,11,10,16,24,40,51,61,
        12,12,14,19,26,58,60,55,
        14,13,16,24,40,57,69,56,
        14,17,22,29,51,87,80,62,
        18,22,37,56,68,109,103,77,
        24,35,55,64,81,104,113,92,
        49,64,78,87,103,121,120,101,
        72,92,95,98,112,100,103,99]

    qy = np.array(qy)
    qy = qy.reshape([8, 8])

    qc = [17,18,24,47,99,99,99,99,
        18,21,26,66,99,99,99,99,
        24,26,56,99,99,99,99,99,
        47,66,99,99,99,99,99,99,
        99,99,99,99,99,99,99,99,
        99,99,99,99,99,99,99,99,
        99,99,99,99,99,99,99,99,
        99,99,99,99,99,99,99,99]

    qc = np.array(qc)
    qc = qc.reshape([8, 8])

    z = [0,1,5,6,14,15,27,28,
        2,4,7,13,16,26,29,42,
        3,8,12,17,25,30,41,43,
        9,11,18,24,31,40,44,53,
        10,19,23,32,39,45,52,54,
        20,22,33,38,46,51,55,60,
        21,34,37,47,50,56,59,61,
        35,36,48,49,57,58,62,63]

    result = ''
    result += self.getTime() + '[INFO] ycbcr convert\n'

    # ycbcr convert
    self.img = cv2.cvtColor(self.img,cv2.COLOR_BGR2YUV)

    result += self.getTime() + 'Done\n' + self.getTime() + '[INFO] Subsampling\n'
    # subsampling
    imgY, imgCb, imgCr = self.subsampling()

    # DCT convert
    result += self.getTime() + 'Done\n' + self.getTime() + '[Info] DCT convert\n'
    imgY, imgCb, imgCr = self.DCT(imgY, imgCb, imgCr)

    # Quantization
    result += self.getTime() + 'Done\n' + self.getTime() + '[INFO] Quantization\n'
    imgY = self.quantization(imgY, qy)
    imgCb = self.quantization(imgCb, qc)
    imgCr = self.quantization(imgCr, qc)

    # z-scan
    result += self.getTime() + 'Done\n' + self.getTime() + '[INFO] z-scan\n'
    imgY = self.scan(imgY, z)
    imgCb = self.scan(imgCb, z)
    imgCr = self.scan(imgCr, z)

    # input()
    # encode
    result += self.getTime() + 'Done\n' + self.getTime() + '[INFO] RLE\n'

    imgY = self.RLE(imgY)
    imgCb = self.RLE(imgCb)
    imgCr = self.RLE(imgCr)

    # Tuple to string
    result += self.getTime() + 'Done\n' + self.getTime() + '[INFO] Tuple to string\n'
    imgY = '{} {} {} {} {} '.format(self.path[self.path.rfind('.')+1:], self.width, self.height, self.supWidth, self.supHeight) + self.tupleToString(imgY)
    imgCb = self.tupleToString(imgCb)
    imgCr = self.tupleToString(imgCr)

    result += self.getTime() + 'Done\n'
    return imgY, imgCb, imgCr, result


if __name__ == '__main__':
  _encoder = encoder('../assets/demo.png')
  a, b, c, d = _encoder.encode()
  print(a)
