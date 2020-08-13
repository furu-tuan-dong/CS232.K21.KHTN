import cv2
import numpy as np
import datetime

class decoder():
  def __init__(self):
    pass

  def deRLE(self, img):
    numBlocks = 0
    tmp_dc = img[0][1]
    dc = [tmp_dc]
    for i in range(1, len(img)):
      if img[i][0] == 0:
        numBlocks = i+1
        dc.append(dc[i-1]+img[i][1])
      else:
          break

    da = ''

    for i in range(numBlocks-1, len(img)):
      da = da + img[i][0]*(str(img[i][1])+' ')

    da = list(map(int,da.strip().split(' ')))
    col = len(da)//numBlocks
    da = np.array(da).reshape(numBlocks,col)
    result = np.insert(da,0,dc,axis =1)

    return result

  def inverseScan(self, img, z, height, width):
    origin = np.zeros([height, width], dtype=int)
    for i in range(len(img)):
      tmp = np.zeros(len(img[i]))
      for j in range(len(img[i])):
        tmp[z[j]] = img[i][j]

      tmp = tmp.reshape([8, 8])
      row, col = i // (width // 8), i % (width // 8)
      row = row * 8
      col = col * 8
      origin[row:row+8, col:col+8] = tmp
  
    return origin
  
  def inverseDCT(self, img, dct_kernel):
    origin = np.zeros(img.shape)
    for i in range(0, img.shape[0], 8):
      for j in range(0, img.shape[1], 8):
        temp = img[i:i+8, j:j+8]
        t1 = np.dot(np.transpose(dct_kernel), temp)
        origin[i:i+8, j:j+8] = np.dot(t1, dct_kernel)
    return origin

  def inverseQuantization(self, img, q):
    origin = np.zeros(img.shape)
    for i in range(0, img.shape[0], 8):
      for j in range(0, img.shape[1], 8):
        temp = img[i:i+8, j:j+8]
        origin[i:i+8, j:j+8] = temp * q
    return origin

  def inverseSubsampling(self, img_cb, img_cr, height, width):
    originCb, originCr = np.zeros([height, width]), np.zeros([height, width])
    for i in range(img_cb.shape[0]):
      for j in range(img_cb.shape[1]):
        tmp1, tmp2 = img_cb[i][j], img_cr[i][j]
        originCb[i*2:i*2+2, j*2:j*2+2] = np.array([tmp1, tmp1, tmp1, tmp1]).reshape([2, 2])
        originCr[i*2:i*2+2, j*2:j*2+2] = np.array([tmp2, tmp2, tmp2, tmp2]).reshape([2, 2])
    return originCb, originCr
  
  def convertRGB(self, img, origin_cb, origin_cr, img_y):
    img[:,:,0] = img_y
    img[:,:,1] = origin_cb
    img[:,:,2] = origin_cr
    img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR)
    return img

  def stringToTuple(self, string, flag =0):
    img = string.strip().split(' ')
    print(img[:5])
    tail = ''
    if flag == 1:
      tail = img[0]
      img = img[1:]
      
    img = list(map(int, img))
    dims = []
    if flag == 1:
      dims = img[:4]
      img = img[4:]
    tmp = len(img)-1
    return [tuple([img[i],img[i+1]]) for i in range(0,tmp,2)],[dims,tail]

  def getTime(self):
    now = datetime.datetime.now()
    return "[{}:{}:{}] - ".format(now.hour,now.minute, now.second)

  def decode(self, imgY, imgCb, imgCr):
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
    dctKernel = np.zeros([8, 8])
    dctKernel[0, :] = 1 / np.sqrt(8)
    for i in range(1, 8):
      for j in range(8):
        dctKernel[i, j] = np.cos(np.pi * i * (2 * j + 1) / 16) * np.sqrt(2 / 8)

    # string to tuple
    result = ''
    result += self.getTime() + '[Info] De String to tuple:\n'
    imgY, dims = self.stringToTuple(imgY, 1)
    width, height = dims[0][0:2]
    imgCb, _ = self.stringToTuple(imgCb)
    imgCr, _ = self.stringToTuple(imgCr)
    result += self.getTime() + 'Done\n' + self.getTime() + '[Info] DeRLE\n'

    imgY = self.deRLE(imgY)
    imgCb = self.deRLE(imgCb)
    imgCr = self.deRLE(imgCr)

    result += self.getTime() + 'Done\n' + self.getTime() + '[Info] Inverse-z-scan\n'

    # inverse-z-scan
    imgY = self.inverseScan(imgY, z, height, width)
    imgCb = self.inverseScan(imgCb, z, height // 2, width // 2)
    imgCr = self.inverseScan(imgCr, z, height // 2, width // 2)
    result+= self.getTime() + 'Done\n' + self.getTime() + '[Info] Inverse-quantization\n'

    # inverse-quantization
    imgY = self.inverseQuantization(imgY, qy)
    imgCb = self.inverseQuantization(imgCb, qc)
    imgCr = self.inverseQuantization(imgCr, qc)
    result += self.getTime() + 'Done\n' + self.getTime() + '[Info] Invert DCT\n'

    # inverse DCT
    imgY = self.inverseDCT(imgY, dctKernel)
    imgCb = self.inverseDCT(imgCb, dctKernel)
    imgCr = self.inverseDCT(imgCr, dctKernel)

    # inverse subsampling
    result += self.getTime() + 'Done\n' + self.getTime() + '[INFO] Inverse_subsampling\n'
    origin_cb, origin_cr = self.inverseSubsampling(imgCb, imgCr, height, width)
    result += self.getTime() + 'Done\n' + self.getTime() + '[INFO] rgb convert\n'
    img = np.zeros([height, width, 3], dtype=np.uint8)
    img = self.convertRGB(img, origin_cb, origin_cr, imgY)
    result += self.getTime() + 'Done\n'
    return img, dims[0][2:], dims[1], result


if __name__== '__main__':
  _decoder = decoder()
