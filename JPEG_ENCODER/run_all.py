import run
import os
import time

# huff = 0
# lzw = 0
# ari = 0
compressed_files = []


def compress_all():
    huff = 0
    lzw = 0
    ari = 0
    compressed_files = []
    list_img = [f"input/{x}.png" for x in range(1, 101)]

    for i in [0, 1, 2]:
        for img in list_img:
            run.compress(img, i)
            new_path = img[:-4].replace('input', 'compressed_file')
            if i == 0:
                new_path += '_huffman.pkl'
                huff += score(img, new_path)
            elif i == 1:
                new_path += '_lzw.pkl'
                lzw += score(img, new_path)
            else:
                new_path += '_arithmetic.pkl'
                ari += score(img, new_path)
            compressed_files.append(new_path)

    return huff, lzw, ari, compressed_files


def score(org_path, com_path):
    org = os.stat(org_path).st_size
    new = os.stat(com_path).st_size
    return round(org/new, 2)


def decompress_all(compressed_files):
    begin = time.time()
    for file in compressed_files:
        i = 0
        if 'huffman' in file:
            i = 0
        elif 'lzw' in file:
            i = 1
        else:
            i = 2

        run.decompress(file, i)
    end = time.time()
    print(end - begin)


if __name__ == '__main__':
    begin_1 = time.time()
    huff, lzw, ari, compressed_files = compress_all()
    end_1 = time.time()
    time_1 = end_1 - begin_1
    print("Time compressed: {}".format(time_1))

    begin_2 = time.time()
    decompress_all(compressed_files)
    end_2 = time.time()
    time_2 = end_2 - begin_2
    print("Time decompress: {}".format(time_2))

    # print(huff)
    # print(lzw)
    # print(ari)