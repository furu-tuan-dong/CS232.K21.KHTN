from encoder import encoder
from decoder import decoder
import LZW
from huffman import HuffmanCoding
import pickle
import time
import cv2
import os
import arithmetic_compress
import arithmetic_decompress
import argparse

dict_Alg = {0: "JPEG encoder with Huffman Coding", 1: "JPEG encoder LZW Coding",
            2: "JPEG encoder Arithmetic Coding", 3: "LZW Lossless Coding"}


def info_img(path, flag_alg):
    img = cv2.imread(path)
    try:
        if img is None:
            output_info = "Please choose file image"
            return output_info
    except:
        h, w = img.shape[:2]
        size_img = os.path.getsize(path) / 1000
        output_info = "Algorithm : {} \n".format(dict_Alg[flag_alg])
        output_info += "================================\n"
        output_info += "Info Image:\nPath: {} \nSize: {} KB \nWidthxHeight:{}x{}".format(path, size_img, w, h)
        return output_info


def compress(path, flag_alg):
    dir_folder = path[:path.rfind('.')]
    begin = time.time()
    result = ''
    _encoder = encoder(path)
    imgY, imgCb, imgCr, result = _encoder.encode()
    print(result)
    print(_encoder.getTime() + '[INFO] Entropy Encoder')

    path_output = dir_folder.replace('input', 'compressed_file')

    # Huffman
    if flag_alg == 0:
        print(len(imgY))
        h1 = HuffmanCoding('a.txt')
        h2 = HuffmanCoding('a.txt')
        h3 = HuffmanCoding('a.txt')
        imgY = h1.compress(imgY, 0)
        imgCb = h2.compress(imgCb, 1)
        imgCr = h3.compress(imgCr, 2)

        print(type(imgY))
        path_output += '_huffman'

        with open(path_output + ".pkl", "wb") as fp:
            pickle.dump([h1, h2, h3, imgY, imgCb, imgCr], fp)

    # LZW
    elif flag_alg == 1:
        imgY = LZW.compress1(imgY)
        imgCb = LZW.compress1(imgCb)
        imgCr = LZW.compress1(imgCr)

        path_output += '_lzw'
        print(len(imgY) + len(imgCb) + len(imgCr))

        with open(path_output + ".pkl", "wb") as fp:
            pickle.dump([imgY, imgCb, imgCr], fp)

    # Arithmetic
    elif flag_alg == 2:
        imgY = arithmetic_compress.arith_compress(imgY)
        imgCb = arithmetic_compress.arith_compress(imgCb)
        imgCr = arithmetic_compress.arith_compress(imgCr)

        path_output += '_arithmetic'
        with open(path_output + ".pkl", "wb") as fp:  # Pickling
            pickle.dump([imgY, imgCb, imgCr], fp)

    new_path = path_output + '.pkl'
    print('Ratio: {}'.format(score(path, new_path)))

    print(_encoder.getTime() + 'Done\n')

    print('Time Total: {} s '.format(time.time() - begin))
    print('PATH RESULT: {}'.format(dir_folder + '.pkl'))
    return result


def score(org_path, com_path):
    org = os.stat(org_path).st_size
    new = os.stat(com_path).st_size
    return round(org/new, 2)


def decompress(path, flag_alg):
    begin = time.time()
    dir_folder = path[:path.rfind('.')]
    path_restored = dir_folder.replace('compressed_file', 'restored_images')

    result = ''
    _decoder = decoder()
    print(_decoder.getTime() + '[INFO] Entropy Decoder')

    # Huffman
    if flag_alg == 0:
        DIR = os.path.dirname(os.path.realpath(__file__)) + '/TMP/'
        print("DIR: {}".format(DIR))
        with open(path, "rb") as fp:
            [h1, h2, h3, imgY, imgCb, imgCr] = pickle.load(fp)

            with open(DIR + "huffman{}.bin".format(0), 'wb') as output:
                output.write(bytes(imgY))
            with open(DIR + "huffman{}.bin".format(1), 'wb') as output:
                output.write(bytes(imgCb))
            with open(DIR + "huffman{}.bin".format(2), 'wb') as output:
                output.write(bytes(imgCr))

        imgY = h1.decompress(0)
        imgCb = h2.decompress(1)
        imgCr = h3.decompress(2)

    # LZW
    elif flag_alg == 1:
        with open(path, "rb") as fp:
            [imgY, imgCb, imgCr] = pickle.load(fp)

        # decode
        imgY = LZW.decompress1(imgY)
        imgCb = LZW.decompress1(imgCb)
        imgCr = LZW.decompress1(imgCr)

    # Arithmetic
    elif flag_alg == 2:
        print("Arithmetic Decode")
        with open(path, "rb") as fp:  # Pickling
            [imgY, imgCb, imgCr] = pickle.load(fp)
        # decode
        imgY = arithmetic_decompress.arith_decompress(imgY)
        imgCb = arithmetic_decompress.arith_decompress(imgCb)
        imgCr = arithmetic_decompress.arith_decompress(imgCr)

    print(_decoder.getTime() + 'Done\n')

    # decode
    img, dims, tail_f, result = _decoder.decode(imgY, imgCb, imgCr)
    print(result)
    sup_width, sup_height = dims
    cv2.imwrite(path_restored + '_restored.{}'.format(tail_f),
                img[0:img.shape[0] - sup_height, 0:img.shape[1] - sup_width])

    print('Time Total: {} s'.format(time.time() - begin))
    print('PATH IMG: {}'.format(path_restored + '_restored.{}'.format(tail_f)))

    return path_restored + '_restored.{}'.format(tail_f), result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='Path image', required=True)
    parser.add_argument('-f', '--flag', type=int, help='Choose: 0 :Compress | 1 :Decompress', default=0)
    parser.add_argument('-m', '--method', type=int,
                        help='Choose method: 0 :JPEG encoder with Huffman Coding | 1 :JPEG encoder LZW Coding | 2 :JPEG encoder Arithmetic Coding | 3 :LZW Lossless Coding\n',
                        default=0)
    args = parser.parse_args()
    if args.flag == 0:
        compress(args.input, args.method)
    else:
        decompress(args.input, args.method)
